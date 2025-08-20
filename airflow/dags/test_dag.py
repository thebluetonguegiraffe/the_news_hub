from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

# Default arguments for the DAG
default_args = {
    "owner": "news_rs",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    "test_news_dag",
    default_args=default_args,
    description="A simple test DAG for news processing",
    # schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["test", "news"],
)


def print_hello():
    """Simple function to test Python operator"""
    print("Hello from Airflow!")
    return "success"


# Define tasks
hello_task = PythonOperator(
    task_id="hello_python",
    python_callable=print_hello,
    dag=dag,
)

bash_task = BashOperator(
    task_id="hello_bash",
    bash_command='echo "Hello from Bash!"',
    dag=dag,
)

# Set task dependencies
hello_task >> bash_task
