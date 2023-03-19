from pathlib import Path
import pandas as pd 
import os 
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task
def extract_from_gcs():
    logger = get_run_logger()
    logger.info(f"Retrieving data from GCS bucket to /raw_data.")
    gcp_cloud_storage_bucket_block = GcsBucket.load("tsnpdcl-gcs-block")
    gcp_cloud_storage_bucket_block.get_directory(from_path= 'raw_data/')
    logger.info(f"Data retrieval from GCS to local finished.")

@task
def write_to_bq():
    logger = get_run_logger()
    gcp_credentials_block = GcpCredentials.load("tsnpdcl-gcp-cred-block")

    csv_dir = 'raw_data/'
    rows = 0
    cur_rows = 0
    for root, _, files in os.walk(csv_dir):
        for file in files:
            path = f"{csv_dir}{file}"
            logger.info(f"Adding data from {path}")

            df = pd.read_parquet(path)
            if rows==0:
                replace_append = "replace"
            else:
                replace_append = "append"
            logger.info(f"using {replace_append}")

            cur_rows = df.shape[0]
            rows += cur_rows
            df.to_gbq(
                destination_table='tsnpdcl_BQ_raw.tsnpdcl',
                project_id='tsnpdcl-zoomcamp',
                credentials=gcp_credentials_block.get_credentials_from_service_account(),
                chunksize=500_000,
                if_exists=replace_append,
            )

            logger.info(f"Data of {path} uploaded to BigQuery. No. of rows added {cur_rows}.")
            # break

    logger.info(f"All the data uploaded to BigQuery. Total no. of rows uploaded {rows}.")

@task(name="Clean_job_in_gcs_to_bq")
def clean_data():
    logger = get_run_logger()
    os.system('rm -rf ./raw_data')
    logger.info(f"./raw_data directory has been deleted")


@flow()
def gcs_to_bq():
    extract_from_gcs()
    write_to_bq()
    clean_data()

if __name__=='__main__':
    gcs_to_bq()