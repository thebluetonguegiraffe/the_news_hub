

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator


default_args = {
    "owner": "the_blue_tongue_giraffe_dev",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["thebluetonguegiraffe+dev@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    # "retries": 1,
    # "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "news_population_dag",
    default_args=default_args,
    description="DAG for news ingestion and topic enrichment",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "news"],
)

ingest_news = BashOperator(
    task_id="ingest_news",
    bash_command=(
        "python ../scripts/db_population/ingest_news.py "
        "--source www.nytimes.com,www.bbc.com,www.theguardian.com,www.washingtonpost.com "
        "--date {{ params.ingest_date }}"
    ),
    params={
        "ingest_date": "{{ execution_date.strftime('%Y-%m-%dT00:00') }}"
    },
    dag=dag,
)

enrich_with_topic = BashOperator(
    task_id="enrich_with_topic",
    bash_command=(
        "python ../scripts/db_population/populate_topic.py "
        "--date {{ params.ingest_date }}"
    ),
    params={
        "ingest_date": "{{ execution_date.strftime('%Y-%m-%dT00:00') }}"
    },
    dag=dag,
)


ingest_news >> enrich_with_topic
