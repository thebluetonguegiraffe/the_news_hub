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
    "ingest_scrapper_news_dag",
    default_args=default_args,
    description="DAG for API news ingestion",
    schedule="55 11,23 * * *",  # Run every day at 23:55
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "news", "scrapper"],
)


ingest_news_scrapper = DockerOperator(
    task_id="ingest_scrapper_news",
    image=DOCKER_IMAGE_NAME,
    auto_remove=True,
    command="""
    sh -c "
    echo 'RUNNING: python scripts/db_population/ingest_scrapper_news.py'
    python scripts/db_population/ingest_scrapper_news.py --date
     {{ (data_interval_end - macros.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M') }}
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
    force_pull=True,
    # output in the mail
    do_xcom_push=True,
    xcom_all=True,
)

notify_success = EmailOperator(
    task_id="notify_success",
    to="thebluetonguegiraffe@gmail.com",
    subject="Scrapper News Scrapper Dag Success for {{ data_interval_end.strftime('%Y-%m-%dT%H:%M') }}✅",  # noqa
    html_content="""
    <h3>Execution Report:</h3>
    <pre style="background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd;">
    {{ ti.xcom_pull(task_ids='ingest_scrapper_news') | join('\n') }}
    </pre>
    """,
    dag=dag,
)


ingest_news_scrapper >> notify_success
