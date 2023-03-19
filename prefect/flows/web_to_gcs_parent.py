import pandas as pd 
import kaggle
import os 
import sys
from prefect import flow, task, get_run_logger
from prefect_gcp.cloud_storage import GcsBucket
from prefect.tasks import task_input_hash
from pathlib import Path

@task()
def fetch_data_to_local():
    logger = get_run_logger()
    logger.info(f"Fetching data from Kaggle to Local /raw_data")

    #create raw_data folder.If it already exists, delete and then create.
    if os.path.exists('raw_data'):
        os.system('rm -rf ./raw_data')

    logger.info(f"creating /raw_data directory")
    os.makedirs('raw_data')

    #download data from kaggle using its API
    os.system("kaggle datasets download -d dattapadal/tsnpdcl-domestic-consumption-data -p './raw_data' --unzip")
    logger.info(f"data has been downloaded to local")
    
@task()
def push_data_to_datalake():
    
    logger = get_run_logger()
    gcp_cloud_storage_bucket_block = GcsBucket.load("tsnpdcl-gcs-block")

    #process all the csv files in raw_data folder one by one
    csv_dir = 'raw_data/'
    for root, _, files in os.walk(csv_dir):
        for file in files:
            # File name is in "TS-NPDCL_consumption_detail_general_XXX-YYYY.csv" format 
            # where XXX represents month in 3 character abbreviation like JUN, JUL, FEB, JAN, etc., and
            # YYYY is year
            # Lets retrieve Month and Year from the file name.
            month = file[37:40]
            year = int(file[41:45])

            #Read the csv and create dataframe 
            logger.info(f"Processing data of {year}-{month}.")
            dataset_url = f"{csv_dir}{file}"
            df = pd.read_csv(dataset_url)

            #adding above retrieve year and month as columns
            df['month'] = month 
            df['year'] = year 

            #datatype conversions
            df.CatCode = pd.to_numeric(df.CatCode, errors="coerce")
            df.TotServices = pd.to_numeric(df.TotServices, errors="coerce")
            df.BilledServices = pd.to_numeric(df.BilledServices, errors="coerce")
            df.Units = pd.to_numeric(df.Units, errors="coerce")
            df.Load = pd.to_numeric(df.Load, errors="coerce")
            df = df.astype({'CatCode':'Float64', 'TotServices':'Int64', 'BilledServices': 'Int64', 'Units':'Float64', 'Load':'Float64', })

            #convert file format from csv to parquet
            parquet_file = dataset_url.replace('.csv', '.parquet')
            df.to_parquet(parquet_file, compression='gzip')

            #add the file to GCS
            gcp_cloud_storage_bucket_block.upload_from_path(from_path=parquet_file, to_path=parquet_file)

            logger.info(f"Data upload finished for {year}-{month}.")
            # break

@task(name="Clean_job_in_web_to_gcs")
def clean_data():
    logger = get_run_logger()
    os.system('rm -rf ./raw_data')
    logger.info(f"./raw_data directory has been deleted")

@flow()
def web_to_gcs():
    fetch_data_to_local()
    push_data_to_datalake()
    clean_data()


if __name__=="__main__":
    web_to_gcs()