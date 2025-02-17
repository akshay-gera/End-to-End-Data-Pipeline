import requests
import logging
import os
from google.cloud import bigquery
import json
import pandas as pd

# Define the path where the log file will be stored
log_file_path = os.path.join(os.getcwd(), 'extraction.log')
# Print the directory and full path to help debug where the log file will be created
print(f"Current working directory: {os.getcwd()}")
print(f"Log file will be created at: {log_file_path}")

# Set up logging to output to a file
logging.basicConfig(
    filename=log_file_path,  # Full path to the log file
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def extract_data(url, headers, params):
    try:
        logging.info("Starting data extraction from LinkedIn API...")
        response = requests.get(url, headers=headers, params=querystring)

        # To make sure we log messages from API call response which doesn't result into any data and also doesn't go into except code block
        response_data = response.json()
        if response_data['success'] == True:
            logging.info("API Call Successful. No error messages returned")
            jobs_today = pd.json_normalize(response.json()['data'], sep='_')
            jobs_today['timestamp_fetched'] = pd.Timestamp.now()
            logging.info(f"Today's Data Extracted with {len(jobs_today)} records")
            return jobs_today
            

        else:
            logging.error(f"API Call failed. Response: {response_data}")
            
    
    
    except requests.exceptions.RequestException as e:
        
        logging.error(f"Error fetching data from API: {e}")
    
    except Exception as e:
        logging.error(f"API Call Returned Error with message {response_data}")

def get_existing_ids_from_bq(project_id, dataset_id, table_id):
    
    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)
    query = f"SELECT ID FROM `{table_id}`"
    query_job = client.query(query)
    result = query_job.result() 
    # result is in row iteration output so geting that output by running a for loop
    existing_ids = [row['ID'] for row in result] 
    return existing_ids

def fetch_new_record_id(input_df, existing_ids ):
    # Creating a for loop result a list of ids from input_df which are not in existing_ids
    list_new_records_id = []
    for id in input_df.id:
        if id  not in existing_ids:
            list_new_records_id.append(id)
    
    new_records_df = input_df[input_df.id.isin(list_new_records_id)]
    logging.info(f"Found {len(new_records_df)} new records to be pushed into BigQuery")
    return new_records_df



def load_raw_data(project_id, dataset_id, table_id, todays_df):
    try:

        # Initialize BigQuery client
        client = bigquery.Client(project=project_id)


        # Configuring Data Loading into BigQuery
        # Data Load Methodology adopted for "WRITE_APPEND"` to append data new data
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  
            source_format=bigquery.SourceFormat.PARQUET,
        )

        # Load data into the BigQuery table
        load_job = client.load_table_from_dataframe(todays_df, f"{table_id}", job_config=job_config)

        # Waiting for the job to complete
        load_job.result()
        logging.info(f"Successful Extraction and Load. Loaded {load_job.output_rows} rows into {table_id}")
    
    except Exception as e:
        logging.error(f"Data Load Function Failed with error {e}")


from config import config
from config.config import API_KEY


api_url = "https://linkedin-api8.p.rapidapi.com/search-jobs"

querystring = {"keywords":"Data Analyst","locationId":"103035651","datePosted":"past24Hours","sort":"mostRecent"}

headers = {
	"x-rapidapi-key": API_KEY,
	"x-rapidapi-host": "linkedin-api8.p.rapidapi.com"
}

# Set your Google Cloud project ID and BigQuery dataset/table info
project_id = 'linkedinapidatapipeline'
dataset_id = 'linkedinapidatapipeline.Raw'
table_id = f"{dataset_id}.Raw_Data"

df_jobs_today = extract_data(url=api_url, headers=headers, params=querystring)


existing_job_ids = get_existing_ids_from_bq(project_id=project_id, dataset_id=dataset_id, table_id=table_id)
df_jobs_today_new_records = fetch_new_record_id(input_df=df_jobs_today, existing_ids=existing_job_ids)

load_raw_data(project_id=project_id, dataset_id=dataset_id, table_id=table_id, todays_df=df_jobs_today_new_records)