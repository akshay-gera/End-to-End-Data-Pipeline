import os
import logging
from google.cloud import bigquery
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta


# Setting up the logging for the DAG execution
log_file_path = os.path.join(os.getcwd(), 'test_gcp_connection.log')
logging.basicConfig(
    filename=log_file_path,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



# Google Cloud BigQuery Project Name and Data Set
project_id = 'linkedinapidatapipeline'
dataset_id = f"{project_id}.Raw"
table_id = f"{dataset_id}.Raw_Data"
# Function to test Google Cloud connection (BigQuery)
def test_gcp_connection(project_id=project_id, dataset_id=dataset_id, table_id=table_id):
    try:
        # Using BigQueryHook which will automatically pull connection from Airflow UI
        hook = BigQueryHook(gcp_conn_id='google_cloud')  # Use your connection ID here
        
        # Initialize BigQuery client via the hook
        client = hook.get_client(project_id)
        # Fetch a list of datasets (just to test if the connection is working)
        datasets = list(client.list_datasets())
        print(datasets)  # Will list datasets in the project
        
        
        if datasets:
            logging.info(f"Successfully connected to Google Cloud BigQuery. Found {len(datasets)} datasets.")
            print('Starting working on query')
            try:
                table_name = table_id.split('.')[-1]
                query = f"SELECT column_name FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS` WHERE table_name = '{table_name}';"
                query_job = client.query(query)
                result = query_job.result() 
                # result is in row iteration output so geting that output by running a for loop
                existing_columns = [row['column_name'] for row in result]
                print(existing_columns) 
            except Exception as e:
                logging.error(f"Failed to fetch schema from BigQuery: {e}")
        else:
            logging.warning("Successfully connected to Google Cloud BigQuery, but no datasets found.")

    
    except Exception as e:
        logging.error(f"Failed to connect to Google Cloud BigQuery: {e}")

# DAG definition
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 2, 16),
    'catchup': False,
}

dag = DAG(
    'test_gcp_connection',
    default_args=default_args,
    description='Test Google Cloud BigQuery connection',
    schedule_interval=None,  # This is a one-time manual run
)

# Task to test Google Cloud connection
test_connection_task = PythonOperator(
    task_id='test_gcp_connection',
    python_callable=test_gcp_connection,
    dag=dag,
)

# Set the task dependencies (only one task here)
test_connection_task
