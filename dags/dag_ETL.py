import requests
import logging
import os
from google.cloud import bigquery
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
import json
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.models import Variable
import sys
import os
from utils.ETL_functions import extract_data, get_existing_ids_from_bq, fetch_new_record_id, load_raw_data

# Creating a log process in our current directory where extraction and load success or failures will be documented
log_file_path = os.path.join(os.getcwd(), 'extraction.log')
logging.basicConfig(
    filename=log_file_path,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Api End Point and parameters that we want

api_url = "https://linkedin-api8.p.rapidapi.com/search-jobs"

querystring = {"keywords":"Data Analyst","locationId":"103035651","datePosted":"past24Hours","sort":"mostRecent"}
API_KEY = Variable.get("API_KEY")
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "linkedin-api8.p.rapidapi.com"
}


# Google Cloud BigQuery Project Name and Data Set
project_id = 'linkedinapidatapipeline'
dataset_id = f"{project_id}.Raw"
table_id = f"{dataset_id}.Raw_Data"

def api_data_extraction(url, headers, params, ti):
    df_jobs_today = extract_data(url=api_url, headers=headers, params=querystring).to_dict(orient='records')
     # Push the data to XCom
    ti.xcom_push(key='df_jobs_today', value=df_jobs_today)
    return df_jobs_today


def existing_records_check(project_id, dataset_id, table_id, ti):
   
    existing_job_ids =  get_existing_ids_from_bq(project_id=project_id, dataset_id=dataset_id, table_id=table_id)
    ti.xcom_push(key='existing_job_ids', value=existing_job_ids) 
    return existing_job_ids

def fetch_new_records(ti ):
    df_jobs_today = ti.xcom_pull(task_ids='api_data_extraction_task', key='df_jobs_today')  # Fetch data from the previous task
    existing_ids = ti.xcom_pull(task_ids='existing_records_check_task', key='existing_job_ids')  # Fetch existing IDs
    
    # Converting it back to pandas dataframe to perform function as this is coming as a dict from output of api_extraction
    df_jobs_today = pd.DataFrame(df_jobs_today)
    df_jobs_today_new_records = fetch_new_record_id(input_df=df_jobs_today, existing_ids=existing_ids).to_dict(orient='records')
    # Push the new records as dict to XCom
    ti.xcom_push(key='df_jobs_today_new_records', value=df_jobs_today_new_records)
    return df_jobs_today_new_records

def loading(ti):
    todays_df = ti.xcom_pull(task_ids='fetch_new_records_task', key='df_jobs_today_new_records') 
    # Convert the dict back to a DataFrame if needed for loading
    todays_df = pd.DataFrame(todays_df)
    return load_raw_data(project_id=project_id, dataset_id=dataset_id, table_id=table_id, todays_df=todays_df)




# DAG definition
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 2, 15),
    'catchup': False,
}

dag = DAG(
    'Extract_and_Load_Pipeline',
    default_args=default_args,
    description='Extracts data from LinkedIn API and loads it to BigQuery',
    schedule_interval=timedelta(days=1),  # This will run the DAG every day
)

# Task Definitions
api_date_extraction_operator = PythonOperator(
    task_id='api_data_extraction_task',
    python_callable=api_data_extraction,
    op_kwargs={'url': api_url, 'headers': headers, 'params': querystring},
    dag=dag,
)

existing_records_check_operator = PythonOperator(
    task_id='existing_records_check_task',
    python_callable=existing_records_check,
    op_args=[project_id, dataset_id, table_id],
    dag=dag,
)

fetch_new_records_operator = PythonOperator(
    task_id='fetch_new_records_task',
    python_callable=fetch_new_records,
    provide_context=True,  # Ensures that task instance context is available
    dag=dag,
)

loading_operator = PythonOperator(
    task_id='loading_task',
    python_callable=loading,
     provide_context=True,  # Ensures that task instance context is available
    dag=dag,
)

# Task dependencies: This sets the order of task execution
api_date_extraction_operator >> existing_records_check_operator >> fetch_new_records_operator >> loading_operator