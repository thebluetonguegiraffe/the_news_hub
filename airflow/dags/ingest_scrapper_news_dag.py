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
    "email_on_retry": False,
}

dag = DAG(
    "ingest_scrapper_news_dag",
    default_args=default_args,
    description="DAG for API news ingestion",
    schedule="55 23 * * *",  # Run every day at 23:55
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "news", "scrapper"],
)

ingest_news = BashOperator(
    task_id="ingest_scrapper_news",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/ && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/ingest_scrapper_news.py "
    ),
    dag=dag,
)

notify_success = PythonOperator(
    task_id="notify_success",
    python_callable=send_email,
    op_kwargs={
        "to_email": "thebluetonguegiraffe@gmail.com",
        "subject": "SCRAPPER News ingestion Dag Success ✅",
        "body": "Your task finished successfully!",
    },
    dag=dag,
)

(
    ingest_news
    >> notify_success
)
