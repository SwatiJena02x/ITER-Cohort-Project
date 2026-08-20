import os
import csv
import json

from pypdf import PdfReader


# ============================================================
# STAGE 1: DATA INGESTION
# ============================================================

def _read_pdf(path):
    """Extract text from every page of a PDF."""

    reader = PdfReader(path)

    pages_text = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)

    return "\n".join(pages_text)


def _read_plain_text(path):
    """
    Read normal text-based files.

    Works for:
    .md
    .txt
    .py
    """

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.read()


def _read_csv(path):
    """Convert CSV rows into readable text."""

    lines = []

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            row_text = ", ".join(
                f"{key}: {value}"
                for key, value in row.items()
            )

            lines.append(row_text)

    return "\n".join(lines)


def _read_json(path):
    """Read JSON and convert it into readable text."""

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        data = json.load(f)

    return json.dumps(
        data,
        indent=2
    )


def _read_ipynb(path):
    """
    Read Jupyter Notebook.

    Extracts code and markdown cells.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        notebook = json.load(f)

    parts = []

    for cell in notebook.get("cells", []):

        cell_type = cell.get(
            "cell_type",
            ""
        )

        source = cell.get(
            "source",
            []
        )

        if isinstance(source, list):
            text = "".join(source)
        else:
            text = str(source)

        if text.strip():

            parts.append(
                f"[{cell_type} cell]\n{text}"
            )

    return "\n\n".join(parts)


# ============================================================
# FILE TYPE → READER
# ============================================================

READERS = {

    ".pdf": _read_pdf,

    ".md": _read_plain_text,

    ".txt": _read_plain_text,

    ".py": _read_plain_text,

    ".csv": _read_csv,

    ".json": _read_json,

    ".ipynb": _read_ipynb,

}


# ============================================================
# LOAD ONE FILE
# ============================================================

def load_file(path):

    extension = os.path.splitext(path)[1].lower()

    reader = READERS.get(extension)

    if reader is None:

        print(
            f"[SKIP] Unsupported file type: {path}"
        )

        return ""

    try:

        return reader(path)

    except Exception as e:

        print(
            f"[ERROR] Could not read {path}: {e}"
        )

        return ""


# ============================================================
# CHUNKING
# ============================================================

def chunk_text(
    text,
    chunk_size=200,
    overlap=40
):
    """
    Split text into overlapping chunks.

    chunk_size = number of words per chunk
    overlap = number of words repeated
    between consecutive chunks.
    """

    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0

    step = chunk_size - overlap

    while start < len(words):

        chunk_words = words[
            start:start + chunk_size
        ]

        chunks.append(
            " ".join(chunk_words)
        )

        start += step

    return chunks


# ============================================================
# BUILD ALL DOCUMENTS
# ============================================================

def build_documents(
    kb_root="knowledge_base",
    chunk_size=200,
    overlap=40
):
    """
    Walk through knowledge_base/,
    read every supported file,
    chunk the content,
    and return document chunks.
    """

    documents = []

    for dirpath, _, filenames in os.walk(kb_root):

        for filename in filenames:

            full_path = os.path.join(
                dirpath,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                kb_root
            )

            print(
                f"[READ] {relative_path}"
            )

            text = load_file(full_path)

            if not text.strip():
                continue

            chunks = chunk_text(
                text,
                chunk_size=chunk_size,
                overlap=overlap
            )

            for i, chunk in enumerate(chunks):

                documents.append({

                    "id":
                        f"{relative_path}::chunk{i}",

                    "text":
                        chunk,

                    "source":
                        relative_path,

                    "chunk_index":
                        i

                })

    return documents


# ============================================================
# TEST INGESTION + CHUNKING
# ============================================================

if __name__ == "__main__":

    documents = build_documents()

    print()
    print(
        f"Total chunks created: {len(documents)}"
    )

    for document in documents[:3]:

        print("-" * 70)

        print(
            "ID:",
            document["id"]
        )

        print(
            "SOURCE:",
            document["source"]
        )

        print(
            "TEXT:",
            document["text"][:300]
        )

