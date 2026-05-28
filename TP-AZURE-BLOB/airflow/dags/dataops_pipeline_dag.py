from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"

with DAG(
    dag_id="dataops_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["dataops", "dbt", "airflow"],
) as dag:

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "dbt run --project-dir dataops_dbt "
            "--profiles-dir /opt/airflow/project/.dbt"
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "dbt test --project-dir dataops_dbt "
            "--profiles-dir /opt/airflow/project/.dbt"
        ),
    )

    dbt_run >> dbt_test
