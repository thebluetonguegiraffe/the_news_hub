from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

from src.utils.mail_sender import send_email

default_args = {
    "owner": "the_blue_tongue_giraffe_dev",
    "depends_on_past": False,
    "email": ["thebluetonguegiraffe@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False
}

dag = DAG(
    dag_id="ingest_topics_dag",
    default_args=default_args,
    description="DAG for news ingestion and topic enrichment",
    schedule="02 00 * * *",  # Run every day at 02:00
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "topics", "mongo"],
)

ingest_topics = BashOperator(
    task_id="ingest_topics",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/news_rs && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/ingest_topics.py "
        "--date {{ macros.ds_add(ds, -1) }}T23:55"
    ),
    dag=dag,
)


notify_success = PythonOperator(
    task_id='notify_success',
    python_callable=send_email,
    op_kwargs={
        "to_email": "thebluetonguegiraffe@gmail.com",
        "subject": "News topic ingestion Dag Success ✅",
        "body": "Your task finished successfully!",
    },
    dag=dag
)

ingest_topics >> notify_success