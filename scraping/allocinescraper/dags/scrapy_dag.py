from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import subprocess
from airflow.models import Variable

def run_scrapy():
    if Variable.get("scraping_enabled", default_var="true") == "false":
        print("⏸️ Scraping désactivé via Variable Airflow.")
        return
    subprocess.call([
        'docker', 'run', '--rm',
        '-v', '/opt/airflow/data:/app/data',  # volume partagé
        'allocineacr.azurecr.io/scraping-allocine:latest'
    ])

schedule = Variable.get("scrapy_schedule", default_var="*/15 * * * *")

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 4, 15, 9, 0),  # Début le 15 avril à 9h00
}

dag = DAG(
    'scrapy_dag',
    default_args=default_args,
    schedule_interval=schedule,
    catchup=False,
)

run_scrapy_task = PythonOperator(
    task_id='run_scrapy',
    python_callable=run_scrapy,
    dag=dag,
)
