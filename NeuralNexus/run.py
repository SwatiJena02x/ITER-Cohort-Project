"""
run.py
------
Single command to run both Backend (FastAPI) and Frontend (HTML & Streamlit) together.

Usage:
    python run.py
"""
import os
import sys
import subprocess
import time
import webbrowser

def main():
    print("=" * 65)
    print("Starting Proctoring Risk Scoring System (Backend + Frontend)")
    print("=" * 65)

    cwd = os.path.dirname(os.path.abspath(__file__))

    # 1. Start FastAPI Backend (Port 8000)
    print("[1/3] Starting Backend API (FastAPI) on http://localhost:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=cwd
    )


    # 2. Start HTML Frontend Server (Port 8080)
    html_dir = os.path.join(cwd, "frontend", "html")
    html_proc = None
    if os.path.exists(html_dir):
        print("[2/3] Starting HTML Frontend UI on http://localhost:8080 ...")
        html_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8080", "--directory", html_dir],
            cwd=cwd
        )

    # 3. Start Streamlit App (Port 8501)
    streamlit_app = os.path.join(cwd, "frontend", "streamlit_app.py")
    streamlit_proc = None
    if os.path.exists(streamlit_app):
        print("[3/3] Starting Streamlit Dashboard on http://localhost:8501 ...")
        streamlit_proc = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py",
             "--server.port", "8501", "--server.headless", "true"],
            cwd=cwd
        )

    time.sleep(2)
    print("\n" + "=" * 65)
    print("System Running! Access URLs below:")
    print("   * HTML Frontend UI : http://localhost:8080/index.html")
    print("   * FastAPI Mount UI  : http://localhost:8000/app/index.html")
    print("   * Streamlit UI     : http://localhost:8501")
    print("   * Backend API      : http://localhost:8000")
    print("   * Swagger Docs     : http://localhost:8000/docs")
    print("=" * 65)
    print("Press Ctrl+C to stop all servers.\n")

    try:
        webbrowser.open("http://localhost:8080/index.html")
    except Exception:
        pass

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping all services...")
        backend_proc.terminate()
        if html_proc:
            html_proc.terminate()
        if streamlit_proc:
            streamlit_proc.terminate()

if __name__ == "__main__":
    main()
