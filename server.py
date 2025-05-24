import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException, File, Query
from fastapi.responses import FileResponse
from emailer import send_workflow_error_email_batch
from classify import classify

app = FastAPI()

@app.post("/classify/")
async def classify_logs(file: UploadFile = File(...), email: str = Query(None)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")
    
    try:
        # Read the uploaded CSV
        df = pd.read_csv(file.file)
        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'log_message' columns.")
        
        # Classify logs
        predictions = classify(list(zip(df["source"], df["log_message"])))

        # Append new columns
        df["target_label"] = [p["target_label"] for p in predictions]
        df["used_method"] = [p["used_method"] for p in predictions]
        df["confidence"] = [p["confidence"] for p in predictions]

        print("Dataframe:",df.to_dict())

        # Optional: Batch email alerts for Workflow Errors
        if email:
            workflow_errors = df[df["target_label"] == "Workflow Error"]
            if not workflow_errors.empty:
                send_workflow_error_email_batch(workflow_errors, email)

        # Save the modified file
        output_file = "resources/output.csv"
        df.to_csv(output_file, index=False)
        print("File saved to output.csv")
        return FileResponse(output_file, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()
        # # Clean up if the file was saved
        # if os.path.exists("output.csv"):
        #     os.remove("output.csv")