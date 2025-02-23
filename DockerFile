FROM apache/airflow:2.5.1

# Install dependencies from requirements.txt
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
