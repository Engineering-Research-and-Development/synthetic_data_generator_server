import numpy as np
from scipy.stats import normaltest, ttest_1samp, kstest, norm

from ai_lib.post_process.functions.FunctionInfo import FunctionInfo
from ai_lib.post_process.functions.UnspecializedFunction import UnspecializedFunction
from ai_lib.post_process.functions.Parameter import Parameter


class NormalTester(UnspecializedFunction):
    def __init__(self, parameters: list[dict]):
        super().__init__(parameters)
        self.mean = None
        self.std = None
        self._check_parameters()

    def _check_parameters(self):
        param_mapping = {param.name: param for param in self.parameters}
        self.mean = param_mapping["mean"].value
        self.std = param_mapping["standard_deviation"].value

    def _compute(self, data: np.array) -> tuple[np.array, np.array]:
        """
        Currently returns same data
        :param data:
        :return:
        """
        return data, np.array(range(len(data)))

    def _evaluate(self, data: np.array) -> bool:
        """
        Checks if data is normally distributed.
        Consider the null hypotesis that data is normally distributed.
        If null hypotesis is rejected (p < 0.05), it means that data is not normally distributed
        Evaluation is based on 3 tests:
        1. D’Agostino and Pearson’s test
        2. Student's t-test
        3. Kolmogorov-Smirnov

        :param data:
        :return: False if null hypotesis is rejected (p < 0.05), True if it is failed to reject (p > 0.05)
        """

        def cdf_function(x):
            return norm.cdf(x, loc=self.mean, scale=self.std)

        _, p_normal = normaltest(data)
        _, p_t = ttest_1samp(data, self.mean)
        _, p_k = kstest(data, cdf_function)
        p = min(p_normal, p_t, p_k)

        return p > 0.05

    @classmethod
    def self_describe(cls):
        return FunctionInfo(
            name=f"{cls.__qualname__}",
            function_reference=f"{cls.__module__}.{cls.__qualname__}",
            parameters=[
                Parameter("mean", 0.0, "float"),
                Parameter("standard_deviation", 1.0, "float"),
            ],
            description="Checks if data is normally distributed given a desired mean and standard deviation",
        ).get_function_info()
