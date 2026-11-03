from unittest import mock

from gpt_computer.applications.cli import learning
from gpt_computer.applications.cli.learning import Learning
from gpt_computer.core.default.disk_memory import DiskMemory
from gpt_computer.core.prompt import Prompt

# Import the actual module where Path is used for patching
from gpt_computer.interfaces import cli as cli_interfaces


def test_human_review_input_no_concent_returns_none():
    with (
        mock.patch.object(
            cli_interfaces.learning, "check_collection_consent", return_value=False
        ),
        mock.patch("builtins.print"),  # Suppress print statements
    ):
        result = learning.human_review_input()

    assert result is None


def test_human_review_input_consent_code_ran_no_comments():
    with (
        mock.patch.object(
            cli_interfaces.learning, "check_collection_consent", return_value=True
        ),
        mock.patch("builtins.input", return_value="y"),
    ):
        result = learning.human_review_input()

    assert result.raw == "y, y, "
    assert result.ran is True
    assert result.works is None
    assert result.comments == ""


def test_human_review_input_consent_code_ran_not_perfect_but_useful_no_comments():
    with (
        mock.patch.object(
            cli_interfaces.learning, "check_collection_consent", return_value=True
        ),
        mock.patch("builtins.input", side_effect=["y", "n", "y", ""]),
    ):
        result = learning.human_review_input()

    assert result.raw == "y, n, y"
    assert result.ran is True
    assert result.works is True
    assert result.comments == ""


def test_check_collection_consent_yes():
    gptc_consent_mock = mock.Mock()
    gptc_consent_mock.exists.return_value = True
    gptc_consent_mock.read_text.return_value = "true"

    with mock.patch.object(
        cli_interfaces.learning, "Path", return_value=gptc_consent_mock
    ):
        result = learning.check_collection_consent()

    assert result is True


def test_check_collection_consent_no_ask_collection_consent():
    with mock.patch.object(cli_interfaces.learning, "Path") as gptc_consent_mock:
        gptc_consent_mock.exists.return_value = True
        gptc_consent_mock.read_text.return_value = "false"

        with mock.patch.object(
            cli_interfaces.learning, "ask_collection_consent", return_value=True
        ):
            result = learning.check_collection_consent()

    assert result is True


def test_ask_collection_consent_yes():
    with (
        mock.patch("builtins.input", return_value="y"),
        mock.patch("builtins.print"),  # Suppress print statements
    ):
        result = cli_interfaces.learning.ask_collection_consent()

    assert result is True


def test_ask_collection_consent_no():
    with (
        mock.patch("builtins.input", return_value="n"),
        mock.patch("builtins.print"),  # Suppress print statements
    ):
        result = cli_interfaces.learning.ask_collection_consent()

    assert result is False


def test_extract_learning():
    review = learning.Review(
        raw="y, n, y",
        ran=True,
        works=True,
        perfect=False,
        comments="The code is not perfect",
    )
    memory = mock.Mock(spec=DiskMemory)
    memory.to_json.return_value = {"prompt": "prompt"}

    result = learning.extract_learning(
        Prompt("prompt"),
        "model_name",
        0.01,
        ("prompt_tokens", "completion_tokens"),
        memory,
        review,
    )

    assert isinstance(result, Learning)


def test_get_session():
    with mock.patch.object(cli_interfaces.learning, "Path") as path_mock:
        # can be better tested with pyfakefs.
        path_mock.return_value.__truediv__.return_value.exists.return_value = False

        with mock.patch.object(cli_interfaces.learning, "random") as random_mock:
            random_mock.randint.return_value = 42
            result = learning.get_session()

        assert result == "42"
