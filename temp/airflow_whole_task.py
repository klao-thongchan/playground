from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
'owner': 'test_user',
'start_date': airflow.utils.dates.days_ago(1),
'depends_on_past': False,
'email': ['info@example.com'],
'email_on_failure': True,
'email_on_retry': False,
'retries': 5,
'retry_delay': timedelta(minutes=30),
}

dag = DAG(
'basic_dag_1_0',
default_args=default_args,
schedule_interval=timedelta(days=1),
)

def my_func():
    print('Hello from my_func')
 

bashtask = BashOperator(
task_id='print_date',
bash_command='date',
dag=dag,
)

ready_task 	= DummyOperator(task_id='dummy_task', retries=3)

python_task	= PythonOperator(task_id='python_task', python_callable=my_func)

ready_task.set_downstream(bashtask)
python_task.set_downstream(bashtask)