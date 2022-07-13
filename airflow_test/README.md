# Airflow setup and testing instructions

## Specific required installations:
Note: you may have to install other basic libraries like pandas, numpy.
1. pip install airflow (first check this: https://airflow.apache.org/docs/apache-airflow/stable/start/local.html)
2. pip install google-cloud-bigquery[pandas,pyarrow]
3. pip install pygbif
4. pip install ee (might need authentication when running it for the first time, can comment out human interference code to avoid)

## To connect to bigquery programatically
1. Need service account credentials to connect to bigquery: https://cloud.google.com/bigquery/docs/reference/libraries#setting_up_authentication
2. After downloading the json file locally, update the PATH variable in the 'dags/bigquery_load.py' file. 

## To start setup:
1. Navigate to your 'airflow' folder that was installed by pip. Then take the dags folder from here and paste it in your 'airflow' folder. 
2. In your terminal run: <br>
    export AIRFLOW_HOME=[Your airflow folder path], for example <br>
    export AIRFLOW_HOME = ~/airflow
3. In a seperate terminal, run the following command <br>
    airflow scheduler
4. In a seperate terminal, run the following command <br>
    airflow webserver
5. In a seperate terminal, run the following command <br>
    airflow db init <br>
    follow this by a test backfill command <br>
    airflow dags test main_pipeline 2022-04-04


