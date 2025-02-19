# Data Pipeline Project using APIs, Python, Google Cloud, Airflow

This repository contains an end-to-end data pipeline that extracts job listings from LinkedIn using their API, processes the data, and loads it into Google BigQuery for further analysis. This pipeline is intended to be used for data extraction, transformation, and loading (ETL) with optional integration into Airflow for scheduling and automation.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technologies Used](#technologies-used)
3. [Getting Started](#getting-started)
4. [Pipeline Overview](#pipeline-overview)
5. [Directory Structure](#directory-structure)
6. [Setup and Configuration](#setup-and-configuration)
7. [Running the Pipeline](#running-the-pipeline)
8. [Airflow DAG Run Sample](#airflow-dag-run-sample)
9. [Data Visualization Sample](#data-visualization-sample)

---

## Project Overview

This project aims to automate the process of extracting job data from LinkedIn's API and storing it into a BigQuery database. It leverages a modular structure, allowing you to execute the pipeline locally or integrate it into scheduling frameworks like Apache Airflow. The ETL pipeline performs the following tasks:

- **Extract**: Fetch job listings from the LinkedIn API.
- **Transform**: Process and clean the data (e.g., normalize JSON and filter based on new records).
- **Load**: Store the data into BigQuery, appending new records to the existing data.

This project can be executed manually via a Python script or can be scheduled via Airflow for automated execution.

---

## Technologies Used

- **Python**: The main programming language used to implement the ETL pipeline.
- **LinkedIn API**: Used to fetch job data. The API is accessed via the RapidAPI platform.
- **Google BigQuery**: Data is loaded into Google Cloud's BigQuery for analysis.
- **pandas**: Used for data manipulation and transformation.
- **logging**: Python’s built-in logging module for tracking the progress and errors during execution.
- **Airflow** (optional): For scheduling and orchestrating the data pipeline (integration possible, but not mandatory for local execution).

---

## Getting Started

Follow these instructions to get the project up and running on your local machine.

## Prerequisites

1. **Python 3.x**: Ensure Python is installed on your system. You can verify it by running:
   ```bash
   python --version

2. Google Cloud account: You need a Google Cloud account to use BigQuery. Make sure you have the correct credentials set up (you can use the Google Cloud SDK).

3. RapidAPI Key: Sign up for the LinkedIn API on RapidAPI, and get your API key.

4. Install dependencies: All dependencies are listed in the requirements.txt file, and you can install them with the following command:
   pip install -r requirements.txt

## Pipeline Overview

The pipeline follows a clear ETL process:

1. **Data Extraction**:
    - The `extract_data()` function fetches job data from the LinkedIn API using the provided parameters (e.g., keywords, location, date).
    
2. **Incremental Loading Logic**:
    - The existing_records_check() would first check what job IDs we already have in our BigQuery data warehouse (table=Raw_Data) to avoid data duplication
    - The `fetch_new_record_id()` function checks for new records by comparing them with existing data stored in BigQuery.
    - We finally get new records after performing this comparing mechanism
    
3. **Data Loading**:
    - The transformed data is loaded into Google BigQuery using the `load_raw_data()` function, which appends new records to the BigQuery table.

The entire ETL process is wrapped in a single function, `run_etl()`, which can be run manually by executing `main.py`.


## Directory Structure
![image](https://github.com/user-attachments/assets/3b5b1152-7b6e-425a-9cbe-43a657386190)




## Setup and Configuration

### 1. **Create a Google Cloud Project**:
   - If you haven't already, create a Google Cloud Project.
   - Enable the **BigQuery API**.
   - Create a Project on BigQuery studio
   - Manually Create a Dataset called Raw (Which will be your Raw schema)
   - Manually Create a Table in Raw dataset called Raw_Data 
   - Create a service account and down service key json
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials-file.json"
    ```

### 2. **Configure LinkedIn API**:
   - Go to RapidAPI, sign up, and subscribe to the LinkedIn API.
   - Get your **API key** from RapidAPI and place it in the `config.py` file.

    ```python
    API_KEY = "your-rapidapi-key"
    ```
### 3. **Airflow Connection Configuration**
   - We are using BigQuery Hook in Airflow DAG to interact with BigQuery through Airflow
   - For that go to Airflow UI and add the connection variable from the service account key JSON file
---

## Running the Pipeline

To run the ETL pipeline locally, follow these steps:

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/your-username/End-to-End-Data-Pipeline.git
   cd End-to-End-Data-Pipeline


2. Install the necessary dependencies:
   pip install -r requirements.txt
3. Set up your environment variables for Google Cloud and LinkedIn API as described above.
4. Run ETL Pipeline
   python main.py

## Airflow DAG Run Sample
Showcasing how Airflow DAG run would like based on the DAG we created
![image](https://github.com/user-attachments/assets/9b002bbf-96a6-4815-88b7-9aaf3b96c23f)
 
Logging of Process Flow on Airflow
 ![image](https://github.com/user-attachments/assets/ab00c152-8520-46bd-a201-3be67e2aa11b)

![image](https://github.com/user-attachments/assets/30a3c798-235e-4609-958f-d3ea23f44ec7)
![image](https://github.com/user-attachments/assets/13182536-87ce-4eba-a600-ace6c1e8d45d)
![image](https://github.com/user-attachments/assets/a3f0a83c-cdac-478a-a1b7-ed5bbd2c0246)




## Data Visualization Sample
-Showcasing how front end dashboard could look like based on this data
![image](https://github.com/user-attachments/assets/50084e93-4f02-4abe-b3d1-29a37e06e735)
