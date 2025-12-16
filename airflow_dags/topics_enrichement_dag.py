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
    schedule="55 14,02 * * *",  # Run every day at 02:55 and at 14:55
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["ingestion", "topics", "mongo"],
)


topics_enrichement = DockerOperator(
    task_id="topics_enrichement",
    image=DOCKER_IMAGE_NAME,
    auto_remove=True,
    command="""
    sh -c "
    echo 'RUNNING python scripts/db_population/topics_enrichement.py --date {{ data_interval_end.subtract(hours=3).strftime('%Y-%m-%dT%H:%M') }} --overwrite'
    python scripts/db_population/topics_enrichement.py --date {{ data_interval_end.subtract(hours=3).strftime('%Y-%m-%dT%H:%M') }} --overwrite
    "
    """,  # noqa
    environment={
        "PYTHONPATH": "/the_news_hub",
        "CHROMA_DB_TOKEN": "{{ var.value.CHROMA_DB_TOKEN }}",
        "GITHUB_TOKEN": "{{ var.value.GITHUB_TOKEN }}",
        "MONGO_URI_TOKEN": "{{ var.value.MONGO_URI_TOKEN }}",
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
    subject="News Topics Enrichement Dag Success for {{ data_interval_end.strftime('%Y-%m-%dT%H:%M') }} ✅", # noqa
    html_content="""
    <h3>Execution Report:</h3>
    <pre style="background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd;">
    {{ ti.xcom_pull(task_ids='topics_enrichement') | join('\n') }}
    </pre>
    """,
    dag=dag,
)

topics_enrichement >> notify_success
