from faster_whisper import WhisperModel
import os
import shutil

def save_file(file):
    if file is not None:
        # Ensure the directory exists
        save_dir = "app/data"
        os.makedirs(save_dir, exist_ok=True)  # ✅ Create directory if it doesn't exist

        # Define the full file path
        file_location = os.path.join(save_dir, file.filename)  # ✅ Corrected path format
        
        # Save the file locally
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        return file_location
    else:
        return None  
    
def download_model():
    # Set model path
    model_dir = "./../app/models/whisper_base_en"  # Change to your preferred directory
    model = WhisperModel("base.en", download_root=model_dir)
    return("✅ Model downloaded and stored locally at:", model_dir)

def clear_pycache(directory: str = "/"):
    """
    Recursively deletes all __pycache__ directories in the given directory.
    :param directory: The root directory to search for __pycache__ folders.
    """
    for root, dirs, files in os.walk(directory):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"🗑️ Deleted: {pycache_path}")
            
import os
import requests

def url_download_file(url: str, save_dir: str = "app/data") -> str:
    """
    Downloads a file from the given URL and saves it in the specified directory.

    Args:
        url (str): The URL of the file to download.
        save_dir (str, optional): The directory where the file will be saved. Defaults to "downloads".

    Returns:
        str: The file path of the downloaded file.
    """

    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True)

    # Extract filename from URL
    filename = os.path.basename(url.split("?")[0])  # Remove query params if any
    file_path = os.path.join(save_dir, filename)

    try:
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"✅ File downloaded successfully: {file_path}")
        return file_path

    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading file: {e}")
        return ""

# Example usage:
# file_path = url_download_file("https://exam.sanand.workers.dev/shapes.png")
          
            
            