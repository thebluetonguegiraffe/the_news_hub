#!/bin/bash
set -e

# Make sure we're in the right directory
cd ~/the_news_hub/news_rs

export AIRFLOW_HOME=$(pwd)/airflow
echo "Setting AIRFLOW_HOME to $AIRFLOW_HOME"

export AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags
echo "Setting AIRFLOW__CORE__DAGS_FOLDER to $AIRFLOW__CORE__DAGS_FOLDER"

export AIRFLOW__CORE__SQL_ALCHEMY_CONN="mysql+mysqldb://airflow:${MYSQL_PASSWORD}@127.0.0.1:3306/airflow"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Verify the configuration is correct
echo "Verifying configuration..."
airflow config get-value core dags_folder
airflow config get-value core load_examples

# Create directories
mkdir -p $AIRFLOW__CORE__DAGS_FOLDER
mkdir -p $AIRFLOW_HOME/logs

# Reset database
airflow db reset --yes

# Start scheduler
echo "Starting scheduler..."
nohup airflow scheduler > $AIRFLOW_HOME/logs/scheduler.log 2>&1 &

# Wait for scheduler to scan DAGs
echo "Waiting for scheduler to scan DAGs..."
sleep 15

# Check for DAGs
echo "Listing DAGs..."
airflow dags reserialize
airflow dags list

# Check for any import errors
echo "Checking for import errors..."
airflow dags list-import-errors

# Start API server
airflow api-server --host 127.0.0.1 --port 8080