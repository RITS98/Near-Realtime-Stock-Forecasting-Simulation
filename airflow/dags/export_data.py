from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sdk import Variable
from datetime import date, datetime
import time
import logging
import psycopg2
from airflow.hooks.base import BaseHook
import boto3
from airflow.exceptions import AirflowSkipException

default_args = {
    "owner": "Ritayan Patra",
    "start_date": datetime(2025, 7, 17),
    "retries": 0,
}

DAG_ID = "postgres_to_dynamodb_continuous"
TABLE_NAME = "netflix-stock-data-table-ritayan"
POSTGRES_CONFIG = {
    "host": "db",
    "port": 5432,
    "user": "stock_user",
    "password": "stock_pass",
    "dbname": "stock_data"
}

def serialize_value(val):
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return val

def transfer_100_rows(**kwargs):
    
    last_index = int(Variable.get("last_index", 0))
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()

    # Fetch next 100 rows by ID lookup
    found_rows = 0
    for offset in range(100):
        current_id = last_index + offset
        cursor.execute("SELECT * FROM netflix_historical.stock_prices WHERE id = %s", (current_id,))
        row = cursor.fetchone()

        if not row:
            print(f"✅ No row found for ID = {current_id}, skipping.")
            continue
        
        found_rows += 1
        columns = [desc[0] for desc in cursor.description]


        row_dict = {}
        for col, val in zip(columns, row):
            if col == "id":
                row_dict[col] = str(val)  # 🔑 Convert primary key 'id' to string
            else:
                row_dict[col] = serialize_value(val)

        # DynamoDB
        aws_conn = BaseHook.get_connection("aws-credentials")
        session = boto3.Session(
            aws_access_key_id=aws_conn.login,
            aws_secret_access_key=aws_conn.password,
            region_name=aws_conn.extra_dejson.get("region_name", "us-east-1")
        )

        dynamodb = session.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=row_dict)

        print(f"Transferred ID {current_id} → DynamoDB")

    if found_rows == 0:
        raise AirflowSkipException(f"No new records found starting from id {last_index}")
    # Update last_index by +100
    Variable.set("last_index", str(last_index + 100))

    # Sleep 1 second between batches
    time.sleep(1)

with DAG(
    dag_id="postgres_to_dynamodb_batch_streaming",
    default_args=default_args,
    schedule="*/1 * * * *",  # runs every 1 minute
    catchup=False,
    max_active_runs=1,
    tags=["batch", "postgres", "dynamodb"],
) as dag:

    transfer_task = PythonOperator(
        task_id="transfer_100_rows",
        python_callable=transfer_100_rows,
    )