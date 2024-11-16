import uvicorn
import os
import shutil

INPUTS_DIRECTORY = "inputs"
OUTPUTS_DIRECTORY = "outputs"

if __name__ == "__main__":
    for directory in [INPUTS_DIRECTORY, OUTPUTS_DIRECTORY]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.makedirs(directory)

    uvicorn.run("api:app", host="0.0.0.0", port=8000, log_level="info", workers=os.cpu_count())