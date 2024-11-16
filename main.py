import uvicorn
import os
import shutil

INPUTS_DIRECTORY = "inputs"
OUTPUTS_DIRECTORY = "outputs"
for directory in [INPUTS_DIRECTORY, OUTPUTS_DIRECTORY]:
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

if __name__ == "__main__":
    uvicorn.run("api:app", port=8000, log_level="info", works=os.cpu_count())