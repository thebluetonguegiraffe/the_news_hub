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
    "ingest_and_enrich_news_dag",
    default_args=default_args,
    description="DAG for news ingestion and topic enrichment",
    schedule="55 23 * * *",  # Run every day at 23:55
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "news"],
)

ingest_news_tnyt = BashOperator(
    task_id="ingest_news_tnyt",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/news_rs && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/ingest_news.py "
        "--source www.nytimes.com "
        "--date {{  ds  }}T23:55"
    ),
    dag=dag,
)

ingest_news_bbc = BashOperator(
    task_id="ingest_news_bbc",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/news_rs && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/ingest_news.py "
        "--source www.bbc.com "
        "--date {{  ds  }}T23:55"
    ),
    dag=dag,
)

ingest_news_guardian = BashOperator(
    task_id="ingest_news_guardian",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/news_rs && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/ingest_news.py "
        "--source www.theguardian.com "
        "--date {{  ds  }}T23:55"
    ),
    dag=dag,
)

ingest_news_twp = BashOperator(
    task_id="ingest_news_twp",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/news_rs && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/ingest_news.py "
        "--source www.washingtonpost.com "
        "--date {{  ds  }}T23:55"
    ),
    dag=dag,
)

enrich_with_topic = BashOperator(
    task_id="enrich_with_topic",
    bash_command=(
        "cd /home/ubuntu/the_news_hub/news_rs && "
        "export PYTHONPATH=. && "
        "python scripts/db_population/populate_topic.py "
        "--date {{  ds  }}T23:55 "
        "--topics-history DEFAULT"
    ),
    dag=dag,
)

notify_success = PythonOperator(
    task_id='notify_success',
    python_callable=send_email,
    op_kwargs={
        "to_email": "thebluetonguegiraffe@gmail.com",
        "subject": "News ingestion and enrichment Dag Success ✅",
        "body": "Your task finished successfully!",
    },
    dag=dag
)

ingest_news_tnyt >> ingest_news_bbc >> ingest_news_guardian >> ingest_news_twp >> enrich_with_topic >> notify_success
