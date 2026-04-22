import sys
import os

# 👇 เพิ่ม path ให้ Airflow หา scripts เจอ
sys.path.append("/opt/airflow")

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# 👇 import หลังจาก set path
from scripts.extract import extract_weather
from scripts.transform import transform_weather
from scripts.load import load_data

# =========================
# DAG CONFIG
# =========================
with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2024, 1, 1),   # ใช้อดีต (best practice)
    schedule_interval="@hourly",       # รันทุกชั่วโมง
    catchup=False                      # ไม่ต้องรันย้อนหลัง
) as dag:

    # =========================
    # TASK 1: EXTRACT
    # =========================
    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_weather
    )

    # =========================
    # TASK 2: TRANSFORM
    # =========================
    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_weather
    )

    # =========================
    # TASK 3: LOAD
    # =========================
    load_task = PythonOperator(
        task_id="load",
        python_callable=load_data
    )

    # =========================
    # PIPELINE FLOW
    # =========================
    extract_task >> transform_task >> load_task