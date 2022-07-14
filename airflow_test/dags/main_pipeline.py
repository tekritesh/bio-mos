from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator

from datetime import datetime, timedelta
import pandas as pd
from gbif_modules import HumanInterference, get_occurrences
from bigquery_load import CustomBigqueryInsert, CustomBigqueryQuery, get_schema


def get_gbif_daily(ds, country):
    df = get_occurrences(ds, country) ##ds is airflows default parameter for execution_date
    table_id = "gbif-challenge.airflow_uploads.gbif_occurrence"
    load = CustomBigqueryInsert(df, table_id)
    load.load(schema=get_schema(table_id))

def get_human_daily(ds):
    query = CustomBigqueryQuery()

    sql= f"""SELECT * 
             FROM `gbif-challenge.airflow_uploads.gbif_occurrence` 
             WHERE DATE(eventDate) = '{ds}'
             AND countryCode IN ('BR', 'GB')""" ##hardcoding these two countries for demo

    df = query.query(sql)

    if df.shape[0] > 0: ## check if gbif returned any rows.
        hum_int = HumanInterference(df)
        df_out = hum_int.human_wrapper()

        sql_inv = f"""SELECT * 
                FROM `gbif-challenge.airflow_uploads.invasive_species` 
                WHERE countryCode IN ('BR', 'GB')""" ##hardcoding these two countries for demo

        df_inv = query.query(sql_inv)

        inv_dict = { 'BR': list(set(df_inv[df_inv.countryCode=='BRA'].scientificName.to_list())),
                'GB': list(set(df_inv[df_inv.countryCode=='GBR'].scientificName.to_list())) }

        df_out['is_invasive'] = df_out[['countryCode','scientificName']].\
                        apply(lambda x: True if x['scientificName'] in inv_dict[x['countryCode']] else False, axis=1)

        table_id = "gbif-challenge.airflow_uploads.human_interference"
        load = CustomBigqueryInsert(df_out, table_id)
        load.load(schema=get_schema(table_id))



with DAG(
    'main_pipeline',
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        'depends_on_past': True,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=3),
        'end_date': datetime(2022, 4, 5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function,
        # 'on_success_callback': some_other_function,
        # 'on_retry_callback': another_function,
        # 'sla_miss_callback': yet_another_function,
        # 'trigger_rule': 'all_success'
    },
    description='our gbif pipeline to append covariate data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 4, 4),
    catchup=False,
    tags=['draft'],
) as dag:

    pull_occ_br = PythonOperator(task_id='pull_occ', python_callable=get_gbif_daily,
                             op_kwargs={###"eventDate":'2022-04-04',
                                        "country": 'BR'})

    pull_human	= PythonOperator(task_id='pull_human', python_callable=get_human_daily)                                 )

    pull_occ_br >> [pull_human]
    









