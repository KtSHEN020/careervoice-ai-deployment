from __future__ import annotations

import fitz
import pytest

from careervoice_ai_web_app.scanned_document import (
    MAX_SCANNED_PDF_PAGES,
    render_pdf_pages,
)


def _create_pdf_bytes(
    *,
    pages: int,
) -> bytes:
    document = fitz.open()

    for page_number in range(pages):
        page = document.new_page()

        page.insert_text(
            (72, 72),
            f"Mock CV page {page_number + 1}",
        )

    content = document.tobytes()
    document.close()

    return content


def test_render_single_pdf_page() -> None:
    pages = render_pdf_pages(
        _create_pdf_bytes(
            pages=1,
        )
    )

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert pages[0].media_type == "image/png"

    assert pages[0].image_bytes.startswith(
        b"\x89PNG"
    )


def test_render_multiple_pdf_pages_in_order() -> None:
    pages = render_pdf_pages(
        _create_pdf_bytes(
            pages=3,
        )
    )

    assert [
        page.page_number
        for page in pages
    ] == [
        1,
        2,
        3,
    ]


def test_empty_pdf_content_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="PDF is empty",
    ):
        render_pdf_pages(b"")


def test_invalid_pdf_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="could not be opened",
    ):
        render_pdf_pages(
            b"this-is-not-a-pdf"
        )


def test_large_scanned_pdf_is_rejected() -> None:
    content = _create_pdf_bytes(
        pages=MAX_SCANNED_PDF_PAGES + 1,
    )

    with pytest.raises(
        ValueError,
        match="supports up to",
    ):
        render_pdf_pages(content)