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
    dag_id="topics_enrichement_dag",
    default_args=default_args,
    description="DAG news topic enrichment",
    schedule="02 00 * * *",  # Run every day at 02:00
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "topics", "mongo"],
)


topics_enrichement = DockerOperator(
    task_id="topics_enrichement",
    image=DOCKER_IMAGE_NAME,
    auto_remove=True,
    command="python scripts/db_population/topics_enrichement.py --date {{ macros.ds_add(ds, -1) }}T23:55",  # noqa
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
    force_pull=True,
)


notify_success = EmailOperator(
    task_id="notify_success",
    to="thebluetonguegiraffe@gmail.com",
    subject="News topic ingestion Dag Success ✅",
    html_content="Your task finished successfully!",
    dag=dag,
)

topics_enrichement >> notify_success
