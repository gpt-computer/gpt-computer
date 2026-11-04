import unittest

import gptc

from gptc import ChatCompletion

from .mocks import ModelProviderMock

DEFAULT_MESSAGES = [{"role": "user", "content": "Hello"}]

test_model = gptc.models.Model(
    name="test/test_model", base_provider="", best_provider=ModelProviderMock
)
gptc.models.ModelUtils.convert["test_model"] = test_model


class TestPassModel(unittest.TestCase):
    def test_model_instance(self):
        response = ChatCompletion.create(test_model, DEFAULT_MESSAGES)
        self.assertEqual(test_model.name, response)

    def test_model_name(self):
        response = ChatCompletion.create("test_model", DEFAULT_MESSAGES)
        self.assertEqual(test_model.name, response)

    def test_model_pass(self):
        response = ChatCompletion.create(
            "test/test_model", DEFAULT_MESSAGES, ModelProviderMock
        )
        self.assertEqual(test_model.name, response)
