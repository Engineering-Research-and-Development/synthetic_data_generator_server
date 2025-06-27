import numpy as np
from abc import ABC, abstractmethod

from ai_lib.post_process.functions.FunctionResult import FunctionResult
from ai_lib.post_process.functions.Parameter import Parameter


class UnspecializedFunction(ABC):
    def __init__(self, parameters: list[dict]):
        self.parameters = [Parameter.from_json(param) for param in parameters]

    @abstractmethod
    def _check_parameters(self):
        raise NotImplementedError

    @abstractmethod
    def _compute(self, data: np.array) -> tuple[np.array, np.array]:
        """
        Applies a data transformation function on a given set of generated data
        :param data: a numpy array of data from a single feature
        :return: transformed data and affected indexes
        """
        raise NotImplementedError

    @abstractmethod
    def _evaluate(self, data: np.array) -> bool:
        """
        Applies an evaluation function on a given set of generated data
        :param data: a numpy array of data from a single feature
        :return: a single boolean value evaluating id data meets evaluation criteria
        """
        raise NotImplementedError

    @classmethod
    def self_describe(cls):
        raise NotImplementedError

    def get_results(self, data: np.array) -> dict:
        results, indexes = self._compute(data)
        evaluation_results = self._evaluate(data)
        report = FunctionResult(results, indexes, evaluation_results)
        return report.to_dict()
