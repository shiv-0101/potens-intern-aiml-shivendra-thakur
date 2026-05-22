import uvicorn
import subprocess
import sys

def run_api():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

def run_ui():
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "app/ui/streamlit_app.py",
        "--server.port", "8501"
    ])

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"

    if mode == "api":
        run_api()
    elif mode == "ui":
        run_ui()
    elif mode == "ingest":
        from app.ingestion.pipeline import run_ingestion_pipeline
        result = run_ingestion_pipeline()
        print(result)
    else:
        print("Usage: python run.py [api|ui|ingest]")