from typing import List, Literal, Optional

from pydantic import BaseModel, PositiveInt, Field


#################### INPUTS - DATA ####################


class BaseColumn(BaseModel):
    column_name: str
    column_datatype: Literal["float32", "float64", "int32", "int64", "str"]
    column_type: Literal["continuous", "categorical", "primary_key", "group_index"]


class Data(BaseColumn):
    column_data: List[float | int | str] | List


class DatasetInTrain(BaseModel):
    data: List[Data]
    dataset_type: Literal["table", "time_series"]


class DatasetInInfer(BaseModel):
    data: Optional[List[Data]] = []
    dataset_type: Literal["table", "time_series"]


class DataSkeleton(BaseColumn):
    column_position: PositiveInt
    column_size: PositiveInt


#################### INPUTS - MODEL ####################


class BaseModelInfo(BaseModel):
    algorithm_name: str
    model_name: str


class InferModelInfoData(BaseModelInfo):
    image: str
    input_shape: str = Field(pattern=r"\([0-9]+,(([0-9]+,?)+)?\)", examples=["(3,4)"])


class InferModelInfoNodata(InferModelInfoData):
    training_data_info: List[DataSkeleton] = []


#################### INPUTS - FUNCTIONS ####################


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


#################### INPUTS - TRAINING ####################


class TrainRequest(BaseModel):
    model: BaseModelInfo
    dataset: DatasetInTrain
    functions: Optional[List[Function]] = []
    n_rows: PositiveInt


#################### INPUTS - INFER ####################


class InferRequest(BaseModel):
    model: InferModelInfoNodata
    functions: Optional[List[Function]] = []
    n_rows: PositiveInt
    dataset: DatasetInInfer


########################################## OUTPUTS ##########################################


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
