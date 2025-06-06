import pandas as pd
import pendulum
from unidecode import unidecode


class Parser:
    def __init__(
        self, file_path: str, project_id: str, dataset_id: str, table_id: str
    ) -> None:
        self.file_path = file_path
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

    def read_file(self) -> None:
        df_ = pd.read_excel(self.file_path).astype(str)
        df_.columns = df_.columns.str.lower().str.replace(" ", "_").map(unidecode)
        df_.insert(
            loc=0,
            column="fecha_carga",
            value=pd.to_datetime(pendulum.now("America/Santiago").isoformat()),
        )
        self.df_ = df_

    def updload_to_bq(self) -> None:
        