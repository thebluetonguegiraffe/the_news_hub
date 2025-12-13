from datetime import datetime
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.email import EmailOperator

DOCKER_IMAGE_NAME = "ghcr.io/thebluetonguegiraffe/the_news_hub:latest"

default_args = {
    "owner": "the_blue_tongue_giraffe_dev",
    "depends_on_past": False,
    "email": ["thebluetonguegiraffe@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
}

dag = DAG(
    "ingest_api_news_dag",
    default_args=default_args,
    description="DAG for API news ingestion running on Docker",
    schedule="55 23 * * *",
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "news", "docker"],
)

ingest_news = DockerOperator(
    task_id="ingest_api_news",
    image=DOCKER_IMAGE_NAME,
    auto_remove=True,
    command="""
    sh -c "
    echo 'RUNNING python scripts/db_population/ingest_api_news.py --date {{ ds }}T23:55'
    python scripts/db_population/ingest_api_news.py --date {{ ds }}T23:55
    "
    """,
    environment={
        "PYTHONPATH": "/the_news_hub",
        "CHROMA_DB_TOKEN": "{{ var.value.CHROMA_DB_TOKEN }}",
        "FINLIGHT_API_TOKEN": "{{ var.value.FINLIGHT_API_TOKEN }}",
        "GITHUB_TOKEN": "{{ var.value.GITHUB_TOKEN }}",
    },
    network_mode="bridge",
    docker_url="unix://var/run/docker.sock",
    dag=dag,
    docker_conn_id="ghcr_test",
    force_pull=True
)

notify_success = EmailOperator(
    task_id="notify_success",
    to="thebluetonguegiraffe@gmail.com",
    subject="API News ingestion Dag Success for date {{ ds }}T23:55 ✅",
    html_content="Your task finished successfully!",
    dag=dag,
)

ingest_news >> notify_success
