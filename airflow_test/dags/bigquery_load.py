from google.cloud import bigquery
from pandas import DataFrame
import os

PATH = '/Users/advikabattini/Desktop/gbif/bio-conservation/airflow/dags/gbif-challenge-1cd64d18b349.json'

schema_dict = {
"gbif-challenge.airflow_uploads.gbif_occurrence": [bigquery.SchemaField("key", "INTEGER"),
                                                    bigquery.SchemaField("datasetKey", "STRING"),
                                                    bigquery.SchemaField("publishingCountry", "STRING"),
                                                    bigquery.SchemaField("protocol", "STRING"),
                                                    bigquery.SchemaField("lastCrawled", "TIMESTAMP"),
                                                    bigquery.SchemaField("lastParsed", "TIMESTAMP"),
                                                    bigquery.SchemaField("crawlId", "INTEGER"),
                                                    bigquery.SchemaField("key", "INTEGER"),
                                                    bigquery.SchemaField("datasetKey", "STRING"),
                                                    bigquery.SchemaField("publishingCountry", "STRING"),
                                                    bigquery.SchemaField("protocol", "STRING"),
                                                    bigquery.SchemaField("lastCrawled", "TIMESTAMP"),
                                                    bigquery.SchemaField("lastParsed", "TIMESTAMP"),
                                                    bigquery.SchemaField("crawlId", "INTEGER"),
                                                    bigquery.SchemaField("basisOfRecord", "STRING"),
                                                    bigquery.SchemaField("occurrenceStatus", "STRING"),
                                                    bigquery.SchemaField("taxonKey", "INTEGER"),
                                                    bigquery.SchemaField("kingdomKey", "INTEGER"),
                                                    bigquery.SchemaField("phylumKey", "INTEGER"),
                                                    bigquery.SchemaField("classKey", "INTEGER"),
                                                    bigquery.SchemaField("orderKey", "INTEGER"),
                                                    bigquery.SchemaField("familyKey", "INTEGER"),
                                                    bigquery.SchemaField("genusKey", "INTEGER"),
                                                    bigquery.SchemaField("speciesKey", "FLOAT"),
                                                    bigquery.SchemaField("acceptedTaxonKey", "INTEGER"),
                                                    bigquery.SchemaField("scientificName", "STRING"),
                                                    bigquery.SchemaField("acceptedScientificName", "STRING"),
                                                    bigquery.SchemaField("kingdom", "STRING"),
                                                    bigquery.SchemaField("phylum", "STRING"),
                                                    bigquery.SchemaField("order", "STRING"),
                                                    bigquery.SchemaField("family", "STRING"),
                                                    bigquery.SchemaField("genus", "STRING"),
                                                    bigquery.SchemaField("species", "STRING"),
                                                    bigquery.SchemaField("genericName", "STRING"),
                                                    bigquery.SchemaField("specificEpithet", "STRING"),
                                                    bigquery.SchemaField("taxonRank", "STRING"),
                                                    bigquery.SchemaField("taxonomicStatus", "STRING"),
                                                    bigquery.SchemaField("iucnRedListCategory", "STRING"),
                                                    bigquery.SchemaField("decimalLongitude", "FLOAT"),
                                                    bigquery.SchemaField("decimalLatitude", "FLOAT"),
                                                    bigquery.SchemaField("coordinateUncertaintyInMeters", "FLOAT"),
                                                    bigquery.SchemaField("year", "INTEGER"),
                                                    bigquery.SchemaField("month", "INTEGER"),
                                                    bigquery.SchemaField("day", "INTEGER"),
                                                    bigquery.SchemaField("eventDate", "TIMESTAMP"),
                                                    bigquery.SchemaField("issues", "STRING"),
                                                    bigquery.SchemaField("modified", "TIMESTAMP"),
                                                    bigquery.SchemaField("lastInterpreted", "TIMESTAMP"),
                                                    bigquery.SchemaField("recordedBy", "STRING"),
                                                    bigquery.SchemaField("identifiedBy", "STRING"),
                                                    bigquery.SchemaField("class", "STRING"),
                                                    bigquery.SchemaField("countryCode", "STRING"),
                                                    bigquery.SchemaField("country", "STRING"),
                                                    bigquery.SchemaField("dateIdentified", "TIMESTAMP"),
                                                    bigquery.SchemaField("datasetName", "STRING"),
                                                ],

"gbif-challenge.airflow_uploads.human_interference": [bigquery.SchemaField("decimalLatitude", "FLOAT"),
                                                    bigquery.SchemaField("decimalLongitude", "FLOAT"),
                                                    bigquery.SchemaField("countryCode", "STRING"),
                                                    bigquery.SchemaField("eventDate", "TIMESTAMP"),
                                                    bigquery.SchemaField("avg_radiance", "FLOAT"),
                                                    bigquery.SchemaField("avg_deg_urban", "FLOAT"),
                                                    bigquery.SchemaField("scientificName", "STRING"),
                                                    bigquery.SchemaField("is_invasive", "BOOLEAN"),
                                                ]

}

def get_schema(table_id):
    return schema_dict[table_id]


class CustomBigqueryInsert():

    def __init__(self, dataframe, table_id) -> None:
        self.dataframe = dataframe
        self.table_id = table_id
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH

    def load(self, schema) -> None:
        #connect to BigQuery
        client = bigquery.Client()
        job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND",
                                                schema = schema ,
                                        autodetect=False,
                                        source_format=bigquery.SourceFormat.CSV)
        job = client.load_table_from_dataframe(
            self.dataframe,
            self.table_id,
            job_config=job_config
        ) 
        job.result()  
        table = client.get_table(self.table_id)
        print(
            "Loaded {} rows and {} columns to {}".format(
                self.dataframe.shape[0], len(table.schema), self.table_id
            )
        )

class CustomBigqueryQuery():

    def __init__(self) -> None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH

    def query(self, sql):
        client = bigquery.Client()
        job_config = bigquery.QueryJobConfig()

        df = client.query(
            sql,
            location="US",
            job_config=job_config).to_dataframe()
        return df