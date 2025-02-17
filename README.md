# LinkedIn Job Data Pipeline

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
8. [Contributing](#contributing)
9. [License](#license)

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

### Prerequisites

1. **Python 3.x**: Ensure Python is installed on your system. You can verify it by running:
   ```bash
   python --version

2. Google Cloud account: You need a Google Cloud account to use BigQuery. Make sure you have the correct credentials set up (you can use the Google Cloud SDK).

3. RapidAPI Key: Sign up for the LinkedIn API on RapidAPI, and get your API key.

4. Install dependencies: All dependencies are listed in the requirements.txt file, and you can install them with the following command:
