import uvicorn
from fastapi import FastAPI, Query, File, UploadFile, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from app.utils.save_files import save_file
from app.models.LLM_response import chatgpt
import logging
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json

# Create FastAPI app instance
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s %(threadName)s %(message)s",
    encoding="utf-8"  
)
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ok")
def read_root():
    return {"message": "Hello from Vercel!"}


@ app.api_route("/Tds_ques/", methods=["POST", "GET"])
async def UI_api_endpoint(
    request: Request,
    question: str = Form(..., description="A question string"),
    file: Optional[UploadFile] = File(None)
):
    try:
        logging.debug(f"API endpoint (Tds_ques) accessed with question: {question}")
        file_path = None
        if file and file.filename:
            logging.debug(f"Received file: {file.filename}")
            file_path = save_file(file)

        # Fetch response from chatgpt
        response = await chatgpt(query=question, file_loc=file_path)
        logging.debug(f"Raw response from ChatGPT: {response}")

        # Ensure response is a dictionary and extract the "answer" field
        try:
            # First, try to parse it as JSON
            response_dict = json.loads(response["answer"])
            
            # If it's still a JSON string inside the "answer" key, try to load again
            if isinstance(response_dict, str):
                try:
                    response_dict = json.loads(response_dict)  # Double-parse if needed
                except json.JSONDecodeError:
                    pass  # If it's not valid JSON inside, move to the next check
            
            parsed_detail = response_dict  # Successfully parsed JSON
            
        except json.JSONDecodeError:
            logging.warning("Response is not valid JSON, treating as a string.")
            
            parsed_detail = response["answer"]
            
        except Exception as e:
            logging.error(f"Error parsing response: {e}")
            parsed_detail = f"Error: {str(e)}"


            
        return templates.TemplateResponse("index.html", {
            "request": request,
            "response": response,  # Properly formatted original response
            "parsed_json": parsed_detail,  # Properly formatted parsed response
            "question": question
        })

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

    
@app.api_route("/api/", methods=["POST", "GET"])
async def api_endpoint(
    question: str = Query(..., description="A question string"),
    file: Optional[UploadFile] = File(None)
):
    try:
        logging.debug(f"API endpoint (/api/) accessed with question: {question}")
        file_path = save_file(file) if file else None
        response = await chatgpt(query=question, file_loc=file_path)
        return response

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

#venv\Scripts\activate 
#python -m app.main

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)