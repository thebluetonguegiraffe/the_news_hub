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
    "test_dag",
    default_args=default_args,
    start_date=datetime(2025, 8, 1),
    catchup=False,
    tags=["test"],
)

notify_success = PythonOperator(
    task_id="notify_success",
    python_callable=send_email,
    op_kwargs={
        "to_email": "thebluetonguegiraffe@gmail.com",
        "subject": "Test email ✅",
        "body": "Your task finished successfully!",
    },
    dag=dag,
)


failed_task = BashOperator(
    task_id="failed_task",
    bash_command=("shs"),
    email_on_failure=True,
    dag=dag,
)

notify_success >> failed_task
