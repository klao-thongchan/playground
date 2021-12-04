default_args = {
'owner': 'default_user',
'start_date': airflow.utils.dates.days_ago(1),
'depends_on_past': True,
  #With this set to true, the pipeline won't run if the previous day failed
'email': ['info@example.com'],
'email_on_failure': True,
 #upon failure this pipeline will send an email to your email set above
'email_on_retry': False,
'retries': 5,
'retry_delay': timedelta(minutes=30),
}


dag = DAG(
'basic_dag_1',
default_args=default_args,
schedule_interval=timedelta(days=1),
)