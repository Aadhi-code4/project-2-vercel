import os
import httpx
import json
from dotenv import load_dotenv  
from app.utils.function_calls import function_call
from app.utils.function import * 
from app.utils.save_files import * 
import logging
    
# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s %(threadName)s %(message)s",
    encoding="utf-8")
# Get API Token
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable not set")

# OpenAI Proxy API URLs
URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

# Set API Headers
headers = {
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
    "Content-Type": "application/json",
}

async def main(task: str):
    """ Sends a request to OpenAI proxy and returns the response. """
    logging.info(f"📡 Sending request: {task}")
    
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        try:
            response = await client.post(
                URL,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "You are an intelligent assistant.Your job is to selects the correct function to call based on a given user query. Below is a list of available functions and their descriptions.and also some data will be provided to you like in 'json' 'markdowm' you may want to provide them to the function"},
                        {"role": "user", "content": task}
                    ],
                    "tools": function_call,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()  

            # Parse the JSON response
            response_json = response.json()
            logging.info(f"✅ API Response: {json.dumps(response_json, indent=2)}")

            return response_json

        except httpx.HTTPStatusError as http_err:
            logging.error(f"🚨 HTTP Error {http_err.response.status_code}: {http_err.response.text}")
            return {"error": f"HTTP Error {http_err.response.status_code}"}

        except Exception as e:
            logging.error(f"❌ API request failed: {e}")
            return {"error": str(e)}

async def chatgpt(query, file_loc):
    """Processes the chat request and handles function calls if needed."""
    result = await main(query)

    if "choices" not in result or not isinstance(result["choices"], list) or len(result["choices"]) == 0:
        logging.error(f"❌ Unexpected API response structure: {result}")
        return {"error": "Unexpected API response format"}

    message = result["choices"][0].get("message", {})
    logging.info(f"🔍 Processed message: {message}")

    if "tool_calls" in message:
        function_name = message["tool_calls"][0]["function"]["name"]
        function_args = json.loads(message["tool_calls"][0]["function"]["arguments"])
        logging.info(f"🔧 Function Call: {function_name}, Args: {function_args}")  
                           
    try:
        
        if function_name == "vscode_code_s":
            response= vscode_code_s()
            logging.info(f"in if condition response:{response}")
            return response
        
        elif function_name == "send_httpie_request":
            response = await send_httpie_request(
                url=function_args["url"], email=function_args["email"]
            )
            return(response)
        
        elif function_name == "format_and_hash":
            response = await format_and_hash(file_path=file_loc)
            return(response)
        
        elif function_name == "calculate_formula":
            response = await calculate_formula(
                sheet_type=function_args["sheet_type"], formula=function_args["formula"]
            )
            return(response)
        
        elif function_name == "extract_hidden_value_from_string":
            if file_loc is not None:
                response = await extract_hidden_value_from_string(html_input=file_loc,is_file="True")
            else:
                response = await extract_hidden_value_from_string(html_input=function_args["html_input"],is_file="False")
            return(response)
        
        elif function_name == "count_weekdays":
            response = count_weekdays(
                day_of_week=function_args["day_of_week"],
                start_date=function_args["start_date"],
                end_date=function_args["end_date"]
            )
            return(response)
        
        elif function_name == "read_answer_column":
            response = await read_answer_column(
                zip_file_path=file_loc, column=function_args["column"]
            )
            return response
        
        elif function_name == "sort_json_array":
            response = sort_json_array(
                json_array=function_args["json_array"],
                first=function_args["first"],
                second=function_args["second"]
            )
            return(response)
            
        elif function_name == "convert_txt_to_json_hash":
            response = await convert_txt_to_json_hash(file_path=file_loc)
            return(response)

        elif function_name == "sum_data_value":#11
            if file_loc:
                response = await sum_data_value(input_data=file_loc,is_file=True)
            else:
                response = await sum_data_value(input_data=function_args["input_data"],is_file=False)
            
            return(response)
        
        elif function_name == "process_files_and_sum_symbols":#12
            response =  await process_files_and_sum_symbols(zip_file_path=file_loc,target_symbols=function_args["target_symbols"])
            return(response)

        elif function_name == "commit_and_push_file":#13
            response = await commit_and_push_file(file_name=function_args["file_name"],file_content=function_args["file_content"])
            return response
        
        elif function_name == "process_zipped_file":#14
            response = await process_zipped_file(zip_file_path=file_loc)
            return(response)

        elif function_name == "process_zip_and_calculate_size":#15
            response = await process_zip_and_calculate_size(zip_file_path=file_loc, min_size=function_args["min_size"], date_threshold=function_args["date_threshold"])
            return(response)
        
        elif function_name == "process_zip_and_rename":#16
            response = await process_zip_and_rename(zip_file_path=file_loc)
            return(response)
        
        elif function_name == "compare_files_in_zip":
            response = await compare_files_in_zip(zip_file_path=file_loc)
            return(response)
        
        elif function_name == "get_total_sales_sql":
            response = get_total_sales_sql(ticket_type=function_args["ticket_type"])
            return(response)
     
        elif function_name=="fetch_markdown":#1
            response = await fetch_markdown(task=function_args["task"])
            return response
        
        elif function_name=="compress_image_to_base64":#2
            file_path=url_download_file(function_args["file_path"])
            response = await compress_image_to_base64(image_path=file_path)
            # response = await compress_image_to_base64(image_path=file_loc)
            return response
        
        elif function_name == "generate_hash":#4
            response= generate_hash(email=function_args["email"])
            return(response)

        elif function_name =="count_light_pixels":
            file_path=url_download_file(function_args["file_path"])
            response = count_light_pixels(image_path=file_path)
            return(response)
        
        #Serverless hosting: Vercel
        
        elif function_name =="push_github_action":
            # response = push_github_action(email,github_username,repo_name,github_token)
            return(response)
        
        elif function_name =="push_docker_image":
            response = push_docker_image(image_name=function_args["image_name"])
            return(response)
        
        #CORS: Cross-Origin Resource Sharing
        #Make sure you enable CORS to allow GET requests from any origin.
        # What is the API URL endpoint for FastAPI? It might look like: http://127.0.0.1:8000/api
        
        elif function_name =="run_llamafile_with_ngrok":
            response = run_llamafile_with_ngrok()
            return(response)
#ga3
        elif function_name == "fetch_function":
            response = await fetch_function(task=function_args["task"])
            return response
        
        elif function_name == "count_tokens":
            response = count_tokens(text=function_args["text"])
            return response
        
        elif function_name == "create_openai_request":
            if file_loc is not None:
                response = create_openai_request(image_path_or_base64=file_loc,is_file=True)
                return response
            else:
                # file_path = url_download_file(function_args["image_path_or_base64"])
                response = create_openai_request(image_path_or_base64=function_args["image_path_or_base64"],is_file=False)
                return response
        
        elif function_name == "create_embedding_json":
            response = create_embedding_json(value1=function_args["value1"],value2=function_args["value2"])
            return response
#GA4       
        elif function_name ==  "fetch_cricinfo_ducks":
            response = await fetch_cricinfo_ducks(page_number=function_args["page_number"])
            return response
        
        elif function_name == "extract_top_25_movies":
            response = await extract_top_25_movies(url=function_args["url"],start=function_args["start"],end=function_args["end"])
            return response
        #3Scraping emarketer
#What is the URL of your API endpoint?
        
        elif function_name == "fetch_bbc_weather_summary":
            response = await fetch_bbc_weather_summary(required_city=function_args["required_city"])
            return response
        
        elif function_name == "get_max_latitude":
            response = await get_max_latitude(country=function_args["country"],city=function_args["city"])
            return response
        
        elif function_name == "fetch_hacker_news_post":
            response = await fetch_hacker_news_post(min_points=function_args["min_points"])
            return response
#7Emerging Developer Talent for CodeConnect

#8Scheduled Scraping with GitHub Actions

        elif function_name == "compute_total_subject_marks":
            
            response = extract_and_calculate(
                pdf_path=file_loc,
                start_group=function_args["start_group"],
                end_group=function_args["end_group"],
                subject_filter=function_args["subject_filter"],
                total_subject_mark=function_args["total_subject_mark"],
                min_mark=function_args["min_mark"]
                )
            return response
#10
#Ga5
        elif function_name == "process_file":
            response = process_file(file_path=file_loc,product=function_args["product"],country=function_args["country"],filter_date=function_args["filter_date"])
            return response

        elif function_name == "count_unique_students_by_id":
            response = count_unique_students_by_id(file_path=file_loc)
            return response

        elif function_name == "count_successful_requests":
            file_path=url_download_file(function_args['url'])
            response = count_successful_requests(file_path=file_path,category=function_args["category"],start_hour=function_args["start_hour"],end_hour=function_args["end_hour"],day=function_args["day"])
            return response

        elif function_name == "process_log":
            file_path=url_download_file(function_args['url'])
            response = process_log(file_path=file_path,category=function_args["category"],target_date=function_args["target_date"])
            return response

        elif function_name == "count_units_sold_in_tokyo":
            response = count_units_sold_in_tokyo(file_path=file_loc,target_city=function_args["target_city"],product=function_args["product"],sales_threshold=function_args["sales_threshold"])
            return response

        elif function_name == "count_key_occurrences":
            response = count_key_occurrences(file_path=file_loc,key_to_count=function_args["key_to_count"])
            return response

        elif function_name == "youtube_transcribe":
            response = youtube_transcribe(start_time=function_args["start_time"],end_time=function_args["end_time"])
            return response
        return{"answer":"No function was found"}

    except TypeError as e:
        if str(e) == "exists: path should be string, bytes, os.PathLike or integer, not NoneType":
            return{"answer":"Error: The file path is None. Please provide a valid file path."}
        else:
            # Re-raise the exception if it's a different TypeError
            return{"answer":f"Error:{e}"}    
    
    except Exception as e:
        if str(e)=="TypeError: 'coroutine' object is not subscriptable":
            raise {"answer":"await is missing or async is missing"}
            #return {"answer":"await is missing or async is missing"}

