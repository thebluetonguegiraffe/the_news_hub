from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

DOCKER_IMAGE_NAME = "ghcr.io/thebluetonguegiraffe/the_news_hub:latest"

ENVIRONMENT = {
    "PYTHONPATH": "/the_news_hub",
    "CHROMA_DB_TOKEN": "{{ var.value.CHROMA_DB_TOKEN }}",
    "MISTRAL_API_KEY": "{{ var.value.MISTRAL_API_KEY }}",
    "MONGO_URI_TOKEN": "{{ var.value.MONGO_URI_TOKEN }}",
}

default_args = {
    "owner": "the_blue_tongue_giraffe_dev",
    "depends_on_past": False,
    "email": ["thebluetonguegiraffe@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    # The Mistral plan rate-limits aggressively. The code retries individual
    # calls, and these task-level retries cover a longer outage on top of that.
    "retries": 2,
    "retry_delay": timedelta(minutes=15),
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

BUCKET = "{{ data_interval_end.subtract(hours=3).strftime('%Y-%m-%dT%H:%M') }}"

topics_enrichement = DockerOperator(
    task_id="topics_enrichement",
    image=DOCKER_IMAGE_NAME,
    auto_remove=True,
    command=f"""
    sh -c "
    echo 'RUNNING python scripts/db_population/topics_enrichement.py --date {BUCKET} --overwrite'
    python scripts/db_population/topics_enrichement.py --date {BUCKET} --overwrite
    "
    """,  # noqa
    environment=ENVIRONMENT,
    network_mode="bridge",
    docker_url="unix://var/run/docker.sock",
    dag=dag,
    docker_conn_id="ghcr_test",
    force_pull=True,
    # output in the mail
    do_xcom_push=True,
    xcom_all=True,
)

# The scrapers can take many hours to drain a bucket, so documents regularly
# land after the run for their own bucket has finished. This pass picks up
# whatever is still unlabelled in the last week, which keeps the backlog at zero
# without re-labelling anything that already has a category.
topics_catchup = DockerOperator(
    task_id="topics_catchup",
    image=DOCKER_IMAGE_NAME,
    auto_remove=True,
    command="""
    sh -c "
    echo 'RUNNING python scripts/db_population/backfill_topics.py --days 7'
    python scripts/db_population/backfill_topics.py --days 7
    "
    """,  # noqa
    environment=ENVIRONMENT,
    network_mode="bridge",
    docker_url="unix://var/run/docker.sock",
    dag=dag,
    docker_conn_id="ghcr_test",
    force_pull=False,
    do_xcom_push=True,
    xcom_all=True,
)

topics_enrichement >> topics_catchup
