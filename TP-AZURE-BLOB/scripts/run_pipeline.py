import subprocess
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/pipeline.log")
DBT_PROJECT_DIR = "dataops_dbt"
DBT_PROFILES_DIR = str(Path.home() / ".dbt")
DBT = r"C:\Users\lopap\OneDrive\Bureau\Lab_Azurite_Blob\TP-AZURE-BLOB\.venv\Scripts\dbt.exe"

def log(message):
    LOG_FILE.parent.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(full_message + "\n")

def run_command(command, step_name):
    log(f"START : {step_name}")
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.stdout:
        log(result.stdout)
    if result.stderr:
        log(result.stderr)
    if result.returncode != 0:
        log(f"ERROR : {step_name}")
        raise Exception(f"Pipeline failed at : {step_name}")
    log(f"SUCCESS : {step_name}")

def main():
    log("PIPELINE STARTED")

    run_command("python scripts/upload_blob.py", "UPLOAD BLOB")
    run_command("python scripts/load_blob_to_sql.py", "LOAD SQLITE")
    run_command(
        f'"{DBT}" run --project-dir {DBT_PROJECT_DIR} --profiles-dir "{DBT_PROFILES_DIR}"',
        "DBT RUN"
    )
    run_command(
        f'"{DBT}" test --project-dir {DBT_PROJECT_DIR} --profiles-dir "{DBT_PROFILES_DIR}"',
        "DBT TEST"
    )

    log("PIPELINE FINISHED")

if __name__ == "__main__":
    main()