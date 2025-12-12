from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator

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

notify_success_with_email_operator = EmailOperator(
    task_id="notify_success_with_email_operator",
    to="thebluetonguegiraffe@gmail.com",
    subject="API News ingestion Dag Success ✅",
    html_content="Your task finished successfully!",
    dag=dag,
)


failed_task = BashOperator(
    task_id="failed_task",
    bash_command=("shs"),
    email_on_failure=True,
    dag=dag,
)

notify_success >> notify_success_with_email_operator >> failed_task
