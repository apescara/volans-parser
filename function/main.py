"""
Cloud Function to Upload data for Volans, initialy developed for appointments and customers.

Author: Andres Pescara <andrespescara@gmail.com>
"""

import logging
import time

import functions_framework
import gcsfs  # noqa: F401
from cloudevents.http import CloudEvent

from parser import Parser

start_time = time.time()
logger = logging.Logger(__name__)


@functions_framework.cloud_event
def main(cloud_event: CloudEvent) -> None:
    data = cloud_event.data
    bucket = data["bucket"]
    name = data["name"]
    file_path = f"gs://{bucket}/{name}"

    logger.info("Got the following file_path: %s", file_path)

    if "citas" in file_path:
        table_id = "citas"
        engine = "xlrd"
        sheet = "Citas"
    elif "pacientes" in file_path:
        table_id = "pacientes"
        engine = "openpyxl"
        sheet = "Pacientes"
    else:
        raise ValueError("Invalid file_path")

    prs = Parser()

    prs.read_file(file_path=file_path, engine=engine, sheet=sheet)
    prs.updload_to_bq(
        project_id="clinica-volans",
        dataset_id="data_base",
        table_id=table_id,
    )

    total_time = time.time() - start_time
    logger.info("Total execution time: %s seconds", total_time)
