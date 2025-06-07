"""
Helper for data parsing and upload

Author: Andres Pescara <andrespescara@gmail.com>
"""

import logging

import pandas as pd
import pendulum
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from unidecode import unidecode

logger = logging.Logger(__name__)


class Parser:
    def __init__(self) -> None:
        """Parser helper, also handles data upload."""

    def read_file(
        self,
        file_path: str,
        engine: str,
        sheet: str,
    ) -> None:
        """Read XLSX, parse as STRING, norm columns and add load dt at index 0.

        Args:
            file_path (str): File path. Can handle GCS.
            engine (str): Engine used to read file. openpyxl for xlsx and xlrd for xls.
            sheet (str): Sheet name.
        """
        df_ = pd.read_excel(file_path, engine=engine, sheet_name=sheet).astype(str)
        df_.columns = df_.columns.str.lower().str.replace(" ", "_").map(unidecode)
        df_.insert(
            loc=0,
            column="fecha_carga",
            value=pd.to_datetime(pendulum.now("America/Santiago").isoformat()),
        )
        self.df_ = df_

    def updload_to_bq(
        self,
        project_id: str,
        dataset_id: str,
        table_id: str,
    ) -> None:
        """Upload data to BigQuery, can hadle dataset and table creation but not project.

        rgs:
            project_id (str): Project ID.
            dataset_id (str): Dataset ID. Created on NotFound.
            table_id (str): Table ID. Created on NotFound.
        """
        if not self.df_.empty:
            client = bigquery.Client(project_id)

            try:
                client.get_dataset(dataset_id)  # Make an API request.
                logger.info(f"Dataset {dataset_id} already exists")
            except NotFound:
                logger.warning(f"Dataset {dataset_id} not found, creating")
                dataset = bigquery.Dataset(project_id + "." + dataset_id)
                dataset.location = "us-east1"
                client.create_dataset(dataset, timeout=30)
                logger.warning(f"Dataset {dataset_id} created")

            table = ".".join(
                [
                    project_id,
                    dataset_id,
                    table_id,
                ]
            )
            logger.info("Loading data to BigQuery")
            job_config = bigquery.LoadJobConfig()
            job_config.write_disposition = "WRITE_APPEND"
            job_config.schema_update_options = [
                bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
            ]
            job_config.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field="fecha_carga"
            )
            try:
                load_job = client.load_table_from_dataframe(
                    self.df_,
                    table,
                    job_config=job_config,
                )
                load_job.result()
                logger.info("Dataframe loaded succesfully")
            except Exception as e:
                logger.warning(e)
                logger.warning(
                    "Cloud not load to specified table, retrying with suffix"
                )
                now = pendulum.now("America/Santiago").format("YYYYMMDDHHmmss")
                load_job = client.load_table_from_dataframe(
                    self.df_,
                    table + now,
                    job_config=job_config,
                )
                load_job.result()
                logger.warning(f"Dataframe loaded succesfully with the {now} suffix")
        else:
            logger.warning("No data to upload")
