from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import os
import shutil

SENTIMENT_ANALYSIS_DIR = '../sentiment_analysis'
STREAMLIT_DIR = '../streamlit'
FETCH_REVIEWS_SCRIPT = os.path.join(SENTIMENT_ANALYSIS_DIR, 'get_reviews_updated.py')
ANALYZE_REVIEWS_SCRIPT = os.path.join(SENTIMENT_ANALYSIS_DIR, 'analyze_reviews.py')
VISUALIZATION_SCRIPT = os.path.join(STREAMLIT_DIR, 'visualization.py')
FETCHED_REVIEWS_CSV = os.path.join(SENTIMENT_ANALYSIS_DIR, 'fetchedReviews.csv')
ANALYZED_REVIEWS_CSV = os.path.join(SENTIMENT_ANALYSIS_DIR, 'analyzed_reviews.csv')
STREAMLIT_ANALYZED_CSV = os.path.join(STREAMLIT_DIR, 'analyzed_reviews.csv')

def fetch_reviews():
    os.system(f'python3 {FETCH_REVIEWS_SCRIPT}')

def analyze_reviews():
    os.system(f'python3 {ANALYZE_REVIEWS_SCRIPT}')

def copy_analyzed_reviews():
    shutil.copy(ANALYZED_REVIEWS_CSV, STREAMLIT_ANALYZED_CSV)

def run_visualization():
    os.system(f'streamlit run {VISUALIZATION_SCRIPT}')

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'app_store_reviews_analysis',
    default_args=default_args,
    description='dag para controlar o workflow do tcc',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 6, 27),
    catchup=False,
)

start = DummyOperator(task_id='start', dag=dag)

fetch_reviews_task = PythonOperator(
    task_id='fetch_reviews',
    python_callable=fetch_reviews,
    dag=dag,
)

analyze_reviews_task = PythonOperator(
    task_id='analyze_reviews',
    python_callable=analyze_reviews,
    dag=dag,
)

copy_analyzed_reviews_task = PythonOperator(
    task_id='copy_analyzed_reviews',
    python_callable=copy_analyzed_reviews,
    dag=dag,
)

run_visualization_task = PythonOperator(
    task_id='run_visualization',
    python_callable=run_visualization,
    dag=dag,
)

start >> fetch_reviews_task >> analyze_reviews_task >> copy_analyzed_reviews_task >> run_visualization_task
