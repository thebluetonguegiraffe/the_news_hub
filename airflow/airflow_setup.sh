#!/bin/bash
set -e

# Make sure we're in the right directory
cd ~/the_news_hub/news_rs

export GMAIL_PWD=$(grep '^GMAIL_PWD=' "$(pwd)/.env" | cut -d '=' -f2-)
export GMAIL_PWD_NO_SPACES=$(grep '^GMAIL_PWD_NO_SPACES=' "$(pwd)/.env" | cut -d '=' -f2-)
echo $GMAIL_PWD

export AIRFLOW_HOME=$(pwd)/airflow
echo "Setting AIRFLOW_HOME to $AIRFLOW_HOME"

export AIRFLOW__CORE__DAGS_FOLDER=$AIRFLOW_HOME/dags
echo "Setting AIRFLOW__CORE__DAGS_FOLDER to $AIRFLOW__CORE__DAGS_FOLDER"

export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////home/ubuntu/the_news_hub/news_rs/airflow/airflow.db
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Verify the configuration is correct
echo "Verifying configuration..."
airflow config get-value core dags_folder
airflow config get-value core load_examples

# Create directories
mkdir -p $AIRFLOW__CORE__DAGS_FOLDER
mkdir -p $AIRFLOW_HOME/logs

# Set up mail server configuration
export AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
export AIRFLOW__SMTP__SMTP_STARTTLS=True
export AIRFLOW__SMTP__SMTP_SSL=False
export AIRFLOW__SMTP__SMTP_PORT=587
export AIRFLOW__SMTP__SMTP_MAIL_FROM=thebluetonguegiraffe@gmail.com
export AIRFLOW__SMTP__SMTP_USER=thebluetonguegiraffe@gmail.com
export AIRFLOW__SMTP__SMTP_PASSWORD=${GMAIL_PWD}

# Initialize the databases
airflow db migrate
# airflow db reset --yes

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

echo "Email configuration..."
airflow config get-value smtp smtp_host
airflow config get-value smtp smtp_user
airflow config get-value smtp smtp_password
airflow connections get smtp_default

# Check for any import errors
echo "Checking for import errors..."
airflow dags list-import-errors

# Start API server
airflow api-server --host 127.0.0.1 --port 8080