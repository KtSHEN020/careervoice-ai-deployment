from __future__ import annotations

from dataclasses import dataclass

import pytest

from careervoice_ai_web_app.document_recognition import (
    DEFAULT_DOCUMENT_RECOGNITION_MODEL,
    OpenAIDocumentRecognizer,
)
from careervoice_ai_web_app.scanned_document import RenderedDocumentPage


@dataclass
class FakeResponse:
    output_text: str


class FakeResponses:
    def __init__(
        self,
        *,
        output_text: str = "Alex Chen\nPython\nAdelaide",
        error: Exception | None = None,
    ) -> None:
        self.output_text = output_text
        self.error = error
        self.calls: list[dict[str, object]] = []

    def create(
        self,
        **kwargs: object,
    ) -> FakeResponse:
        self.calls.append(kwargs)

        if self.error is not None:
            raise self.error

        return FakeResponse(
            output_text=self.output_text,
        )


class FakeOpenAIClient:
    def __init__(
        self,
        *,
        responses: FakeResponses,
    ) -> None:
        self.responses = responses


def _page(
    number: int = 1,
) -> RenderedDocumentPage:
    return RenderedDocumentPage(
        page_number=number,
        image_bytes=b"\x89PNGfake-image",
    )


def test_recognize_single_scanned_page() -> None:
    responses = FakeResponses(
        output_text=(
            "Alex Chen\n"
            "Junior Software Developer\n"
            "Python\n"
            "Adelaide"
        )
    )

    recognizer = OpenAIDocumentRecognizer(
        client=FakeOpenAIClient(
            responses=responses
        )
    )

    result = recognizer.recognize(
        [_page()]
    )

    assert result.text == (
        "Alex Chen\n"
        "Junior Software Developer\n"
        "Python\n"
        "Adelaide"
    )
    assert result.page_count == 1
    assert (
        result.model
        == DEFAULT_DOCUMENT_RECOGNITION_MODEL
    )


def test_recognizer_sends_each_page_as_image_input() -> None:
    responses = FakeResponses()

    recognizer = OpenAIDocumentRecognizer(
        client=FakeOpenAIClient(
            responses=responses
        )
    )

    recognizer.recognize(
        [
            _page(1),
            _page(2),
        ]
    )

    call = responses.calls[0]

    assert (
        call["model"]
        == DEFAULT_DOCUMENT_RECOGNITION_MODEL
    )

    input_value = call["input"]

    assert isinstance(input_value, list)

    message = input_value[0]

    assert isinstance(message, dict)

    content = message["content"]

    assert isinstance(content, list)

    image_items = [
        item
        for item in content
        if isinstance(item, dict)
        and item.get("type") == "input_image"
    ]

    assert len(image_items) == 2

    assert all(
        str(item["image_url"]).startswith(
            "data:image/png;base64,"
        )
        for item in image_items
    )


def test_recognizer_rejects_empty_page_list() -> None:
    recognizer = OpenAIDocumentRecognizer(
        client=FakeOpenAIClient(
            responses=FakeResponses()
        )
    )

    with pytest.raises(
        ValueError,
        match="No document pages",
    ):
        recognizer.recognize([])


def test_recognizer_rejects_empty_ai_output() -> None:
    recognizer = OpenAIDocumentRecognizer(
        client=FakeOpenAIClient(
            responses=FakeResponses(
                output_text="   "
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="No readable text",
    ):
        recognizer.recognize(
            [_page()]
        )


def test_recognizer_converts_api_failure_to_safe_error() -> None:
    recognizer = OpenAIDocumentRecognizer(
        client=FakeOpenAIClient(
            responses=FakeResponses(
                error=RuntimeError(
                    "simulated API failure"
                )
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="could not be recognized",
    ):
        recognizer.recognize(
            [_page()]
        )