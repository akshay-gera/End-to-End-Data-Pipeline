import requests
import logging
import os
from google.cloud import bigquery
import json
import pandas as pd
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook


# Defining the path where the log file will be stored
log_file_path = os.path.join(os.getcwd(), 'extraction.log')
print(f"Current working directory: {os.getcwd()}")
print(f"Log file will be created at: {log_file_path}")

# Set up logging to output to a file
logging.basicConfig(
    filename=log_file_path,  # Full path to the log file
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Step 1: Creating a function to use requests to make an API call 
def extract_data(url, headers, params):
    try:
        logging.info("Starting data extraction from LinkedIn API...")
        response = requests.get(url, headers=headers, params=params)

        # To make sure we log messages from API call response which doesn't result into any data and also doesn't go into except code block
        response_data = response.json()
        if response_data['success'] == True:
            logging.info("API Call Successful. No error messages returned")
            jobs_today = pd.json_normalize(response.json()['data'], sep='_')
            # Adding a timestamp column to the dataframe to track when the new data was fetched
            jobs_today['timestamp_fetched'] = pd.Timestamp.now()
            # Converting it to string type to make Xcom through Airflow possible as it will be converted to JSON to move to next step
            jobs_today['timestamp_fetched'] =jobs_today['timestamp_fetched'].astype(str)
            logging.info(f"Today's Data Extracted with {len(jobs_today)} records")
            return jobs_today
            
        else:
            logging.error(f"API Call failed. Response: {response_data}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from API: {e}")
    
    except Exception as e:
        logging.error(f"API Call Returned Error with message {response_data}")

# Step 2: In order to frame incremental logic we need to check existing primary key column values in BigQuery
def get_existing_ids_from_bq(project_id, dataset_id, table_id):
    
    # Using BigQueryHook which will automatically pull connection from Airflow UI
    hook = BigQueryHook(gcp_conn_id='google_cloud')  # Use your connection ID here
        
    # Initialize BigQuery client via the hook
    client = hook.get_client(project_id=project_id)
    query = f"SELECT ID FROM `{table_id}`"
    query_job = client.query(query)
    result = query_job.result() 
    # result is in row iteration output so geting that output by running a for loop
    existing_ids = [row['ID'] for row in result] 
    logging.info(f"Found {len(existing_ids)} exiting records in BigQuery")
    return existing_ids

# Step 3: We compare these existing primary key with today's data fetch id to get new records
def fetch_new_record_id(input_df, existing_ids ):
    if input_df is not None and input_df.empty == False:
        # Creating a for loop result a list of ids from input_df which are not in existing_ids
        list_new_records_id = []
        
        for id in input_df.id:
            if id  not in existing_ids:
                list_new_records_id.append(id)
        
        new_records_df = input_df[input_df.id.isin(list_new_records_id)]
        logging.info(f"Found {len(new_records_df)} new records to be pushed into BigQuery")
        return new_records_df
    else:
        logging.info(f"No todays data to look into to check new records")

# Step 4: Creating a helper function to perform a schema check on our existing columns in the BigQuery table to ensure consistency
def bigquery_schema_check(project_id, dataset_id, table_id):
    # Using BigQueryHook which will automatically pull connection from Airflow UI
    hook = BigQueryHook(gcp_conn_id='google_cloud')  # Use your connection ID here
        
    # Initialize BigQuery client via the hook
    client = hook.get_client(project_id=project_id)

    table_name = table_id.split('.')[-1]
    query = f"SELECT column_name FROM `{dataset_id}.INFORMATION_SCHEMA.COLUMNS` WHERE table_name = '{table_name}';"
    query_job = client.query(query)
    result = query_job.result() 
               
    # result is in row iteration output so geting that output by running a for loop
    existing_columns = [row['column_name'] for row in result] 
    return existing_columns

# Step 5: Load the new data into BigQuery based on the schema check and new records
def load_raw_data(project_id, dataset_id, table_id, todays_df):
    try:

        # Using BigQueryHook which will automatically pull connection from Airflow UI
        hook = BigQueryHook(gcp_conn_id='google_cloud')  # Use your connection ID here
        
        # Initialize BigQuery client via the hook
        client = hook.get_client(project_id=project_id)


        # Configuring Data Loading into BigQuery
        # Data Load Methodology adopted for "WRITE_APPEND"` to append data new data
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  
            source_format=bigquery.SourceFormat.PARQUET,
        )
        # Converting the timestampt column from str to datetime to maintain schema consistency with Raw_Data table in BigQuery 
        todays_df['timestamp_fetched'] = pd.to_datetime(todays_df['timestamp_fetched'])
        # Calling the helper function to check existing schema in BigQuery
        try: 
            existing_schema_columns = bigquery_schema_check(project_id, dataset_id, table_id)
            # Filtering the dataframe columns to match with the schema columns
            todays_df = todays_df[existing_schema_columns]
            logging.info(f"Schema Check Passed. Dataframe columns match with BigQuery Table Schema")
        
        except Exception as e:
            logging.error(f"Failed to fetch schema from BigQuery: {e}")
        
        # Load data into the BigQuery table
        load_job = client.load_table_from_dataframe(todays_df, f"{table_id}", job_config=job_config)

        # Waiting for the job to complete
        load_job.result()
        logging.info(f"Successful Extraction and Load. Loaded {load_job.output_rows} rows into {table_id}")
    
    except Exception as e:
        logging.error(f"Data Load Function Failed with error {e}")


