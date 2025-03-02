from kaggle.api.kaggle_api_extended import KaggleApi
import time

# Authenticate
api = KaggleApi()
api.authenticate()

# Define your Kaggle notebook (username/notebook-name)
NOTEBOOK_PATH = "/home/paolo/Desktop/projects/Ludus/ludus_scacchi/Backend/kaggle/"  # Update with your real notebook path

# Initialize and start the notebook execution
print("Starting Kaggle notebook execution...")
kernel = api.kernels_initialize(NOTEBOOK_PATH)
api.kernel_start(NOTEBOOK_PATH)

# Check status in a loop
while True:
    status = api.kernel_status(kernel['id'])
    print(f"Current Status: {status['status']}")
    
    if status['status'] in ["complete", "error"]:
        break  # Stop when execution completes
    
    time.sleep(30)  # Wait before checking again

# Download output if successful
if status['status'] == "complete":
    print("Execution finished. Downloading output files...")
    api.kernel_output(NOTEBOOK_PATH, path="./output")

else:
    print("Notebook execution failed.")
