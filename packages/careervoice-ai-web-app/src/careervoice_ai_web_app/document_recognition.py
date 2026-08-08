"""AI-assisted text recognition for image-based career documents."""

from __future__ import annotations

import base64
from collections.abc import Sequence
from dataclasses import dataclass

from openai import OpenAI

from careervoice_ai_web_app.scanned_document import RenderedDocumentPage

DEFAULT_DOCUMENT_RECOGNITION_MODEL = "gpt-5.6-luna"


@dataclass(frozen=True)
class RecognizedDocument:
    """Text recognized from rendered document pages."""

    text: str
    page_count: int
    model: str


class OpenAIDocumentRecognizer:
    """Recognize career-document text from rendered page images."""

    def __init__(
        self,
        *,
        client: OpenAI | None = None,
        model: str = DEFAULT_DOCUMENT_RECOGNITION_MODEL,
    ) -> None:
        self._client = client or OpenAI()
        self._model = model

    def recognize(
        self,
        pages: Sequence[RenderedDocumentPage],
    ) -> RecognizedDocument:
        """Recognize readable text from rendered document pages."""
        if not pages:
            raise ValueError(
                "No document pages were provided for image recognition."
            )

        content: list[dict[str, object]] = [
            {
                "type": "input_text",
                "text": (
                    "Extract the readable text from this CV, resume, or "
                    "career document. Preserve headings, names, dates, "
                    "skills, employment history, education, and other "
                    "career information. Do not summarize, interpret, "
                    "or invent information. Return plain text only, in "
                    "natural reading order."
                ),
            }
        ]

        for page in pages:
            encoded_image = base64.b64encode(
                page.image_bytes
            ).decode("ascii")

            content.append(
                {
                    "type": "input_image",
                    "image_url": (
                        f"data:{page.media_type};base64,"
                        f"{encoded_image}"
                    ),
                }
            )

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
            )
        except Exception as error:
            raise ValueError(
                "The scanned document could not be recognized."
            ) from error

        recognized_text = response.output_text.strip()

        if not recognized_text:
            raise ValueError(
                "No readable text could be recognized from the "
                "scanned document."
            )

        return RecognizedDocument(
            text=recognized_text,
            page_count=len(pages),
            model=self._model,
        )