from typing import List, Literal, Optional

from pydantic import BaseModel, PositiveInt, Field


class TrainingDataInfo(BaseModel):
    column_name: str
    column_datatype: Literal["float32", "float64", "int32", "int64"]
    column_type: Literal["continuous", "categorical", "time_series"]


class DatasetIn(TrainingDataInfo):
    column_data: List[float | int] | List


class TrainModelInfo(BaseModel):
    algorithm_name: str
    model_name: str


class Parameter(BaseModel):
    name: str
    value: str
    parameter_type: str


class Function(BaseModel):
    feature: str = Field(
        pattern="^[^ ](.*[^ ])?$",
        description="This field does NOT allow strings that"
        " start or end with spaces or are empty",
        examples=["A feature name"],
    )
    function_reference: str
    parameters: List[Parameter]


class InferModelInfoData(BaseModel):
    algorithm_name: str
    model_name: str
    image: str
    input_shape: str = Field(pattern=r"\([0-9]+,(([0-9]+,?)+)?\)")


class InferModelInfoNodata(InferModelInfoData):
    training_data_info: List[TrainingDataInfo] = []


class TrainRequest(BaseModel):
    model: TrainModelInfo
    dataset: List[DatasetIn]
    functions: Optional[List[Function]] = []
    n_rows: PositiveInt


class InferRequestNoData(BaseModel):
    model: InferModelInfoNodata
    functions: Optional[List[Function]] = []
    n_rows: PositiveInt


class InferRequest(InferRequestNoData):
    dataset: List[DatasetIn]


##################################
class GeneratedData(BaseModel):
    column_data: List[float | int]
    column_name: str
    column_datatype: Literal["float32", "float64", "int32", "int64"]
    column_type: Literal["continuous", "categorical"]


class Metric(BaseModel):
    title: str
    value: float | int | dict
    unit_measure: str


class MetricReport(BaseModel):
    statistical_metrics: list[Metric]
    adherence_metrics: list[Metric]
    novelty_metrics: list[Metric]


class GeneratedResponse(BaseModel):
    result_data: GeneratedData
    metrics: Optional[MetricReport] = {}


class CouchEntry(BaseModel):
    doc_id: str
