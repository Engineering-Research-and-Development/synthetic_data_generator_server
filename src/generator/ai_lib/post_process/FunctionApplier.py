import numpy as np

from ai_lib.post_process.functions.UnspecializedFunction import UnspecializedFunction


class FunctionApplier:
    def __init__(self, functions: list[UnspecializedFunction], data: list[np.array]):
        self.functions = functions
        self.data = data

    def apply(self):
        pass
