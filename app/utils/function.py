import pdfplumber
import pandas as pd
import logging
from fuzzywuzzy import fuzz
from collections import defaultdict
import gzip
from typing import Dict
from faster_whisper import WhisperModel
import xml.etree.ElementTree as ET
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from urllib.parse import urlencode
import aiohttp
import asyncio
import requests
import pandas as pd
import io
import base64
import mimetypes
import tiktoken
import time
import os
import re
import shutil
import hashlib
import zipfile
import logging
import subprocess
import json
import itertools
import platform
import aiofiles
import csv
import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import pytz
import asyncio
import numpy as np
from chardet import detect
import numpy as np
from PIL import Image
import colorsys
import logging
import platform

from dotenv import load_dotenv
load_dotenv()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    logging.error("AIPROXY_TOKEN environment variable not set")
    raise ValueError("AIPROXY_TOKEN environment variable not set")

# OpenAI Proxy API URLs
URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

# Set API Headers
headers = {
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
    "Content-Type": "application/json",
}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(filename)s %(threadName)s %(message)s",
    encoding="utf-8"  
)
extract_path = "app/data/extracted_files/"

def vscode_code_s():  # 1
    ans = "Version:Code 1.96.4 (cd4ee3b1c348a13bafd8f9ad8060705f6d4b9cba, 2025-01-16T00:16:19.038Z)OS Version:Windows_NT x64 10.0.22631"
    
    response = {"answer": ans}
    logging.info(json.dumps({
        "function_name": "vscode_code_s",
        "response": response
    }, indent=2))
    return response

async def send_httpie_request(url: str, email: str):  # 2
    headers = {
        "User-Agent": "HTTPie/3.2.1",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params={"email": email}, headers=headers)
            response.raise_for_status()

            json_response = response.json()
            answer =json_response
            response_data = {"answer": json.dumps(answer)}

            logging.info(json.dumps({
                "function_name": "send_httpie_request",
                "response": response_data
            }, indent=2))

            return response_data

    except httpx.HTTPStatusError as e:
        error_message = json.dumps({
            "answer": f"HTTP error {e.response.status_code}: {e.response.text}"
        }, indent=2)

    except httpx.RequestError as e:
        error_message = json.dumps({
            "answer": f"Request failed: {str(e)}"
        }, indent=2)

    logging.warning(json.dumps({
        "function_name": "send_httpie_request",
        "response": error_message
    }, indent=2))

    return error_message

async def format_and_hash(file_path: str):#3
    """Formats a file using Prettier and returns its SHA-256 hash, then deletes the file."""
    
    file_path = os.path.abspath(file_path)  # Normalize path
    logging.debug(f"📂 Checking file: {file_path}")

    if not os.path.exists(file_path):
        return {"answer": f"Error: File not found - {file_path}"}

    # Ensure npx is installed
    if shutil.which("npx") is None:
        error_message = "Error: npx is not installed or not in PATH."
        logging.error(f"❌ format_and_hash: {error_message}")
        return {"answer": error_message}

    try:
        if platform.system() == "Windows":
            # Windows: Use subprocess.run synchronously (asyncio subprocess is not supported)
            command = ["npx", "-y", "prettier@3.4.2", file_path]
            logging.debug(f"📤 Running command (Windows): {command}")

            result = subprocess.run(command, capture_output=True, text=True, shell=True)

            if result.returncode != 0:
                error_message = f"Prettier Error: {result.stderr.strip()}"
                logging.warning(f"⚠️ format_and_hash failed: {error_message}")
                return {"answer": error_message}

            formatted_content = result.stdout

        else:
            # Linux: Use asyncio subprocess
            command = ["npx", "-y", "prettier@3.4.2", file_path]
            logging.debug(f"📤 Running command (Linux): {command}")

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_message = f"Prettier Error: {stderr.decode().strip()}"
                logging.warning(f"⚠️ format_and_hash failed: {error_message}")
                return {"answer": error_message}

            formatted_content = stdout.decode()

        # Compute SHA-256 hash
        file_hash = hashlib.sha256(formatted_content.encode()).hexdigest()

        # Match Linux `sha256sum` output format
        if platform.system() != "Windows":
            file_hash += "  -"

        logging.info(f"✅ format_and_hash success: {file_hash}")
        return {"answer": file_hash}

    except Exception as e:
        logging.error(f"❌ format_and_hash exception: {e}", exc_info=True)
        return {"answer": f"Exception: {str(e)}"}

    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"🗑️ Deleted file: {file_path}")
        except Exception as e:
            logging.error(f"❌ Failed to delete {file_path}: {e}", exc_info=True)

async def calculate_formula(sheet_type: str, formula: str):#4,5
    """Processes Excel or Google Sheets formulas and returns computed results as a string."""

    try:
        if sheet_type == "Excel":
            data_match = re.search(r"SORTBY\(\{([\d,]+)\},", formula)
            sort_order_match = re.search(r"SORTBY\(.*\{([\d,]+)\}\)", formula)
            range_match = re.search(r"TAKE\(.*?,\s*(\d+),\s*(\d+)\)", formula)

            if not data_match or not sort_order_match or not range_match:
                raise ValueError("Invalid formula format")

            data = np.array([int(num) for num in data_match.group(1).split(',')])
            sort_order = np.array([int(num) for num in sort_order_match.group(1).split(',')])
            start, end = map(int, range_match.groups())

            sorted_data = data[np.argsort(sort_order)]
            result = str(int(np.sum(sorted_data[start - 1:end])))  # Convert to Python int

            logging.info(json.dumps({
                "function_name": "calculate_formula",
                "sheet_type": sheet_type,
                "response": result
            }, indent=2))

            return {"answer": result}

        if sheet_type == "Google Sheets":
            sequence_match = re.search(r'SEQUENCE\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', formula)
            array_constrain_match = re.search(r'ARRAY_CONSTRAIN\(.*?,\s*(\d+),\s*(\d+)\)', formula)

            if not sequence_match or not array_constrain_match:
                raise ValueError("Invalid formula format")

            rows, cols, start, step = map(int, sequence_match.groups())
            numbers = re.findall(r"\d+", formula)
            sr, er = (int(numbers[-2]) - 1, int(numbers[-1])) if len(numbers) >= 2 else (None, None)

            sequence = np.array([[start + r * step + c * step for c in range(cols)] for r in range(rows)])
            result = str(int(np.sum(sequence[sr, :er])))  # Convert to Python int

            logging.info(json.dumps({
                "function_name": "calculate_formula",
                "sheet_type": sheet_type,
                "response": result
            }, indent=2))

            return {"answer": result}

    except ValueError as ve:
        error_message = f"ValueError: {str(ve)}"
    except Exception as e:
        error_message = f"Exception: {str(e)}"

    logging.warning(json.dumps({
        "function_name": "calculate_formula",
        "sheet_type": sheet_type,
        "response": error_message
    }, indent=2))

    return {"answer": error_message}

async def extract_hidden_value_from_string(html_input, is_file=True):#6
    """Extracts the value of the first hidden input field from an HTML string or file."""
    
    function_name = "extract_hidden_value_from_string"
    logging.info(f"🔍 Starting function: {function_name}")

    error_message = None
    extracted_value = None

    try:
        if isinstance(is_file, str):  # Convert string to boolean
            is_file = is_file.lower() == "true"

        if is_file and isinstance(html_input, str):
            if not os.path.exists(html_input):  # Check if file exists
                error_message = "File not found"
                raise FileNotFoundError(error_message)
            
            logging.info(f"📂 Reading file: {html_input}")
            async with aiofiles.open(html_input, 'r', encoding='utf-8') as file:
                html_content = await file.read()
        else:
            html_content = html_input  # Direct HTML string

        soup = BeautifulSoup(html_content, "html.parser")
        hidden_inputs = soup.find_all("input", {"type": "hidden"})
        extracted_value = hidden_inputs[0].get("value", "No value found") if hidden_inputs else "No hidden input found"

        logging.info(f"✅ Extracted hidden value: {extracted_value}")

    except FileNotFoundError:
        logging.error(f"❌ File not found: {html_input}")
        error_message = "File not found"
    except Exception as e:
        logging.error(f"❌ Error extracting hidden value: {str(e)}")
        error_message = f"Error: {e}"
    
    finally:
        if is_file and isinstance(html_input, str) and os.path.exists(html_input):
            try:
                os.remove(html_input)
                logging.info(f"🗑️ Deleted file: {html_input}")
            except Exception as e:
                logging.error(f"❌ Failed to delete file: {html_input}, Error: {str(e)}")

    # Prepare response
    response = extracted_value if extracted_value else error_message

    log_level = logging.INFO if extracted_value else logging.WARNING
    log_data = {
        "function_name": function_name,
        "response": response
    }
    logging.log(log_level, json.dumps(log_data, indent=2))

    return {"answer": response}

def count_weekdays(day_of_week: str, start_date: str, end_date: str):#7
    """Counts occurrences of a weekday between two dates."""
    try:
        day_of_week = day_of_week.rstrip("s").title()  
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if day_of_week not in days_of_week:
            raise ValueError(f"Invalid day_of_week: {day_of_week}. Expected one of {days_of_week}")

        day_index = days_of_week.index(day_of_week)
        count = sum(1 for _ in range((end_date - start_date).days + 1) if (start_date + timedelta(_)).weekday() == day_index)

        logging.info(json.dumps({
            "function_name": "count_weekdays",
            "response": str(count)
        }, indent=2))

        return {"answer": str(count)}

    except ValueError as ve:
        error_message = f"ValueError: {str(ve)}"
    except Exception as e:
        error_message = f"Error: {str(e)}"

    logging.warning(json.dumps({
        "function_name": "count_weekdays",
        "response": error_message
    }, indent=2))

    return {"answer": error_message}

async def read_answer_column(zip_file_path: str, column: str):#8
    """Reads a specific column from extract.csv inside a ZIP file and returns the first value."""
    
    logging.info("🔍 Starting function: read_answer_column")
    try:
        error_message = None
        extracted_value = None
        zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
        output_folder = os.path.join(extract_path, zip_file_name)
    except Exception as e:
        return {"answer":"error file is required to calculate the answer"}
    
    try:
        logging.info(f"📂 Creating extraction directory: {output_folder}")
        os.makedirs(output_folder, exist_ok=True)

        # Extract ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        logging.info(f"📂 Extracted ZIP contents to: {output_folder}")

        # Locate CSV file
        csv_file_path = os.path.join(output_folder, "extract.csv")
        if not os.path.exists(csv_file_path):
            error_message = "extract.csv not found!"
            raise FileNotFoundError(error_message)

        # Read CSV
        async with aiofiles.open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
            content = await csv_file.read()  # ✅ Await reading the file properly
            csv_reader = csv.DictReader(content.splitlines())  # ✅ Correctly process CSV
            first_row = next(csv_reader, None)
            extracted_value = first_row[column] if first_row and column in first_row else "Missing value"

        logging.info(f"✅ Extracted value: {extracted_value}")

    except FileNotFoundError:
        error_message = "ZIP file or extract.csv not found!"
        logging.error(f"❌ {error_message}")
        return {"answer": error_message}
    except Exception as e:
        error_message = str(e)
        logging.error(f"❌ Exception: {error_message}")
        return {"answer": error_message}

    finally:
        # Clean up extracted files
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
            logging.info(f"🗑️ Deleted ZIP file: {zip_file_path}")
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
            logging.info(f"🗑️ Deleted extraction folder: {output_folder}")

    # Return JSON response in expected format
    final_response = {"answer": error_message if error_message else extracted_value}
    log_level = logging.WARNING if error_message else logging.INFO
    logging.log(log_level, final_response)

    return final_response

def sort_json_array(json_array: list, first: str, second: str):#9
    """Sorts a JSON array by two keys and returns the sorted array in JSON format."""

    logging.info("🔍 Starting function: sort_json_array")

    try:
        logging.info(f"📥 Received JSON array: {json.dumps(json_array, indent=2)}")

        # Sort by primary key (first) and secondary key (second)
        sorted_array = sorted(
            json_array,
            key=lambda x: (x.get(first, float('inf')), str(x.get(second, "")).lower())
        )

        logging.info(f"✅ Sorted output: {json.dumps(sorted_array, indent=2)}")

        # ✅ Return JSON with the sorted list as an actual JSON array
        return {"answer": json.dumps(sorted_array)} # Fix applied here

    except Exception as e:
        error_message = f"Error: {e}"
        logging.error(json.dumps({
            "function_name": "sort_json_array",
            "error": error_message
        }, indent=2))
        return {"answer": error_message}

async def convert_txt_to_json_hash(file_path: str):#10
    """Converts a .txt file with key=value pairs into a JSON object, hashes it, and returns the SHA-256 hash."""
    error_message = None  # Initialize error_message

    try:
        logging.info(json.dumps({
            "function_name": "convert_txt_to_json_hash",
            "file_path": file_path
        }, indent=2))

        json_object = {}

        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            async for line in file:
                line = line.strip()
                if not line:
                    continue
                
                if "=" in line:
                    key, value = line.split("=", 1)
                    json_object[key.strip()] = value.strip()

        json_string = json.dumps(json_object, separators=(',', ':'))
        json_hash = hashlib.sha256(json_string.encode()).hexdigest()

        logging.info(json.dumps({
            "function_name": "convert_txt_to_json_hash",
            "json_hash": json_hash
        }, indent=2))

        return {"answer": str(json_hash)}

    except FileNotFoundError:
        error_message = f"File not found: {file_path}"
    except Exception as e:
        error_message = str(e)

    finally:
        if file_path is not None and os.path.exists(file_path):
            os.remove(file_path)
            logging.info(json.dumps({
                "function_name": "convert_txt_to_json_hash",
                "file_deleted": file_path
            }, indent=2))

    if error_message:  # Return error if it was caught
        logging.error(json.dumps({
            "function_name": "convert_txt_to_json_hash",
            "error": error_message
        }, indent=2))
        return {"answer": error_message}

async def sum_data_value(input_data, is_file=True):#11
    """Sums the values of all <div class='foo' data-value='...'> elements in an HTML file or string."""
    error_message = None  # Initialize error_message

    try:
        logging.info(json.dumps({
            "function_name": "sum_data_value",
            "input_data": input_data if not is_file else "File path provided",
            "is_file": is_file
        }, indent=2))

        if is_file and isinstance(input_data, str):
            async with aiofiles.open(input_data, 'r', encoding='utf-8') as file:
                html_content = await file.read()
        else:
            html_content = input_data

        soup = BeautifulSoup(html_content, 'html.parser')
        divs_with_foo_class = soup.select('div.foo')

        total = sum(
            float(div.get('data-value')) for div in divs_with_foo_class
            if div.get('data-value') and re.match(r"^\d+(\.\d+)?$", div.get('data-value'))
        )

        logging.info(json.dumps({
            "function_name": "sum_data_value",
            "total_sum": total
        }, indent=2))

        return {"answer": str(int(total))}

    except FileNotFoundError:
        error_message = "File not found"
    except Exception as e:
        error_message = f"An error occurred: {e}"

    finally:
        if is_file and isinstance(input_data, str) and os.path.exists(input_data):
            os.remove(input_data)
            logging.info(json.dumps({
                "function_name": "sum_data_value",
                "file_deleted": input_data
            }, indent=2))

    if error_message:  # Return error if it was caught
        logging.error(json.dumps({
            "function_name": "sum_data_value",
            "error": error_message
        }, indent=2))
        return {"answer": error_message}

def detect_file_encoding(file_path):#12
    """Detect file encoding using chardet."""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(1024)  # Read the first 1KB to detect encoding
        detected = detect(raw_data)
        return detected['encoding'] if detected['encoding'] else 'utf-8'
    except Exception as e:
        logging.error(f"❌ Encoding detection failed for {file_path}: {e}")
        return 'utf-8'  # Fallback encoding

async def process_files_and_sum_symbols(zip_file_path, target_symbols):#12
    """Processes CSV and TXT files from a ZIP and sums values of given symbols, handling multiple encodings."""
    
    # ✅ Validate input
    if not zip_file_path:
        logging.error("❌ Error: zip_file_path is None")
        return({"answer": "Error: ZIP file path is missing"})

    total_sum = 0
    zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
    output_folder = os.path.join("app/data/extracted_files", zip_file_name)

    logging.info(json.dumps({
        "function_name": "process_files_and_sum_symbols",
        "action": "Extracting ZIP",
        "zip_file": zip_file_path
    }, indent=2))

    try:
        # ✅ Ensure the output folder exists (cross-platform)
        os.makedirs(output_folder, exist_ok=True)

        # ✅ Extract ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        logging.info(f"✅ Successfully extracted ZIP: {zip_file_path}")

        # ✅ Process extracted files
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)

            # Determine encoding dynamically
            detected_encoding = detect_file_encoding(file_path)
            
            # Determine delimiter (',' for CSV, '\t' for TXT)
            delimiter = ',' if filename.endswith('.csv') else '\t'

            logging.info(f"📄 Processing {filename} | Encoding: {detected_encoding} | Delimiter: {repr(delimiter)}")

            try:
                with open(file_path, 'r', encoding=detected_encoding, errors="replace") as file:
                    reader = csv.reader(file, delimiter=delimiter)
                    for row in reader:
                        if len(row) >= 2 and row[0].strip() in target_symbols:
                            try:
                                total_sum += int(row[1].strip())
                            except ValueError:
                                logging.warning(f"⚠️ Invalid number in {filename}: {row[1].strip()}")
            except Exception as e:
                logging.error(f"❌ Error processing file {filename}: {e}")

    except zipfile.BadZipFile:
        logging.error("❌ Corrupt ZIP file")
    except FileNotFoundError:
        logging.error("❌ ZIP file not found")
    except Exception as e:
        logging.error(f"❌ Error extracting ZIP: {e}")
    finally:
        # ✅ Cleanup extracted files
        shutil.rmtree(output_folder, ignore_errors=True)

        # ✅ Delete ZIP file after processing
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
            logging.info(f"🗑️ Deleted ZIP file: {zip_file_path}")

    # ✅ Final log message
    logging.info(json.dumps({
        "function_name": "process_files_and_sum_symbols",
        "action": "Completed",
        "total_sum": str(total_sum)  # Ensure it's a string
    }, indent=2))

    # ✅ Ensure correct return format
    return {"answer": str(total_sum)}

#13
async def run_git_command(command: list, cwd: str):
    """Run a Git command and return the output."""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e.stderr}")
        raise Exception(f"Git error: {e.stderr}")
#13
async def commit_and_push_file(file_name: str, file_content: str) -> str:
    """Takes a file name and content, commits the changes, and pushes to the repo."""
    GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", "./repo")
    GIT_REMOTE_URL = os.getenv("GIT_REMOTE_URL", "git@github.com:user/repo.git")
    file_path = os.path.join(GIT_REPO_PATH, file_name)

    try:
        # Clone the repo if it doesn't exist
        if not os.path.exists(GIT_REPO_PATH):
            await run_git_command(["git", "clone", GIT_REMOTE_URL, GIT_REPO_PATH], cwd="./")

        # Pull latest changes
        await run_git_command(["git", "pull", "origin", "main"], cwd=GIT_REPO_PATH)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(file_content)
        logging.info(f"File {file_name} written successfully.")

        # Check if there are changes
        status_output = await run_git_command(["git", "status", "--porcelain"], cwd=GIT_REPO_PATH)
        if not status_output:
            logging.info("No changes detected. Skipping commit and push.")
            return{"answer": f"{GIT_REMOTE_URL.replace('.git', '/tree/main/')}"}

        # Add, commit, and push
        await run_git_command(["git", "add", file_name], cwd=GIT_REPO_PATH)
        await run_git_command(["git", "commit", "-m", f"Added {file_name}"], cwd=GIT_REPO_PATH)
        await run_git_command(["git", "push", "origin", "main"], cwd=GIT_REPO_PATH)

        logging.info(f"File {file_name} committed and pushed successfully.")
        return {"answer": f"{GIT_REMOTE_URL.replace('.git', '/main/').replace("github","raw.githubusercontent")}{file_name}"}
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise Exception(str(e))
    finally:
        # Cleanup: Delete the local repo folder
        shutil.rmtree(GIT_REPO_PATH, ignore_errors=True)
        logging.info(f"🗑️ Deleted local repo: {GIT_REPO_PATH}")

async def process_zipped_file(zip_file_path):#14
    """
    Extracts a ZIP file, replaces 'IITM' with 'IIT Madras' in text files,
    computes SHA-256 checksum, and cleans up extracted files.
    """
    logging.info(json.dumps({"function_name": "process_zipped_file", "action": "Start processing", "file": zip_file_path}))

    # ✅ Validate input
    if not zip_file_path:
        logging.error(json.dumps({"function_name": "process_zipped_file", "action": "Error", "message": "ZIP file path is missing"}))
        return {"answer": "None"}
    
    output_folder = None
    checksum = "None"
    
    try:
        zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
        output_folder = os.path.join(extract_path, zip_file_name)
        os.makedirs(output_folder, exist_ok=True)

        logging.info(json.dumps({"function_name": "process_zipped_file", "action": "Extracting ZIP", "file": zip_file_path}))
        
        # ✅ Extract ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        
        # ✅ Replace "IITM" with "IIT Madras" in text files
        for root, _, files in os.walk(output_folder):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()

                    updated_content = re.sub(r"(?i)iitm", "IIT Madras", content)

                    with open(file_path, 'w', encoding='utf-8', newline='') as file:
                        file.write(updated_content)
                    
                    logging.info(json.dumps({"function_name": "process_zipped_file", "action": "Updated file", "file": file_name}))
                
                except Exception as e:
                    logging.error(json.dumps({
                        "function_name": "process_zipped_file",
                        "action": "Skipping file",
                        "file": file_name,
                        "error": str(e)
                    }))

        # ✅ Compute SHA-256 checksum (cross-platform)
        try:
            hash_obj = hashlib.sha256()
            for root, _, files in os.walk(output_folder):
                for file_name in sorted(files):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'rb') as f:
                        while chunk := f.read(8192):
                            hash_obj.update(chunk)
            checksum = hash_obj.hexdigest() + "  -"  # Match expected output format

            logging.info(json.dumps({"function_name": "process_zipped_file", "action": "Checksum computed", "checksum": checksum}))

        except Exception as e:
            logging.error(json.dumps({"function_name": "process_zipped_file", "action": "Error computing checksum", "error": str(e)}))
    
    except FileNotFoundError:
        logging.error(json.dumps({"function_name": "process_zipped_file", "action": "File not found", "file": zip_file_path}))
    
    except Exception as e:
        logging.error(json.dumps({"function_name": "process_zipped_file", "action": "Error processing file", "error": str(e)}))
    
    finally:
        # ✅ Ensure output_folder exists before trying to delete it
        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder, ignore_errors=True)
            logging.info(json.dumps({"function_name": "process_zipped_file", "action": "Deleted extracted folder", "folder": output_folder}))

        # ✅ Ensure ZIP file is deleted
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
            logging.info(json.dumps({"function_name": "process_zipped_file", "action": "Deleted ZIP file", "file": zip_file_path}))

    return {"answer": str(checksum)}

async def process_zip_and_calculate_size(zip_file_path, min_size, date_threshold):  # 15
    """Extracts a ZIP file, filters files based on size and date, and computes total size."""

    if not zip_file_path:
        logging.error(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Error", "message": "ZIP file path is missing"}))
        return {"answer": "Error: ZIP file path is missing."}

    output_folder = None  # Ensure variable is always initialized

    try:
        zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
        output_folder = os.path.join(extract_path, zip_file_name)

        os.makedirs(output_folder, exist_ok=True)
        logging.info(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Extracting ZIP", "file": zip_file_path}))

        # ✅ Extract ZIP file while preserving timestamps
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                extracted_path = os.path.join(output_folder, zip_info.filename)

                if zip_info.is_dir():  # Skip directories
                    continue

                os.makedirs(os.path.dirname(extracted_path), exist_ok=True)
                zip_ref.extract(zip_info, output_folder)

                # ✅ Preserve original timestamps
                zip_mtime = datetime(*zip_info.date_time, tzinfo=timezone.utc).timestamp()
                os.utime(extracted_path, (zip_mtime, zip_mtime))

        # ✅ Convert date_threshold to UTC timezone-aware datetime
        try:
            date_format = "%a, %d %b, %Y, %I:%M %p IST"
            ist = pytz.timezone("Asia/Kolkata")  # India Standard Time
            threshold_datetime = ist.localize(datetime.strptime(date_threshold, date_format)).astimezone(timezone.utc)
            logging.info(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Parsed date_threshold", "threshold": str(threshold_datetime)}))
        except Exception as e:
            logging.error(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Invalid date format", "error": str(e)}))
            return{"answer": "Error: Invalid date format."}

        total_size = 0
        for root, _, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if not os.path.isfile(file_path) or file.startswith("."):  # ✅ Skip hidden/system files
                    continue

                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime, timezone.utc)

                # ✅ Correct filtering by size and UTC-adjusted date
                if file_size >= min_size and file_mtime >= threshold_datetime:
                    total_size += file_size
                    logging.info(json.dumps({
                        "function_name": "process_zip_and_calculate_size",
                        "action": "File included",
                        "file": file_path,
                        "size": file_size,
                        "modified": str(file_mtime)
                    }))

        return{"answer": str(total_size)}  # ✅ Ensuring the return value is a string

    except zipfile.BadZipFile:
        logging.error(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Error", "error": "Corrupt ZIP file"}))
        return{"answer": "Error: Corrupt ZIP file."}
    except FileNotFoundError:
        logging.error(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "File not found", "file": zip_file_path}))
        return{"answer": "Error: ZIP file not found."}
    except Exception as e:
        logging.error(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Error", "error": str(e)}))
        return{"answer": f"An error occurred: {e}"}
    finally:
        # ✅ Cleanup safely
        if output_folder and os.path.exists(output_folder):
            shutil.rmtree(output_folder, ignore_errors=True)

        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
            logging.info(json.dumps({"function_name": "process_zip_and_calculate_size", "action": "Deleted ZIP file", "file": zip_file_path}))

async def process_zip_and_rename(zip_file_path):#16
    try:
        logging.info(f"function_name=process_zip_and_rename, zip_file_path={zip_file_path}")

        # Extract folder setup
        zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
        output_folder = os.path.join(extract_path, zip_file_name)
        os.makedirs(output_folder, exist_ok=True)

        # Extract ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)

        logging.info(f"function_name=process_zip_and_rename, extraction_complete={output_folder}")

        # Flatten files into one folder
        flat_folder = os.path.join(output_folder, "flat_files")
        os.makedirs(flat_folder, exist_ok=True)

        for root, _, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path != flat_folder:
                    new_path = os.path.join(flat_folder, file)
                    counter = 1
                    while os.path.exists(new_path):
                        base, ext = os.path.splitext(file)
                        new_path = os.path.join(flat_folder, f"{base}_{counter}{ext}")
                        counter += 1
                    shutil.move(file_path, new_path)
                    logging.info(f"function_name=process_zip_and_rename, moved_file={new_path}")

        # Rename files by modifying digits
        for file in os.listdir(flat_folder):
            old_file_path = os.path.join(flat_folder, file)
            new_file_name = re.sub(r'\d', lambda x: str((int(x.group(0)) + 1) % 10), file)
            new_file_path = os.path.join(flat_folder, new_file_name)
            if old_file_path != new_file_path:
                os.rename(old_file_path, new_file_path)
                logging.info(f"function_name=process_zip_and_rename, renamed={old_file_path} to {new_file_path}")

        # Check if files exist
        files_in_folder = sorted(os.listdir(flat_folder))
        if not files_in_folder:
            return{"answer": "Error: No files found in extracted folder."}

        # Compute SHA-256 checksum using grep, sort, and sha256sum
        checksum = None
        if os.name == "nt":
            logging.info(f"function_name=process_zip_and_rename, platform=Windows")
            hash_obj = hashlib.sha256()
            for file_name in files_in_folder:
                file_path = os.path.join(flat_folder, file_name)
                with open(file_path, "rb") as f:
                    while chunk := f.read(8192):
                        hash_obj.update(chunk)
            checksum = f"{hash_obj.hexdigest()}  -"
        else:
            logging.info(f"function_name=process_zip_and_rename, platform=Linux/Mac")
            bash_command = "grep . * | LC_ALL=C sort | sha256sum | awk '{print $1 \"  -\"}'"
            result = subprocess.run(
                bash_command, shell=True, cwd=flat_folder, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                logging.error(f"function_name=process_zip_and_rename, error={result.stderr}")
                return{"answer": f"Error running bash command: {result.stderr}"}
            checksum = result.stdout.strip()

        logging.info(f"function_name=process_zip_and_rename, checksum={checksum}")
        return{"answer": checksum}

    except FileNotFoundError:
        logging.error(f"function_name=process_zip_and_rename, error=ZIP file not found: {zip_file_path}")
        return{"answer": "Error: The ZIP file does not exist."}
    except Exception as e:
        logging.error(f"function_name=process_zip_and_rename, error={str(e)}")
        return{"answer": f"An error occurred: {e}"}
    finally:
        shutil.rmtree(output_folder, ignore_errors=True)
        os.remove(zip_file_path)
        logging.info(f"function_name=process_zip_and_rename, cleanup_complete={zip_file_path}")

async def compare_files_in_zip(zip_file_path):#17
    try:
        logging.info(f"function_name=compare_files_in_zip, zip_file_path={zip_file_path}")

        zip_file_name = os.path.splitext(os.path.basename(zip_file_path))[0]
        output_folder = os.path.join(extract_path, zip_file_name)
        os.makedirs(output_folder, exist_ok=True)

        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)

        text_files = [f for f in os.listdir(output_folder) if f.endswith('.txt')]
        if len(text_files) != 2:
            logging.error(f"function_name=compare_files_in_zip, error=Expected 2 text files, found {len(text_files)}")
            return{"answer": f"Error: Expected exactly 2 text files, found {len(text_files)}."}

        file1_path = os.path.join(output_folder, text_files[0])
        file2_path = os.path.join(output_folder, text_files[1])

        logging.info(f"function_name=compare_files_in_zip, comparing_files={file1_path}, {file2_path}")

        differing_lines = 0
        with open(file1_path, 'r', encoding='utf-8') as file1, open(file2_path, 'r', encoding='utf-8') as file2:
            for line1, line2 in itertools.zip_longest(file1, file2, fillvalue=""):
                if line1.strip() != line2.strip():
                    differing_lines += 1

        logging.info(f"function_name=compare_files_in_zip, differing_lines={differing_lines}")
        return{"answer": str(differing_lines)}

    except FileNotFoundError:
        logging.error(f"function_name=compare_files_in_zip, error=ZIP file not found: {zip_file_path}")
        return{"answer": "Error: The ZIP file does not exist."}
    except zipfile.BadZipFile:
        logging.error(f"function_name=compare_files_in_zip, error=Corrupt ZIP file: {zip_file_path}")
        return{"answer": "Error: Corrupt ZIP file."}
    except Exception as e:
        logging.error(f"function_name=compare_files_in_zip, error={str(e)}")
        return{"answer": f"An error occurred: {e}"}
    finally:
        shutil.rmtree(output_folder, ignore_errors=True)
        os.remove(zip_file_path)
        logging.info(f"function_name=compare_files_in_zip, cleanup_complete={zip_file_path}")

def get_total_sales_sql(ticket_type):#18
    try:
        logging.info(f"function_name=get_total_sales_sql, ticket_type={ticket_type}")
        # SQL query with TRIM and explicit ticket type
        sql_query = f"SELECT SUM(Units * Price) AS Total_Sales FROM tickets WHERE TRIM(LOWER(Type)) = LOWER('{ticket_type}');"
        logging.info(f"function_name=get_total_sales_sql, sql_query_generated={sql_query.strip()}")
        return{"answer": sql_query}

    except Exception as e:
        logging.error(f"function_name=get_total_sales_sql, error={str(e)}")
        return{"answer": f"An error occurred: {e}"}

#GA2---------------------------------------------------------
async def fetch_markdown(task: str):#1
    """
    Fetches a Markdown document from the AI API based on the given task.

    Args:
        task (str): The description of the documentation required.

    Returns:
        str: JSON response as a string in the format {"answer": markdown_content}
    """
    logging.info(f"Fetching Markdown for task: {task}")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                URL,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a technical writer. Provide a Markdown-formatted document.only return the Markdown document.not need  any explanation."},
                        {"role": "user", "content": f"Write a Markdown document for: {task.replace('\n', ' ')}"}  # Ensure line breaks don't cause issues
                    ]
                },
            )

            response.raise_for_status()
            response_json = response.json()

            # Handle potential missing keys
            markdown_content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not markdown_content:
                logging.error("API response did not contain expected markdown content")
                return {"answer": "API response error: No content returned"}

            logging.info("Markdown fetched successfully")

            # Return as a JSON string
            return {"answer": str(markdown_content)}

    except (httpx.HTTPError, httpx.RequestError) as e:
        logging.error(f"API request failed: {e}")
        return {"answer": f"API request failed: {e}"}


async def compress_image_to_base64(image_path: str, max_size: int = 1500) -> str:
    """
    Compress an image to Base64 Data URL format while ensuring the file size remains within the given limit.

    Args:
        image_path (str): Path to the image file.
        max_size (int, optional): Maximum allowed size in bytes. Defaults to 1500.

    Returns:
        str: JSON response in the format {"answer": base64_data_url}
    """
    logging.info(f"Starting compression for: {image_path} with max size {max_size} bytes")

    try:
        # Open the image and convert to 8 colors
        image = Image.open(image_path).convert("P", palette=Image.ADAPTIVE, colors=8)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        compressed_size = len(buffer.getvalue())

        logging.info(f"Initial compression size: {compressed_size} bytes")

        # If still above max_size, reduce to 4 colors
        if compressed_size > max_size:
            logging.info("Further compression needed, reducing colors to 4")
            image = image.convert("P", palette=Image.ADAPTIVE, colors=4)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            compressed_size = len(buffer.getvalue())

        logging.info(f"Final compressed image size: {compressed_size} bytes")

        # Convert to Base64 Data URL
        base64_string = base64.b64encode(buffer.getvalue()).decode("utf-8")
        base64_data_url = f"data:image/png;base64,{base64_string}"

        return {"answer": base64_data_url}

    except Exception as e:
        logging.error(f"Image compression failed: {e}")
        return {"answer": json.dumps(f"Error: {str(e)}")}

#Static hosting: GitHub Pages

def generate_hash(email: str, expiry_year: str = '2025'):#4
    """Generate a 5-character hash based on email and token expiry year."""
    try:
        email = email.strip()  # Remove unwanted spaces
        logging.info(f"Generating hash for email: {email} with expiry year: {expiry_year}")
        
        hash_value = hashlib.sha256(f"{email} {expiry_year}".encode()).hexdigest()
        result = hash_value[-5:]
        
        logging.info(f"Generated hash: {result}")
        return {"answer": result}
    except Exception as e:
        logging.error(f"Error in generate_hash: {e}")
        return {"answer": "error"}

def count_light_pixels(image_path: str) -> dict:#5
    """Counts the number of pixels with lightness > 0.662 in an image."""
    try:
        logging.info(f"Running on: {platform.system()} - Processing image: {image_path}")
        
        image = Image.open(image_path)
        rgb = np.array(image) / 255.0
        lightness = np.apply_along_axis(lambda x: colorsys.rgb_to_hls(*x)[1], 2, rgb)
        count = int(np.sum(lightness > 0.662))
        
        logging.info(f"Counted {count} light pixels in the image")
        return {"answer": str(count)}
    
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
        return {"answer": "error"}

#Serverless hosting: Vercel

async def push_github_action(email: str, github_username: str, repo_name: str, github_token: str) -> dict:#7
    """Creates and pushes a GitHub Actions workflow file, then returns the action URL."""
    logging.info(f"Starting GitHub Action setup for {github_username}/{repo_name}")

    workflow_content = f"""name: Custom GitHub Action

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: {email}
        run: echo \"Hello, world!\"
    """

    workflows_dir = ".github/workflows"
    workflow_file = f"{workflows_dir}/custom_action.yml"
    repo_url = f"https://{github_username}:{github_token}@github.com/{github_username}/{repo_name}.git"

    try:
        os.makedirs(workflows_dir, exist_ok=True)
        with open(workflow_file, "w") as f:
            f.write(workflow_content)
        logging.info("Workflow file created successfully.")

        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        subprocess.run(["git", "fetch"], check=True)
        subprocess.run(["git", "checkout", "-B", "main"], check=True)
        subprocess.run(["git", "add", workflow_file], check=True)
        subprocess.run(["git", "commit", "-m", "Added GitHub Actions workflow"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

        actions_url = f"https://github.com/{github_username}/{repo_name}/actions"
        logging.info(f"GitHub Actions setup completed: {actions_url}")
        return {"answer": actions_url}

    except subprocess.CalledProcessError as e:
        logging.error(f"Error while pushing to GitHub: {e}")
        return {"answer": "Error occurred while pushing workflow."}

async def push_docker_image(image_name: str) -> dict:#8
    """Builds, tags, and pushes a Docker image to Docker Hub, then returns its URL."""
    
    docker_username = "YOUR_DOCKER_USERNAME"  # Replace with your actual Docker Hub username
    full_image_name = f"{docker_username}/{image_name}"
    tag = "latest"

    logging.info(f"Starting Docker build for image: {full_image_name}")

    try:
        # Build the Docker image
        subprocess.run(["docker", "build", "-t", full_image_name, "."], check=True)
        logging.info(f"Docker image {full_image_name} built successfully.")

        # Tag the image
        subprocess.run(["docker", "tag", full_image_name, f"{full_image_name}:{tag}"], check=True)
        logging.info(f"Docker image {full_image_name} tagged as {tag}.")

        # Push the image
        subprocess.run(["docker", "push", f"{full_image_name}:{tag}"], check=True)
        logging.info(f"Docker image {full_image_name}:{tag} pushed successfully.")

        docker_url = f"https://hub.docker.com/r/{docker_username}/{image_name}"
        logging.info(f"Docker image available at: {docker_url}")

        return {"answer": docker_url}

    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while processing Docker image: {e}", exc_info=True)
        return {"answer": f"Error: {e}"}

#CORS: Cross-Origin Resource Sharing
#Make sure you enable CORS to allow GET requests from any origin.
# What is the API URL endpoint for FastAPI? It might look like: http://127.0.0.1:8000/api

async def run_llamafile_with_ngrok(model_path: str, port: int = 8080) -> dict:#10
    """Runs Llamafile with the given model and exposes it via ngrok, returning the public URL."""

    logging.info(f"Starting Llamafile server with model: {model_path}")

    try:
        # Start Llamafile server in the background
        llamafile_process = subprocess.Popen(
            [model_path, "--server"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logging.info("Llamafile server started successfully.")

        # Wait for the server to initialize
        time.sleep(5)

        # Start ngrok tunnel
        logging.info(f"Starting ngrok on port {port}...")
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Wait for ngrok to establish the tunnel
        time.sleep(5)

        # Fetch the public ngrok URL
        ngrok_output = subprocess.check_output(["curl", "-s", "http://127.0.0.1:4040/api/tunnels"])
        match = re.search(r'"public_url":"(https://[a-zA-Z0-9.-]+\.ngrok-free.app)"', ngrok_output.decode())

        if match:
            public_url = match.group(1)
            logging.info(f"ngrok tunnel established: {public_url}")
            return {"answer": public_url}
        else:
            error_message = "Error: Could not retrieve ngrok URL."
            logging.error(error_message)
            return {"answer": error_message}

    except subprocess.CalledProcessError as e:
        error_message = f"Error: {e}"
        logging.error(error_message, exc_info=True)
        return {"answer": error_message}

#GA3 -------------------------------------------------------

#LLM Sentiment Analysis

def count_tokens(text: str):#2
    """Counts the number of tokens in a given text using the GPT-4 tokenizer."""

    logging.info("Initializing the tokenizer for GPT-4 models.")
    
    try:
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        token_count = len(encoding.encode(text))
        logging.info(f"Token count for the provided text: {token_count}")
        return {"answer": str(token_count)}
    
    except Exception as e:
        logging.error(f"Error in token counting: {str(e)}", exc_info=True)
        return {"answer": f"Error: {str(e)}"}

#3LLM Text Extraction

def create_openai_request(image_path_or_base64: str,is_file=True):#4
    """
    Creates a JSON body for an OpenAI API request using GPT-4o-mini.

    - If the input is a file path, it converts the image to a base64 URL.
    - If the input is already a base64 URL, it uses it directly.

    Returns the JSON body as a string inside a dictionary (to match required format).
    """
    
    logging.info("Processing image input for OpenAI API request.")

    try:
        # Check if the input is already a base64 URL
        # if image_path_or_base64.startswith("data:image/"):
        if is_file==False:
            logging.info("Input is already in base64 format.")
            image_url = image_path_or_base64  # Use it directly
        else:
            if not os.path.exists(image_path_or_base64):
                raise FileNotFoundError(f"File not found: {image_path_or_base64}")

            # Read the image and convert it to base64 URL
            mime_type, _ = mimetypes.guess_type(image_path_or_base64)
            if not mime_type:
                raise ValueError("Could not determine MIME type for the image.")

            logging.info(f"Reading image from {image_path_or_base64} and encoding it as base64.")
            with open(image_path_or_base64, "rb") as img_file:
                base64_data = base64.b64encode(img_file.read()).decode("utf-8")
                image_url = f"data:{mime_type};base64,{base64_data}"

        # Construct the JSON body
        json_body = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract text from this image."},
                        {"type": "image_url", "image_url": {"url":image_url}}
                    ]
                }
            ]
        }

        logging.info("Successfully created OpenAI request JSON.")
        return {"answer": json.dumps(json_body)}

    except Exception as e:
        logging.error(f"Error in create_openai_request: {str(e)}", exc_info=True)
        return {"answer": f"Error: {str(e)}"}

def create_embedding_json(value1: str, value2: str):#5
    """
    Creates a JSON structure for text embeddings using 'text-embedding-3-small'.

    - Takes two text inputs and formats them for an embedding request.
    - Returns the JSON object inside a dictionary.
    """

    logging.info("Generating embedding request JSON.")

    try:
        # Construct the embedding request payload
        ans = {
            "model": "text-embedding-3-small",
            "input": [value1, value2]
        }

        logging.info("Successfully created embedding JSON.")
        return {"answer": json.dumps(ans)}

    except Exception as e:
        logging.error(f"Error in create_embedding_json: {str(e)}", exc_info=True)
        return {"answer": f"Error: {str(e)}"}

async def fetch_function(task: str):#1,6
    """
    Fetches a Python function from the AI API based on the given task.

    Args:
        task (str): The description of the function required.

    Returns:
        str: JSON response as a string in the format {"answer": function_code_as_string}
    """
    logging.info(f"Fetching function for task: {task}")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                URL,
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a helpful coding assistant. Only return the function code without any explanation."},
                        {"role": "user", "content": f"Give me a Python function to {task}"}
                    ]
                },
            )

            response.raise_for_status()
            response_json = response.json()
            function_code = response_json["choices"][0]["message"]["content"]

            # Remove unwanted backticks and "python" keyword
            cleaned_function_code = function_code.strip("```").replace("python", "").strip()

            logging.info("Function fetched successfully")
            logging.info(f"Function {cleaned_function_code}")

            # Return as a JSON string
            return {"answer": cleaned_function_code}

    except httpx.HTTPError as e:
        logging.error(f"API request failed: {e}")
        return json.dumps({"answer": f"API request failed: {e}"})

#7Vector Databases
#What is the API URL endpoint for your implementation? It might look like: http://127.0.0.1:8000/similarity

#8Function Calling with OpenAI

#GA4 starts-----------------------------------------------------------------------------------

async def fetch_cricinfo_ducks(page_number: int):#1
    """
    Asynchronously fetches ODI batting statistics from ESPN Cricinfo and counts total ducks on the given page.

    Args:
        page_number (int): The page number to fetch statistics from.

    Returns:
        str: JSON response in the format {"answer": total_ducks_as_string}
    """
    logging.info(f"Fetching ODI batting statistics for page {page_number} asynchronously.")

    url = f"https://stats.espncricinfo.com/stats/engine/stats/index.html?class=2;page={page_number};template=results;type=batting"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.espncricinfo.com/"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logging.error(f"❌ Failed to retrieve data. Status Code: {response.status}")
                    return {"answer": f"Error: HTTP {response.status}"}

                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table", class_="engineTable")

        if len(tables) < 3:
            logging.error("❌ Unable to locate the correct data table.")
            return {"answer": "Error: Data table not found"}

        stats_table = tables[2]
        table_headers = [th.text.strip() for th in stats_table.find_all("th")]

        if not table_headers:
            logging.error("❌ No headers found in the table!")
            return {"answer": "Error: Headers not found in the table"}

        rows = []
        for tr in stats_table.find_all("tr")[1:]:
            cols = [td.text.strip() for td in tr.find_all("td")]
            if cols:
                rows.append(cols)

        df = pd.DataFrame(rows, columns=table_headers)

        if "0" not in df.columns:
            logging.error("❌ Ducks column not found in the table!")
            return json.dumps({"answer": "Error: Ducks column missing"})

        df["0"] = pd.to_numeric(df["0"], errors="coerce").fillna(0).astype(int)
        total_ducks = df["0"].sum()

        logging.info(f"✅ Total ducks on page {page_number}: {total_ducks}")
        return {"answer": str(total_ducks)}

    except aiohttp.ClientError as e:
        logging.error(f"❌ Failed to retrieve data. Error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

async def extract_top_25_movies(url: str,start,end):#2
    """
    Extracts the top 25 movies from the given IMDb URL.

    Args:
        url (str): The IMDb search URL.

    Returns:
        str: JSON response in the format {"answer": movies_list_as_string}
    """
    url=url=url+f"?user_rating={start},{end}"
    logging.info(f"Fetching top 25 movies from IMDb: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logging.info("✅ IMDb page successfully fetched.")

        soup = BeautifulSoup(response.text, 'html.parser')
        movie_divs = soup.find_all('div', class_='sc-f30335b4-0 eefKuM')

        if not movie_divs:
            logging.warning("⚠️ No movie data found on the page.")
            return {"answer": "Error: No movie data found"}

        movies = []

        for movie_div in movie_divs[:25]:  # Limit to first 25 movies
            first_div = movie_div.find('div')
            if first_div:
                a_tag = first_div.find('a')
                movie_id = a_tag['href'].split('/')[-2] if a_tag else "N/A"
                movie_name = first_div.find('h3', class_='ipc-title__text').text.strip() if first_div.find('h3', class_='ipc-title__text') else "N/A"
            else:
                movie_id = movie_name = "N/A"

            year_span = movie_div.find_all('div')[1].find('span') if len(movie_div.find_all('div')) > 1 else None
            year = year_span.text.strip() if year_span else "N/A"

            rating_span = movie_div.find('span', class_='ipc-rating-star--rating')
            rating = rating_span.text.strip() if rating_span else "N/A"

            movies.append({
                "id": movie_id,
                "title": movie_name,
                "year": year,
                "rating": rating
            })

        logging.info(f"✅ Successfully extracted {len(movies)} movies.")

        # Return as a JSON string
        return {"answer": json.dumps(movies)}

    except requests.RequestException as e:
        logging.error(f"❌ Failed to retrieve data. Error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

#3Scraping emarketer
#What is the URL of your API endpoint?

async def fetch_bbc_weather_summary(required_city: str) -> str:#4
    """
    Fetches BBC Weather summary for a given city.

    Args:
        required_city (str): The city for which to fetch the weather summary.

    Returns:
        str: JSON response in the format {"answer": weather_summary_as_string}
    """
    logging.info(f"Fetching BBC Weather summary for {required_city}")

    # Construct API URL to get the location ID
    location_url = 'https://locator-service.api.bbci.co.uk/locations?' + urlencode({
        'api_key': 'AGbFAKx58hyjQScCXIYrxuEwJh2W2cmv',
        's': required_city,
        'stack': 'aws',
        'locale': 'en',
        'filter': 'international',
        'place-types': 'settlement,airport,district',
        'order': 'importance',
        'a': 'true',
        'format': 'json'
    })

    try:
        # Fetch location data
        location_result = requests.get(location_url)
        location_result.raise_for_status()
        location_data = location_result.json()

        # Extract location ID
        location_id = location_data['response']['results']['results'][0]['id']
        weather_url = f'https://www.bbc.com/weather/{location_id}'

        # Fetch weather page
        response = requests.get(weather_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info(f"✅ Successfully retrieved weather data for {required_city}")

        # Extract weather summary
        daily_summary = soup.find('div', attrs={'class': 'wr-day-summary'})
        daily_high_values = soup.find_all('span', attrs={'class': 'wr-day-temperature__high-value'})

        if not daily_summary or not daily_high_values:
            logging.warning("⚠️ Weather data not found on the BBC Weather page.")
            return json.dumps({"answer": "Error: Weather data not found"})

        # Process weather summaries
        daily_summary_list = re.findall('[a-zA-Z][^A-Z]*', daily_summary.text)
        datelist = pd.date_range(datetime.today(), periods=len(daily_high_values)).tolist()
        datelist = [datelist[i].date().strftime('%Y-%m-%d') for i in range(len(datelist))]

        # Construct dictionary
        weather_dict = {datelist[i]: daily_summary_list[i].strip() for i in range(len(datelist))}
        logging.info(f"✅ Successfully processed weather summary for {required_city}")

        # Return as a JSON string
        return {"answer": json.dumps(weather_dict)}

    except requests.RequestException as e:
        logging.error(f"❌ Failed to retrieve data. Error: {str(e)}")
        return json.dumps({"answer": f"Error: {str(e)}"})

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return json.dumps({"answer": f"Error: {str(e)}"})

async def get_max_latitude(country: str, city: str) -> str:#5
    """
    Fetches the latitude of a given city in a specified country.

    Args:
        country (str): Name of the country.
        city (str): Name of the city.

    Returns:
        str: JSON response in the format {"answer": latitude_as_string}
    """
    logging.info(f"Fetching latitude for {city}, {country}.")

    try:
        # Initialize the geocoder
        locator = Nominatim(user_agent="geo_location_fetcher")

        # Fetch the location
        location = locator.geocode(f"{city}, {country}", timeout=10)

        # If location is not found, return an error
        if not location:
            logging.warning(f"⚠️ Location not found for {city}, {country}.")
            return {"answer": "Location not found."}

        latitude = str(location.latitude)
        logging.info(f"✅ Found latitude for {city}, {country}: {latitude}")

        return {"answer": latitude}

    except GeocoderTimedOut:
        logging.error("❌ Geocoder service timed out.")
        return json.dumps({"answer": "Error: Geocoder service timed out."})

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return json.dumps({"answer": f"Error: {str(e)}"})

async def fetch_hacker_news_post(min_points: int) -> str:#6
    """
    Fetches a Hacker News post with at least the specified number of points.

    Args:
        min_points (int): The minimum number of points required for the post.

    Returns:
        str: JSON response in the format {"answer": post_link_as_string}
    """
    logging.info(f"Fetching Hacker News posts with at least {min_points} points.")

    # HNRSS API URL for searching posts mentioning "Hacker"
    url = "https://hnrss.org/newest?q=Hacker"

    try:
        # Fetch the RSS feed
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        root = ET.fromstring(response.content)

        # Iterate through items in the RSS feed
        for item in root.findall(".//item"):
            title = item.find("title").text
            link = item.find("link").text
            description = item.find("description").text

            # Extract points from the description using regex
            match = re.search(r"(\d+) points", description)
            points = int(match.group(1)) if match else 0

            # Check if the post has the required points
            if points >= int(min_points):
                logging.info(f"✅ Found a post with {points} points: {title} ({link})")
                return {"answer": link}

        logging.warning(f"⚠️ No post found with at least {min_points} points.")
        return {"answer": "No post found with the required points."}

    except requests.RequestException as e:
        logging.error(f"❌ Failed to retrieve data. Error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

#7Emerging Developer Talent for CodeConnect

#8Scheduled Scraping with GitHub Actions



def extract_and_calculate(pdf_path, start_group, end_group, subject_filter, total_subject_mark, min_mark):
    logging.disable(logging.CRITICAL)  # Disable all logging
    extracted_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                table = page.extract_table()
                
                if not table:
                    continue  # Skip if no table

                # Detect group numbers from text before the table
                current_group = None
                for line in text.split("\n"):
                    if "Group" in line:
                        try:
                            current_group = int(line.split()[-1])  # Ensure it's an integer
                            break
                        except ValueError:
                            continue  

                if current_group is None or not isinstance(current_group, int):
                    continue  # Skip invalid groups
                
                # Append group number to each row in the table
                for row in table[1:]:  # Skip headers
                    extracted_data.append([current_group] + row)

    except Exception as e:
        logging.error(f"❌ Error processing PDF: {str(e)}")
        return {"answer": f"Error: {str(e)}"}
    
    # If no data was extracted
    if not extracted_data:
        logging.warning(f"⚠️ No relevant data found in {pdf_path}")
        return {"answer": "0"}

    # Extract column names from the first table
    columns = ["Group"] + table[0]

    # Convert to DataFrame
    df = pd.DataFrame(extracted_data, columns=columns)

    # ✅ Convert necessary columns to numeric
    df["Group"] = pd.to_numeric(df["Group"], errors="coerce").fillna(0).astype(int)
    df[subject_filter] = pd.to_numeric(df[subject_filter], errors="coerce").fillna(0).astype(int)
    df[total_subject_mark] = pd.to_numeric(df[total_subject_mark], errors="coerce").fillna(0).astype(int)

    # ✅ Ensure `start_group`, `end_group`, and `min_mark` are integers
    start_group = int(start_group)
    end_group = int(end_group)
    min_mark = int(min_mark)

    # Apply filtering
    df_filtered = df[(df["Group"] >= start_group) & (df["Group"] <= end_group)]
    df_filtered = df_filtered[df_filtered[subject_filter] >= min_mark]

    # Compute sum
    total_marks = df_filtered[total_subject_mark].sum()
    
    logging.info(f"✅ Computed Total {total_subject_mark} Marks: {total_marks} (Groups {start_group}-{end_group})")

    logging.disable(logging.NOTSET)  
    return {"answer": str(total_marks)}

#10

#Ga5----------------------------------------------

def process_file(file_path, product, country, filter_date):#1
    """
    Processes the file, cleans and filters the data, and calculates the total margin.

    Parameters:
        file_path (str): Path to the Excel file.
        product (str): Product name to filter.
        country (str): Country to filter.
        filter_date (datetime): Filter transactions up to this date.

    Returns:
        str: JSON response in the format {"answer": total_margin}
    """
    try:
        logging.info(f"Loading Excel file: {file_path}")
        df = pd.read_excel(file_path, dtype=str)

        # Ensure required columns exist
        required_columns = {'Customer Name', 'Country', 'Date', 'Product/Code', 'Sales', 'Cost'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            logging.error(f"Missing columns: {missing_columns}")
            return {"answer": f"Error: Missing columns {missing_columns}"}

        # Clean customer names
        df['Customer Name'] = df['Customer Name'].str.strip()

        # Standardize country names
        country_map = {
            'USA': 'US', 'U.S.A': 'US', 'United States': 'US',
            'U.K': 'UK', 'United Kingdom': 'UK',
            'Fra': 'FR', 'FRA': 'FR', 'France': 'FR',
            'Bra': 'BR', 'BRA': 'BR', 'Brazil': 'BR',
            'Ind': 'IN', 'IND': 'IN', 'India': 'IN',
            'UAE': 'AE', 'U.A.E': 'AE', 'United Arab Emirates': 'AE'
        }
        df['Country'] = df['Country'].str.strip().replace(country_map)

        # Convert dates to a standardized format
        def robust_parse_date(date):
            if pd.isna(date):
                return pd.NaT
            date_formats = ["%m-%d-%Y", "%Y/%m/%d", "%d-%m-%Y", "%Y-%m-%d"]
            for fmt in date_formats:
                try:
                    return datetime.strptime(date, fmt)
                except ValueError:
                    continue
            return pd.NaT  # Return NaT if parsing fails

        df['Date'] = df['Date'].astype(str).apply(robust_parse_date)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Extract product names
        df['Product'] = df['Product/Code'].apply(lambda x: x.split('/')[0] if pd.notna(x) else '')

        # Clean Sales and Cost columns
        df['Sales'] = df['Sales'].str.replace("USD", "").str.strip()
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)

        df['Cost'] = df['Cost'].str.replace("USD", "").str.strip()
        df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')

        # Fill missing costs with 50% of sales
        df['Cost'].fillna(df['Sales'] * 0.5, inplace=True)

        # Filter transactions based on conditions
        filtered_df = df[(df['Date'] <= filter_date) & 
                         (df['Product'] == product) & 
                         (df['Country'] == country)]

        # Calculate the total margin
        total_sales = filtered_df['Sales'].sum()
        total_cost = filtered_df['Cost'].sum()
        total_margin = (total_sales - total_cost) / total_sales if total_sales > 0 else 0

        logging.info(f"Total Sales: {total_sales}, Total Cost: {total_cost}, Total Margin: {total_margin:.2%}")
        return {"answer": str(round(total_margin, 4))}

    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

def count_unique_students_by_id(file_path):#2
    """
    Counts unique student IDs from a text file and returns the count in a JSON format.

    Parameters:
        file_path (str): Path to the text file.

    Returns:
        str: JSON string containing the unique student count.
    """
    logging.info("Processing file: %s", file_path)

    if not os.path.exists(file_path):
        logging.error("File not found: %s", file_path)
        return {"answer": "Error: File not found"}

    unique_student_ids = set()

    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            for line in file:
                match = re.search(r"-\s*([A-Z0-9]+)\s*::?Marks", line)
                if match:
                    student_id = match.group(1).strip()
                    unique_student_ids.add(student_id)

        student_count = len(unique_student_ids)
        logging.info("Unique student count: %d", student_count)
        return {"answer": str(student_count)}

    except Exception as e:
        logging.exception("Error processing file: %s", str(e))
        return {"answer": f"Error: {str(e)}"}

def count_successful_requests(file_path, category, start_hour, end_hour, day):#3
    """
    Counts the number of successful GET requests for a given category during a specified time range and day.

    Parameters:
    file_path (str): Path to the gzip log file.
    category (str): The category of the URL (e.g., 'hindi').
    start_hour (int): The starting hour (24-hour format).
    end_hour (int): The ending hour (exclusive, 24-hour format).
    day (str): The target day (e.g., 'Thursday').

    Returns:
    dict: JSON response containing the count as a string.
    """

    logging.info("Starting request count process for category: %s, between %d-%d hours on %s", 
                 category, start_hour, end_hour, day)

    # Conditions
    valid_status_range = range(200, 300)  # Successful request status codes
    valid_hours = set(range(start_hour, end_hour))  # Specified hours

    # Pattern to match log entry format
    log_pattern = re.compile(r'^(\S+) (\S+) (\S+) \[(.*?)\] "(GET) (\S+) (\S+)" (\d+) (\S+) "(.*?)" "(.*?)" (\S+) (\S+)')

    # Counter for successful requests
    successful_requests = 0

    try:
        # Process the log file
        with gzip.open(file_path, 'rt', encoding='utf-8') as file:
            for line in file:
                match = log_pattern.match(line)
                if match:
                    # Extract relevant fields
                    time_str = match.group(4)  # Extract timestamp
                    method = match.group(5)  # HTTP method
                    url = match.group(6)  # URL requested
                    status = int(match.group(8))  # Status code

                    # Parse the timestamp (log time is in GMT-0500)
                    log_time = datetime.strptime(time_str, "%d/%b/%Y:%H:%M:%S %z")

                    # Convert log time to GMT-0500 (already in correct timezone per problem statement)
                    gmt_minus_5 = timezone(timedelta(hours=-5))
                    log_time = log_time.astimezone(gmt_minus_5)

                    # Ensure the URL starts with the given category and matches conditions
                    if (method == "GET" and url.startswith(f"/{category}/") and
                            status in valid_status_range and
                            log_time.strftime("%A") == day and
                            log_time.hour in valid_hours):
                        successful_requests += 1

        logging.info("Successfully processed log file: %s", file_path)
    
    except Exception as e:
        logging.error("Error processing file %s: %s", file_path, str(e))
        return {"answer": "Error processing file"}

    logging.info("Total successful requests found: %d", successful_requests)

    # Return result in required format
    return {"answer": str(successful_requests)}

def process_log(file_path, category, target_date):#4
    """
    Processes the log file to identify the top IP address by volume of downloads
    on a specific date for a given category.

    :param file_path: Path to the gzipped log file.
    :param category: The category (e.g., 'hindi') to filter requests.
    :param target_date: The date in "YYYY-MM-DD" format to filter logs.
    :return: JSON response with the total bytes downloaded by the top IP.
    """

    logging.info("Starting log processing for category: %s on date: %s", category, target_date)

    # Apache log format regex
    log_pattern = re.compile(r'^(\S+) (\S+) (\S+) \[(.*?)\] "(GET) (\S+) (\S+)" (\d+) (\S+) "(.*?)" "(.*?)"')

    # Dictionary to store total bytes downloaded per IP
    ip_data = defaultdict(int)

    # Convert target_date to a datetime object for comparison
    try:
        target_datetime = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        logging.error("Invalid date format: %s. Please use YYYY-MM-DD.", target_date)
        return {"answer": "Invalid date format"}

    # Process the log file
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8', errors='ignore') as file:
            for line in file:
                match = log_pattern.match(line)
                if match:
                    ip = match.group(1)  # Extract IP
                    time_str = match.group(4)  # Extract timestamp
                    method = match.group(5)  # HTTP method
                    url = match.group(6)  # URL requested
                    status = int(match.group(8))  # Status code
                    size = match.group(9)  # Response size

                    # Convert size to integer, handling "-" cases
                    bytes_transferred = int(size) if size.isdigit() else 0

                    # Parse log timestamp
                    try:
                        log_time = datetime.strptime(time_str, "%d/%b/%Y:%H:%M:%S %z")
                    except ValueError:
                        logging.warning("Skipping malformed timestamp: %s", time_str)
                        continue

                    # Convert log time to date-only for comparison
                    log_date = log_time.date()

                    # Check if request matches category, date, and is successful (status 200-299)
                    if (method == "GET" and url.startswith(f"/{category}/") and
                        log_date == target_datetime and 200 <= status < 300):
                        ip_data[ip] += bytes_transferred

        logging.info("Successfully processed log file: %s", file_path)

    except FileNotFoundError:
        logging.error("Log file not found: %s", file_path)
        return {"answer": "Log file not found"}
    except Exception as e:
        logging.error("Unexpected error processing file %s: %s", file_path, str(e))
        return {"answer": "Error processing file"}

    # Identify the top IP address by volume of downloads
    if ip_data:
        top_ip = max(ip_data, key=ip_data.get)
        top_bytes = ip_data[top_ip]
        logging.info("Top IP: %s with %d bytes transferred", top_ip, top_bytes)
    else:
        logging.info("No matching log entries found.")
        top_bytes = 0

    return {"answer": str(top_bytes)}

def count_units_sold_in_tokyo(file_path, target_city="Tokyo", product="Shoes", sales_threshold=130):
    """
    Counts the total units of a specific product sold in a target city, considering fuzzy matching and a sales threshold.
    
    :param file_path: Path to the JSON file containing sales data.
    :param target_city: The target city to match (default: 'Tokyo').
    :param product: The product to filter (default: 'Shoes').
    :param sales_threshold: Minimum sales required per transaction (default: 130).
    :return: JSON response with the total units sold in the target city.
    """

    logging.info("Starting sales data processing for city: %s, product: %s", target_city, product)

    # Function to check fuzzy matching for city names
    def is_similar(city_name, target_name):
        return fuzz.ratio(city_name.lower(), target_name.lower()) >= 80

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        total_units_sold = sum(
            transaction['sales']
            for transaction in data
            if is_similar(transaction['city'], target_city)
            and transaction['sales'] >= sales_threshold
            and transaction['product'].lower() == product.lower()
        )

        logging.info("Successfully processed file: %s", file_path)
        logging.info("Total units sold in %s for %s: %d", target_city, product, total_units_sold)

        return {"answer": str(total_units_sold)}

    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
        return {"answer": "File not found"}
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in file: %s", file_path)
        return {"answer": "Invalid JSON format"}
    except Exception as e:
        logging.error("Unexpected error: %s", str(e))
        return {"answer": "Error processing file"}

#6

def count_key_occurrences(file_path: str, key_to_count: str) -> Dict[str, str]:
    """
    Counts occurrences of a specific key in a nested JSON structure.

    :param file_path: Path to the JSON file.
    :param key_to_count: The key to search for in the JSON data.
    :return: A JSON response {"answer": str(count)}.
    """

    def count_key_in_dict(d, key):
        count = 0
        if isinstance(d, dict):
            for k, v in d.items():
                if k == key:
                    count += 1
                count += count_key_in_dict(v, key)
        elif isinstance(d, list):
            for item in d:
                count += count_key_in_dict(item, key)
        return count

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        key_count = count_key_in_dict(data, key_to_count)

        logging.info(f"Key '{key_to_count}' found {key_count} times in the JSON file: {file_path}")

        return {"answer": str(key_count)}

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return {"answer": "Error: File not found"}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {file_path}")
        return {"answer": "Error: Invalid JSON format"}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}
#8

def youtube_transcribe(start_time: int, end_time: int) -> Dict[str, str]:
    """
    Downloads audio from YouTube, extracts a segment, and transcribes it using a locally saved Whisper model.
    """
    youtube_url = "https://www.youtube.com/watch?v=NRntuOJu4ok"
    audio_file = "downloaded_audio.mp3"
    trimmed_audio = "trimmed_audio.wav"
    model_dir = "./../app/models/whisper_base_en"  # Path to the saved model

    try:
        # Step 1: Download audio
        logging.info("📥 Downloading audio from YouTube...")
        subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_file, youtube_url], check=True)

        # Step 2: Extract the required segment
        logging.info(f"✂️ Extracting segment from {start_time}s to {end_time}s...")
        subprocess.run(["ffmpeg", "-i", audio_file, "-ss", str(start_time), "-to", str(end_time),
                        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "-y", trimmed_audio], check=True)

        # Step 3: Load the locally saved model
        logging.info("📝 Loading Faster Whisper model from local storage...")
        model = WhisperModel("base.en", download_root=model_dir)

        # Step 4: Transcribe audio
        segments, _ = model.transcribe(trimmed_audio)
        transcript_text = " ".join(segment.text for segment in segments)
        logging.info(f"✅ Transcription Completed: {transcript_text}")

        return {"answer": transcript_text}

    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocess error: {e}")
        return {"answer": "Error: Failed to process audio"}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"answer": f"Error: {str(e)}"}

#10 image