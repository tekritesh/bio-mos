from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator

from datetime import datetime, timedelta
import pandas as pd
from gbif_modules import HumanInterference, get_occurrences, GetClimateData, LandCover, SoilData
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

def get_climate_daily(ds):
    query = CustomBigqueryQuery()

    sql= f"""SELECT * 
             FROM `gbif-challenge.airflow_uploads.gbif_occurrence` 
             WHERE DATE(eventDate) = '{ds}'
             AND countryCode IN ('BR', 'GB')""" ##hardcoding these two countries for demo

    df = query.query(sql)

    if df.shape[0] > 0: ## check if gbif returned any rows.
        climate_df = GetClimateData(df)

        df_out = climate_df.climate_wrapper()

        table_id = "gbif-challenge.airflow_uploads.climate_covariates"
        load = CustomBigqueryInsert(df_out, table_id)
        load.load(schema=get_schema(table_id))

def get_land_cover_daily(ds):
    query = CustomBigqueryQuery()

    sql= f"""SELECT * 
             FROM `gbif-challenge.airflow_uploads.gbif_occurrence` 
             WHERE DATE(eventDate) = '{ds}'
             AND countryCode IN ('BR', 'GB')""" ##hardcoding these two countries for demo

    df = query.query(sql)

    if df.shape[0] > 0: ## check if gbif returned any rows.
        land_df = LandCover(df)

        df_out = land_df.land_cover_wrapper()

        table_id = "gbif-challenge.airflow_uploads.land_cover"
        load = CustomBigqueryInsert(df_out, table_id)
        load.load(schema=get_schema(table_id))

def get_soil_daily(ds):
    query = CustomBigqueryQuery()

    sql= f"""SELECT * 
             FROM `gbif-challenge.airflow_uploads.gbif_occurrence` 
             WHERE DATE(eventDate) = '{ds}'
             AND countryCode IN ('BR', 'GB')""" ##hardcoding these two countries for demo

    df = query.query(sql)

    if df.shape[0] > 0: ## check if gbif returned any rows.
        soil_df = SoilData(df)

        df_out = soil_df.soil_wrapper()

        table_id = "gbif-challenge.airflow_uploads.soil_type"
        load = CustomBigqueryInsert(df_out, table_id)
        load.load(schema=get_schema(table_id))

def push_combined_data_bigquery(ds):
    query = CustomBigqueryQuery()
##can also use sql insert into here instead of custom python insert, INSERT INTO `gbif-challenge.airflow_uploads.gbif_combined` 
    sql= f"""SELECT
                occ.key,
                occ.publishingCountry,
                occ.basisOfRecord,
                occ.occurrenceStatus,
                occ.scientificName,
                occ.acceptedScientificName,
                occ.kingdom,
                occ.phylum,
                occ.order,
                occ.family,
                occ.genus,
                occ.species,
                occ.genericName,
                occ.specificEpithet,
                occ.taxonRank,
                occ.taxonomicStatus,
                occ.iucnRedListCategory,
                occ.decimalLongitude,
                occ.decimalLatitude,
                occ.coordinateUncertaintyInMeters,
                occ.eventDate,
                occ.issues,
                occ.class,
                occ.countryCode,
                occ.country,
                occ.datasetName,
                hum.avg_radiance,
                hum.avg_deg_urban,
                hum.is_invasive,
                land.land_cover_label,
                cli.tavg,
                cli.tmin,
                cli.tmax,
                cli.prcp,
                cli.snow,
                cli.wdir,
                cli.wspd,
                cli.wpgt,
                cli.pres,
                cli.tsun,
                soil.phh2o_0_5cm_mean,
                soil.bdod_0_5cm_mean,
                soil.cec_0_5cm_mean,
                soil.cfvo_0_5cm_mean,
                soil.clay_0_5cm_mean,
                soil.nitrogen_0_5cm_mean,
                soil.sand_0_5cm_mean,
                soil.silt_0_5cm_mean,
                soil.soc_0_5cm_mean,
                soil.ocd_0_5cm_mean
                FROM
                (SELECT * 
                FROM `gbif-challenge.airflow_uploads.gbif_occurrence` 
                WHERE
                    DATE(eventDate) = '{ds}'
                    AND countryCode IN ('BR', 'GB')
                ) as occ
                LEFT JOIN (SELECT * 
                            FROM `gbif-challenge.airflow_uploads.human_interference` 
                            WHERE
                                DATE(eventDate) = '{ds}'
                                AND countryCode IN ('BR', 'GB')
                ) as hum
                USING (key, decimalLatitude, decimalLongitude, eventDate, countryCode)
                LEFT JOIN (SELECT * 
                            FROM `gbif-challenge.airflow_uploads.climate_covariates` 
                            WHERE
                                DATE(eventDate) = '{ds}'
                                AND countryCode IN ('BR', 'GB')
                ) as cli
                USING (key, decimalLatitude, decimalLongitude, eventDate, countryCode)
                LEFT JOIN (SELECT * 
                            FROM `gbif-challenge.airflow_uploads.land_cover` 
                            WHERE
                                DATE(eventDate) = '{ds}'
                                AND countryCode IN ('BR', 'GB')
                ) as land
                USING (key, decimalLatitude, decimalLongitude, eventDate, countryCode)
                LEFT JOIN (SELECT * 
                            FROM `gbif-challenge.airflow_uploads.soil_type` 
                            WHERE
                                DATE(eventDate) = '{ds}'
                                AND countryCode IN ('BR', 'GB')
                ) as soil
                USING (key, decimalLatitude, decimalLongitude, eventDate, countryCode)
             """ 

    df = query.query(sql)

    if df.shape[0] > 0: ## check if gbif returned any rows.
        table_id = "gbif-challenge.airflow_uploads.gbif_combined"
        load = CustomBigqueryInsert(df, table_id)
        load.load(schema=get_schema(table_id))


with DAG(
    'main_pipeline',
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        #'depends_on_past': True,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=2),
        'end_date': datetime(2022, 5, 31),
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
    tags=['version_1'],
) as dag:

    pull_occ_br = PythonOperator(task_id='pull_occ_br', python_callable=get_gbif_daily,
                             op_kwargs={###"eventDate":'2022-04-04',
                                        "country": 'BR'})

    pull_occ_gb = PythonOperator(task_id='pull_occ_gb', python_callable=get_gbif_daily,
                             op_kwargs={"country": 'GB'})

    pull_human	= PythonOperator(task_id='pull_human', python_callable=get_human_daily) 
    pull_climate = PythonOperator(task_id='pull_climate', python_callable=get_climate_daily)      
    pull_land_cover = PythonOperator(task_id='pull_land_cover', python_callable=get_land_cover_daily)  
    pull_soil = PythonOperator(task_id='pull_soil', python_callable=get_soil_daily)  

    #combine_df = PythonOperator(task_id='combine_df', python_callable=push_combined_data_bigquery)                                      
                                     
     ##airflow does not support list to list operands, so breaking it into two                            
    # pull_occ_br >> [pull_human, pull_climate, pull_land_cover, pull_soil]  >> combine_df
    # pull_occ_gb >> [pull_human, pull_climate, pull_land_cover, pull_soil]  >> combine_df
    pull_occ_br >> [pull_human, pull_climate, pull_land_cover, pull_soil]  
    pull_occ_gb >> [pull_human, pull_climate, pull_land_cover, pull_soil]  




    









