from pathlib import Path
from pypdf import PdfReader


def load_pdf(path: Path) -> dict:
    """
    Extract text from a PDF while preserving page information.
    """
    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                {
                    "page": page_number,
                    "text": text,
                }
            )

    full_text = "\n\n".join(
        f"[Page {page['page']}]\n{page['text']}"
        for page in pages
    )

    return {
        "text": full_text,
        "metadata": {
            "source": str(path),
            "file_name": path.name,
            "file_type": "pdf",
            "page_count": len(reader.pages),
        },
        "pages": pages,
    }