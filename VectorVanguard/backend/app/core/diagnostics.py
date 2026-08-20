import shutil
import subprocess
import sys
from pathlib import Path

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.vector_store import collection


def check_python():
    version = sys.version_info
    return (
        version.major == 3
        and version.minor == 12
    )


def check_postgresql():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_alembic():
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "current",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[2],
        )

        return (
            result.returncode == 0
            and "head" in result.stdout
        )

    except Exception:
        return False


def check_ollama():
    try:
        result = subprocess.run(
            [
                "ollama",
                "list",
            ],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    except FileNotFoundError:
        return False


def get_ollama_models():
    try:
        result = subprocess.run(
            [
                "ollama",
                "list",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return []

        models = []

        for line in result.stdout.splitlines()[1:]:
            parts = line.split()

            if parts:
                models.append(parts[0])

        return models

    except FileNotFoundError:
        return []


def check_ollama_model(model_name, installed_models):
    model_base = model_name.split(":")[0]

    for installed in installed_models:
        installed_base = installed.split(":")[0]

        if installed == model_name:
            return True

        if installed_base == model_base:
            return True

    return False


def check_tesseract():
    configured_path = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    return (
        configured_path.exists()
        or shutil.which("tesseract") is not None
    )


def check_chromadb():
    try:
        collection.count()
        return True
    except Exception:
        return False


def check_storage():
    backend_dir = Path(
        __file__
    ).resolve().parents[2]

    storage_dir = backend_dir / "storage"
    chroma_dir = storage_dir / "chroma"

    storage_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    chroma_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        storage_dir.exists()
        and chroma_dir.exists()
    )


def print_result(name, status, details=""):
    symbol = "[OK]" if status else "[FAIL]"

    if details:
        print(
            f"{symbol} {name}: {details}"
        )
    else:
        print(
            f"{symbol} {name}"
        )


def run_diagnostics():
    print("=" * 60)
    print("VectorVanguard Setup Diagnostic")
    print("=" * 60)

    print()
    print(
        f"Python: {sys.version.split()[0]}"
    )

    python_ok = check_python()
    print_result(
        "Python 3.12",
        python_ok,
    )

    postgres_ok = check_postgresql()
    print_result(
        "PostgreSQL",
        postgres_ok,
    )

    alembic_ok = check_alembic()
    print_result(
        "Alembic migration",
        alembic_ok,
    )

    ollama_ok = check_ollama()
    print_result(
        "Ollama",
        ollama_ok,
    )

    installed_models = get_ollama_models()

    print()
    print("Ollama models:")

    required_models = [
        settings.OLLAMA_EMBED_MODEL,
        settings.OLLAMA_VISION_MODEL,
        settings.OLLAMA_LLM_MODEL,
    ]

    ollama_models_ok = True

    for model in required_models:
        model_ok = check_ollama_model(
            model,
            installed_models,
        )

        if not model_ok:
            ollama_models_ok = False

        print_result(
            model,
            model_ok,
        )

    tesseract_ok = check_tesseract()
    print()
    print_result(
        "Tesseract OCR",
        tesseract_ok,
    )

    chroma_ok = check_chromadb()
    print_result(
        "ChromaDB",
        chroma_ok,
    )

    storage_ok = check_storage()
    print_result(
        "Storage directories",
        storage_ok,
    )

    overall = all(
        [
            python_ok,
            postgres_ok,
            alembic_ok,
            ollama_ok,
            ollama_models_ok,
            tesseract_ok,
            chroma_ok,
            storage_ok,
        ]
    )

    print()
    print("=" * 60)

    if overall:
        print(
            "[SUCCESS] VectorVanguard environment looks healthy."
        )
    else:
        print(
            "[WARNING] One or more environment checks failed."
        )

    print("=" * 60)

    return overall


if __name__ == "__main__":
    success = run_diagnostics()

    sys.exit(
        0 if success else 1
    )