
import subprocess
import sys
import os
import time

log_file_path = "portfolio_analysis_output/uvicorn_output.log"
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

with open(log_file_path, "w") as log_file:
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.backend_projeto.main:app", "--host", "0.0.0.0", "--port", "8001"],
        stdout=log_file,
        stderr=log_file,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP # For Windows
    )
print(f"Uvicorn server started with PID: {process.pid}. Output redirected to {log_file_path}")
print("Giving the server some time to start...")
time.sleep(20) # Give the server 20 seconds to start
