from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, PositiveInt, Field


################### ALLOWED TYPES ####################


class SupportedDataTypes(str, Enum):
    float = "float32"
    int = "int32"
    str = "str"
    bool = "bool"


class SupportedFeatureTypes(str, Enum):
    continuous = "continuous"
    categorical = "categorical"
    primary_key = "primary_key"
    group_index = "group_index"


#################### INPUTS - DATA ####################


class BaseColumn(BaseModel):
    column_name: str
    column_datatype: SupportedDataTypes
    column_type: SupportedFeatureTypes


class Data(BaseColumn):
    column_data: List[float | int | str] | List


"""
TODO: Implement this
class DatasetInTrain(BaseModel):
    data: List[Data]
    dataset_type: Literal["table", "time_series"]


class DatasetInInfer(BaseModel):
    data: Optional[List[Data]] = []
    dataset_type: Literal["table", "time_series"]
"""


class DataSkeleton(BaseColumn):
    column_position: int
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
    dataset: List[Data]
    functions: Optional[List[Function]] = []
    n_rows: PositiveInt


#################### INPUTS - INFER ####################


class InferRequest(BaseModel):
    model: InferModelInfoNodata
    functions: Optional[List[Function]] = []
    n_rows: PositiveInt
    dataset: Optional[List[Data]] = []


################### INPUTS - GENERATION ################


class GenerationRequest(BaseModel):
    functions: List[Function]
    n_rows: PositiveInt


########################################## OUTPUTS ##########################################


class GeneratedData(BaseModel):
    column_data: List[float | int]
    column_name: str
    column_datatype: SupportedDataTypes
    column_type: SupportedFeatureTypes


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
