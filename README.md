# TSNPDCL Domestic Power Consumption

## Data Engineering Zoomcamp Project

This repository contains my project for the completion of [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) by [DataTalks.Club](https://datatalks.club).

### Index
- [Problem Description](#problem-description)
- [Dataset](#dataset)
- [Technologies Used](#technologies-used)
- [Steps for Project Reproduction](#steps-for-project-reproduction)
- [Dashboard](#dashboard)
## Problem Description
The Northern Power Distribution Company of Telangana (TSNPDCL) is the electricity distribution company owned by the government of Telangana for the 18 northern districts of Telangana. 
The purpose of this basic project is to analyze domestic power consumption of Telangana State Norther districts from Jan 2019 to Feb 2023 and understand the consumption patterns across different seasons for the last four years. 

Below is the high level overview of the steps involved:
 * Download csv data from Source.
 * Upload the data to Data Lake by transforming csv into efficient parquet format.
 * Loading the data from Data Lake to Data Warehouse with some transformations and data quality checks.
 
 ## Dataset
 The chosen dataset was the domestic power consumption of northern districts of Telangana State, India from Jan 2019 to Feb 2023.
 It includes monthly power consumed (in Units and as well as Load) data per each area in a separate csv file. 
 It is available for [download as csv](https://data.telangana.gov.in/dataset/ts-npdcl-domestic-consumption-data)  and has one csv file for each month. For download automation using Kaggle API, I have uploaded this data till Feb 2023 (latest data as of the project date) to Kaggle and using [Kaggle as data source](https://www.kaggle.com/datasets/dattapadal/tsnpdcl-domestic-consumption-data).
 
 ### Columns
| Field 		| Description 	|  
| -----------   | -----------   |  
| Area   		| District in Northen part of Telangana state, India|  
| Division	 	| Division within Area|
| SubDivision	| Sub-Division within Division|
| Section		| Section within SubDivision|
| Area			| Area within Section|
| CatCode		| Code Type of connection. 1 denotes Domestic|
| CatDesc		| Type of connection|
| TotServices	| Total Services (Number of connections during the month)|
| BilledServices| Billed Services (Number of Connection billed during the month)|
| Units			| It will give details of units billed in a month|
| Load			| It will give details of load billed (in kW) in a month|

## Technologies Used

Below tools have been used for this project:
- **Infrastructure as code (IaC):** Terraform
- **Workflow orchestration:** Prefect
- **Containerization:** Docker
- **Data Lake:** Google Cloud Storage (GCS)
- **Data Warehouse:** BigQuery
- **Transformations:** dbt
- **Visualization:** Google Data Studio

## Steps for Project Reproduction
Clone this repo to start with.

### Step 1
Creation of a [Google Cloud Platform (GCP)](https://cloud.google.com/) account.

### Step 2: Setup of GCP 
- Creation of new GCP project. Attention: The Project ID is important. 
- Go to `IAM & Admin > Service accounts > Create service account`, provide a service account name and grant the roles `Viewer`, `BigQuery Admin`, `Storage Admin`, `Storage Object Admin`. 
- Download lservice account key locally, rename it to `google_credentials.json`. 
- Store it in your home folder `$HOME/.google/credentials/`for easier access. 
- Set and export the GOOGLE_APPLICATION_CREDENTIALS using `export GOOGLE_APPLICATION_CREDENTIALS=<path/to/your/service-account-authkeys>.json`
- Activate the service account using `gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS`
- Add the above two lines at the end of `.bashrc` so that we don't need to export and activate every time.
- Activate the following API's:
   * https://console.cloud.google.com/apis/library/iam.googleapis.com
   * https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com

### Step 3: Creation of a GCP Infrastructure
- [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- Change default variables `project`, `region`, `BQ_DATASET` in `variables.tf` (the file contains descriptions explaining these variables)
- Run the following commands on bash:
```shell
# Initialize state file (.tfstate)
terraform init

# Check changes to new infra plan
terraform plan -var="project=<your-gcp-project-id>"

# Create new infra
terraform apply -var="project=<your-gcp-project-id>"
```
- Confirm in GCP console that the infrastructure was correctly created.

### Step 4: Creation of Conda environment and Orchestration using prefect flows.

#### Execution

**1.** Create a new Conda environment and install packages listed in  `requirements.txt` . 
```
conda create -n deenv python=3.9
conda activate <env_name>
pip install -r requirements.txt
```
**2.** Register Prefect blocks and start Orion

```
prefect block register-m prefect_gcp
prefect orion start
```
* Navigate to prefect dashboard `http://127.0.0.1:4200` --> go to blocks menu --> add `GCS Bucket` and provide below inputs.
	* Block name : `<your-GCS-bucket-block-name>`
	* Bucket name: `<your-bucket-name-created-by-terraform>`
	* GCP credentials:  Click on Add --> It opens up create block of GCP credentials , provide input below.
		* Block name : `<your-GCP-credentials-block-name>`
		* Service Account info: copy paste the json file data in the service account info.
		* Clicck on create.
	* GCP credentials:  Click on Add --> Select the above created `<your-GCP-credentials-block-name>`
	* Code generated needs to be replaced in the `web-to-gcs-parent.py` and `gcs_to_bq_parent`python files.
		```
		from prefect_gcp.cloud_storage import GcsBucket
		gcp_cloud_storage_bucket_block = GcsBucket.load("<your-gcp-bucket-block-name")

		from prefect_gcp import GcpCredentials
		gcp_credentials_block = GcpCredentials.load("<your-gcs-cred-block-name>")

		```    
**2.** Create Kaggle key and move its json file to root folder:
* Navigate to [Kaggle ](kaggle.com) --> Account --> create a new API token under API, save this kaggle.json and move it to root folder.

    
**3.** Create Docker image and push it to docker hub :
* Create docker image with below command 
	```
	docker image build -t <your-docker-user-name>/<docker-image-name>:<tag> .
	```
* Navigate to [docker hub](https://hub.docker.com/), create an account and generate Access token, save the same.
* Authenticate docker in local environment by using below command, paste the above generated docker key when prompted.
	```
	docker login -u <your-docker-user-name>
	```
* Push the above built docker image.
	```
	docker image push <your-docker-user-name>/<docker-image-name>:<tag>
	```
**4.** Create Docker Container block and create deployments in prefect:
* Navigate to prefect blocks and add a new Docker container block with `<docker-image-name>` and mount volume as `path/to/your/kaggle.json:/root/.kaggle/kaggel.json` so that kaggle download api works with your userid.

* Copy the code from above created docker container block in `docker-deploy.py` file and run the python file to create deployments.
	```
	python docker-deploy.py
	```
* Navigate to prefect deployment dashboard and check for the recently created deployments. 

**5.** Run deployments using below commands

		
		prefect deployment run web-to-gcs/docker_web_to_gcs
		prefect deployment run gcs-to-bq/docker_gcs_to_bq

The above deployments download csv data from kaggle and stores it into GCS bucket as .parquet file and then creates two new columns `year` and `month_int` and writes data into Google BigQuery.

### Step 5: Transformations using dbt.

* Navigate to [dbt cloud](https://www.getdbt.com/) and create a new project by referring to this repository. Under the project subfolder update `/dbt`
* Select the BigQuery connection and update `service-account.json` file for the authentication. 
* Under dbt development menu, edit the `dbt-project.yml` to update the `name` and `models`.
* Navigate to `/dbt/models/staging/schema.yml` update the `sources: name, database, schema and tables`
* Run below commands to execute the transformations:
	```
	dbt deps
	dbt build --vars 'is_test_run: false'
	``` 
* The above will create dbt models and final tables with appropriate partition keys. 
   Note: Considering the given amount of data we don't really need partition by as the performance improvement is not much, but still created partition on `year` just to use this project as template.
   * Create an environment inside dbt with appropriate BigQuery dataset details and dbt commands and run click on the deploy command to get the final deployment BigQuery dataset

 ### Step 6: Development of a visualization using lookerstudio

 * Connect the final BigQuery dataset from above inside lookerstudio and start creating the dashboard with insights. 
 
 ## Dashboard

Below is the final [dashboard](https://lookerstudio.google.com/s/pPae5bMmgq4)

![Dashboard_pdf_link](/images/TSNPDCL_Power_consumption_-_DE_project.pdf)

**A special thank you to [DataTalks.Club](https://datatalks.club) for providing this incredible course! Also, thank you to the amazing slack community!**
