"""Utilities for preparing scanned PDF pages for document recognition."""

from __future__ import annotations

from dataclasses import dataclass

import fitz

MAX_SCANNED_PDF_PAGES = 5
PDF_RENDER_SCALE = 1.5


@dataclass(frozen=True)
class RenderedDocumentPage:
    """One PDF page rendered as an image."""

    page_number: int
    image_bytes: bytes
    media_type: str = "image/png"


def render_pdf_pages(
    content: bytes,
) -> tuple[RenderedDocumentPage, ...]:
    """Render PDF pages into PNG images for later text recognition."""
    if not isinstance(content, bytes):
        raise ValueError(
            "The uploaded PDF content must be bytes."
        )

    if not content:
        raise ValueError(
            "The uploaded PDF is empty."
        )

    try:
        document = fitz.open(
            stream=content,
            filetype="pdf",
        )
    except Exception as error:
        raise ValueError(
            "The PDF could not be opened for image recognition."
        ) from error

    try:
        page_count = document.page_count

        if page_count == 0:
            raise ValueError(
                "The uploaded PDF does not contain any pages."
            )

        if page_count > MAX_SCANNED_PDF_PAGES:
            raise ValueError(
                "Image-based PDF recognition currently supports "
                f"up to {MAX_SCANNED_PDF_PAGES} pages."
            )

        matrix = fitz.Matrix(
            PDF_RENDER_SCALE,
            PDF_RENDER_SCALE,
        )

        pages: list[RenderedDocumentPage] = []

        for index in range(page_count):
            page = document.load_page(index)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False,
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

            if not image_bytes:
                raise ValueError(
                    "A page in the PDF could not be rendered."
                )

            pages.append(
                RenderedDocumentPage(
                    page_number=index + 1,
                    image_bytes=image_bytes,
                )
            )

        return tuple(pages)

    finally:
        document.close()