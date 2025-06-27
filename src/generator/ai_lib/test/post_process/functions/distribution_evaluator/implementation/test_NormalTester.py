import pytest
import numpy as np

from ai_lib.post_process.functions.distribution_evaluator.implementation.NormalTester import (
    NormalTester,
)


@pytest.fixture
def correct_instance():
    params = [
        {"name": "mean", "value": "0.0", "parameter_type": "float"},
        {"name": "standard_deviation", "value": "1.0", "parameter_type": "float"},
    ]
    return NormalTester(parameters=params)


def test_check_parameters(correct_instance):
    param_mapping = {param.name: param for param in correct_instance.parameters}
    param_names = param_mapping.keys()
    assert param_mapping["mean"].value == 0.0
    assert isinstance(param_mapping["mean"].value, float)
    assert param_mapping["standard_deviation"].value == 1.0
    assert isinstance(param_mapping["standard_deviation"].value, float)
    assert "mean" in param_names
    assert "standard_deviation" in param_names


def test_compute(correct_instance):
    data = np.random.normal(correct_instance.mean, correct_instance.std, 10000)
    compute_data, indexes = correct_instance._compute(data)
    assert data.shape == (10000,)
    assert indexes.shape == (10000,)
    assert np.all(compute_data == data)
    assert np.all(indexes == np.array(range(len(data))))


def test_evaluate(correct_instance):
    correct_data = np.random.normal(correct_instance.mean, correct_instance.std, 10000)
    assert correct_instance._evaluate(correct_data)


def test_evaluate_wrong(correct_instance):
    wrong_data = np.random.normal(5, 1, 10000)
    wrong_data_2 = np.random.normal(0, 10, 10000)
    assert not correct_instance._evaluate(wrong_data)
    assert not correct_instance._evaluate(wrong_data_2)


def test_get_result(correct_instance):
    data_correct = np.random.normal(correct_instance.mean, correct_instance.std, 10000)
    results = correct_instance.get_results(data_correct)
    assert results["results"].shape == (10000,)
    assert results["indexes"].shape == (10000,)
    assert results["evaluation_results"]
