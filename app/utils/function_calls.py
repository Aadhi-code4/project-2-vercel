function_call = [
{
    "type": "function",
    "function": {
        "name": "vscode_code_s",
        "description": "Return the version and operating system details of Visual Studio Code when a user asks about the output of the 'code -s' command.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "send_httpie_request",#2
        "description": "Send an HTTPS GET request to the given URL with a URL-encoded parameter 'email' set to the provided email address, and return the JSON body of the response.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to which the HTTPS GET request will be sent (e.g., 'https://httpbin.org/get')."
                },
                "email": {
                    "type": "string",
                    "description": "The email address to include as a URL-encoded query parameter in the GET request."
                }
            },
            "required": ["url", "email"],
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "format_and_hash",
        "description": "run npx -y prettier@3.4.2 README.md | sha256sum. Format the given file using Prettier (version 3.4.2) and compute its SHA-256 hash using sha256sum.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "calculate_formula",
        "description": "Calculate the result of spreadsheet formulas for Google Sheets or Excel, by parsing specific syntax and applying logic.",
        "parameters": {
            "type": "object",
            "properties": {
                "sheet_type": {
                    "type": "string",
                    "enum": ["Google Sheets", "Excel"],
                    "description": "Specify the type of spreadsheet software. Allowed values: 'Google Sheets' or 'Excel'."
                },
                "formula": {
                    "type": "string",
                    "description": "The formula to evaluate. For Google Sheets, example: '=SUM(ARRAY_CONSTRAIN(SEQUENCE(100, 100, 14, 13), 1, 10))'. For Excel, example: '=SUM(TAKE(SORTBY({values}, ...), 1, count))'."
                }
            },
            "required": ["sheet_type", "formula"], 
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "extract_hidden_value_from_string",
        "description": "Extracts the value of the first hidden input field from an HTML file or HTML contents in string.",
        "parameters": {
            "type": "object",
            "properties": {
                "html_input": {
                    "type": "string",
                    "description": "if The HTML content is present in the query return the HTML content.if not then return None"
                },
                "is_file": {
                    "type": "boolean",
                    "description": "Set to false if HTML content is present in the query; true if  HTML content is not present in the query."
                }
            },
            "required": ["html_input", "is_file"],
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "count_weekdays",
        "description": "Calculate the number of occurrences of a specific weekday (e.g., Wednesday) within a given date range.",
        "parameters": {
            "type": "object",
            "properties": {
                "day_of_week": {
                    "type": "string",
                    "description": "The name of the weekday to count (e.g., 'Monday', 'Tuesday', 'Wednesday', etc.)."
                },
                "start_date": {
                    "type": "string",
                    "description": "The starting date of the range, in the format 'YYYY-MM-DD'."
                },
                "end_date": {
                    "type": "string",
                    "description": "The ending date of the range, in the format 'YYYY-MM-DD'."
                }
            },
            "required": ["day_of_week", "start_date", "end_date"],
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "read_answer_column",
        "description": "Extract the values from the specified column ('answer' column) of a CSV file located inside a ZIP archive.",
        "parameters": {
            "type": "object",
            "properties": {
                "zip_file_path": {
                    "type": "string",
                    "description": "The path to the ZIP file containing the CSV file."
                },
                "column": {
                    "type": "string",
                    "description": "The column name in the CSV file from which values need to be extracted (e.g., 'answer')."
                }
            },
            "required": ["zip_file_path", "column"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
  "type": "function",
  "function": {
    "name": "sort_json_array",
    "description": "Sort a structured JSON array of objects based on numerical or string properties. Only use this when a user explicitly asks to sort JSON data by specified keys.",
    "parameters": {
      "type": "object",
      "properties": {
        "json_array": {
          "type": "array",
          "items": {
            "type": "object"
          },
          "description": "The JSON array of objects to be sorted."
        },
        "first": {
          "type": "string",
          "description": "The primary key to sort by (e.g., 'age', 'price', 'date')."
        },
        "second": {
          "type": "string",
          "description": "The secondary key to sort by in case of a tie (e.g., 'name', 'timestamp')."
        }
      },
      "required": ["json_array", "first", "second"]
    }
  }
},{
    "type": "function",
    "function": {
        "name": "convert_txt_to_json_hash",
        "description": "Reads a text file, converts key-value pairs separated by '=' into a JSON object, and returns the SHA-256 hash of the JSON string.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "process_files_and_sum_symbols",
        "description": "Extracts a ZIP file containing multiple encoded data files, reads their content, and sums the values associated with specified symbols.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_symbols": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of symbols to match against in the files."
                }
            },
            "required": ["target_symbols"]
        }
    }
},{
    "type": "function",
    "function": {
        "name": "sum_data_value",
        "description": "Parses HTML content and sums up the numeric values of the 'data-value' attribute from all <div> elements with class 'foo'. The input can be either a file path or a string containing HTML. If no input is provided, the function returns None.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_data": {
                    "type": "string",
                    "description": "if html content present in the query return the html else return NoneThe HTML content as a string as a part of a query return HTML content. If not provided, the function returns None."
                },
                "is_file": {
                    "type": "boolean",
                    "description": "Indicates whether the input_data is a file path (True) or HTML content (False). Default is False."
                }
            },
            "required": ['input_data',"is_file"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "commit_and_push_file",
        "description": "Commits a given file with specified content to a public GitHub repository and returns the raw URL of the file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_name": {
                    "type": "string",
                    "description": "The name of the file to be created and committed to GitHub (e.g., 'email.json')."
                },
                "file_content": {
                    "type": "object",
                    "description": "The content to be written in the file as a JSON object.Note that the file content will given in the query.(e.g,.JSON file called email.json with the value {'email': '23f2004462@ds.study.iitm.ac.in'} here the content is {'email': '23f2004462@ds.study.iitm.ac.in'} )"
                }
            },
            "required": ["file_name", "file_content"]
            
        }
    }
},{
    "type": "function",
    "function": {
        "name": "compare_files_in_zip",
        "description": "Extracts a ZIP file and compares the contents of 'a.txt' and 'b.txt' line by line, returning the number of differing lines.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "process_zip_and_rename",
        "description": "Extracts a ZIP file, moves all files into a single folder, renames files by incrementing digits, and computes a checksum using a sorted file content hash.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",#15
    "function": {
        "name": "process_zip_and_calculate_size",
        "description": "Calculate the total size of files in an extracted ZIP that are at least a given size and modified on or after a specified date.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_size": {
                    "type": "integer",
                    "description": "The minimum file size in bytes for a file to be included in the total size calculation."
                },
                "date_threshold": {
                    "type": "string",
                    "description": "The modification date threshold. Only files modified on or after this date (in 'Day, DD Mon, YYYY, HH:MM AM/PM IST' format) will be considered."
                }
            },
            "required": ["min_size", "date_threshold"],
            "additionalProperties": False
        },
        "strict": True
    }
},
{
    "type": "function",
    "function": {
        "name": "process_zipped_file",
        "description": "Extracts a ZIP file into a uniquely named folder, replaces occurrences of 'IITM' with 'IIT Madras' in all text files, and calculates the SHA-256 checksum of the extracted files.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    }
},
{
    "type": "function",
    "function": {
        "name": "get_total_sales_sql",
        "description": "Generate an SQL query to calculate the total sales for a given ticket type, ignoring case and spaces.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticket_type": {
                    "type": "string",
                    "description": "The ticket type to filter by (e.g., 'Gold', 'Silver'). Case and spaces are ignored."
                }
            },
            "required": ["ticket_type"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "fetch_markdown",
        "description": "Fetches a Markdown document from the AI API based on the given task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The description of the documentation required."
                }
            },
            "required": ["task"]
        }
    }
},{
    "type": "function",
    "function": {
        "name": "compress_image_to_base64",
        "description": "Compresses an image and converts it to a Base64 string while ensuring the file size remains within the specified limit.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The URL or local file path of the image to be compressed and converted."
                },
                "max_size": {
                    "type": "integer",
                    "description": "Maximum allowed size in bytes for the compressed image."
                }
            },
            "required": ["file_path"]
        }
    }
},{
    "type": "function",
    "function": {
        "name": "generate_hash",
        "description": "Generate a 5-character hash based on an email and an optional token expiry year.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The email address for which the hash needs to be generated."
                },
                "expiry_year": {
                    "type": "string",
                    "description": "The expiry year for the hash (default: '2025' if not provided)."
                }
            },
            "required": ["email"]
        }
    }
},{
    "type": "function",
    "function": {
        "name": "count_light_pixels",
        "description": "Counts the number of pixels with lightness > 0.662 in an image.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The URL or local file path of the image to be analyzed."
                }
            },
            "required": ["file_path"]
        }
    }
},{
    "type": "function",
    "function": {
        "name": "push_github_action",
        "description": "Creates and pushes a GitHub Actions workflow file, then returns the action URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "User email to include in the workflow."}
            },
            "required": ["email"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "push_docker_image",
        "description": "Builds, tags, and pushes a Docker image to Docker Hub, then returns its URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_name": {
                    "type": "string",
                    "description": "The name of the Docker image to push."
                }
            },
            "required": ["image_name"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "run_llamafile_with_ngrok",
        "description": "Runs Llamafile with the given model and exposes it via ngrok, returning the public URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "model_path": {
                    "type": "string",
                    "description": "Path to the Llamafile model."
                },
                "port": {
                    "type": "integer",
                    "description": "Port number to expose the Llamafile server. If not provided, the function will use port 8080."
                }
            },
            "required": []
        }
    }
},{
    "type": "function",
    "function": {
    "name": "count_tokens",
    "description": "Counts the number of tokens in a given text using the GPT-4 tokenizer.",
    "parameters": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "description": "The input text to be tokenized."
        }
      },
      "required": ["text"]
    }
  }
},{
    "type": "function",
    "function": {
        "name": "create_openai_request",
        "description": "Creates a JSON body for an OpenAI API request using GPT-4o-mini.",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path_or_base64": {
                    "type": "string",
                    "description": "Either the image file path or a base64-encoded image string."
                }
            },
            "required": ["image_path_or_base64"],
            "additionalProperties": False
        },
        "strict": True
    }
},{
    "type": "function",
    "function": {
        "name": "create_embedding_json",
        "description": "Creates a JSON structure for text embeddings using 'text-embedding-3-small'.",
        "parameters": {
            "type": "object",
            "properties": {
                "value1": {
                    "type": "string",
                    "description": "The first text input for embedding."
                },
                "value2": {
                    "type": "string",
                    "description": "The second text input for embedding."
                }
            },
            "required": ["value1", "value2"],
            "additionalProperties": False
        }
    }
},{
  "type": "function",
  "function": {
    "name": "fetch_function",
    "description": "Fetches a Python function from the AI API based on the given task.",
    "parameters": {
      "type": "object",
      "properties": {
        "task": {
          "type": "string",
          "description": "The description of the function required."
        }
      },
      "required": ["task"]
    }
  }
},{
  "type": "function",
  "function": {
    "name": "fetch_cricinfo_ducks",
    "description": "Fetches ODI batting statistics from ESPN Cricinfo and counts total ducks on the given page.",
    "parameters": {
      "type": "object",
      "properties": {
        "page_number": {
          "type": "integer",
          "description": "The page number to fetch statistics from."
        }
      },
      "required": ["page_number"]
    }
  }
},{
  "type": "function",
  "function": {
    "name": "extract_top_25_movies",
    "description": "Extracts the top 25 movies from the given IMDb URL.",
    "parameters": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "The IMDb search URL."
        }
      },
      "required": ["url"]
    }
  }
},{
  "type": "function",
  "function": {
    "name": "fetch_bbc_weather_summary",
    "description": "Fetches BBC Weather summary for a given city.",
    "parameters": {
      "type": "object",
      "properties": {
        "required_city": {
          "type": "string",
          "description": "The city for which to fetch the weather summary."
        }
      },
      "required": ["required_city"]
    }
  }
},{
  "type": "function",
  "function": {
    "name": "get_max_latitude",
    "description": "Fetches the latitude of a given city in a specified country.",
    "parameters": {
      "type": "object",
      "properties": {
        "country": {
          "type": "string",
          "description": "The name of the country."
        },
        "city": {
          "type": "string",
          "description": "The name of the city."
        }
      },
      "required": ["country", "city"]
    }
  }
},{
    "type": "function",
    "function": {
      "name": "fetch_hacker_news_post",
      "description": "Fetches a Hacker News post with at least the specified number of points.",
      "parameters": {
        "type": "object",
        "properties": {
          "min_points": {
            "type": "integer",
            "description": "The minimum number of points required for the post."
          }
        },
        "required": ["min_points"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "compute_total_subject_marks",
      "description": "Computes the total marks of a subject for students who scored a minimum threshold in another subject.",
      "parameters": {
        "type": "object",
        "properties": {
          "start_group": {
            "type": "integer",
            "description": "Starting group number to consider in the dataset."
          },
          "end_group": {
            "type": "integer",
            "description": "Ending group number to consider in the dataset."
          },
          "subject_filter": {
            "type": "string",
            "description": "The subject used for filtering students based on marks."
          },
          "min_mark": {
            "type": "integer",
            "description": "The minimum marks required in the filtering subject."
          },
          "total_subject_mark": {
            "type": "string",
            "description": "The subject whose total marks need to be computed."
          }
        },
        "required": ["start_group", "end_group", "subject_filter", "min_mark", "total_subject_mark"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "process_file",
      "description": "Processes an Excel file, cleans and filters data based on product, country, and date, and calculates the total margin.",
      "parameters": {
        "type": "object",
        "properties": {
          "product": {
            "type": "string",
            "description": "Product name to filter."
          },
          "country": {
            "type": "string",
            "description": "Country to filter."
          },
          "filter_date": {
            "type": "string",
            "format": "date",
            "description": "Filter transactions up to this date (YYYY-MM-DD format)."
          }
        },
        "required": ["product", "country", "filter_date"]
      }
    }
  }
,{
  "type": "function",
  "function": {
    "name": "count_unique_students",
    "description": "Counts the number of unique student IDs from a given text file and returns the result as a JSON string.",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "Path to the text file containing student records."
        }
      },
      "required": ["file_path"]
    }
  }
},{
    "type": "function",
    "function": {
      "name": "count_successful_requests",
      "description": "Counts the number of successful GET requests for a specific category in a log file during a given time range and day.",
      "parameters": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "description": "The category of the URL (e.g., 'hindi')."
          },
          "start_hour": {
            "type": "integer",
            "description": "The starting hour (24-hour format)."
          },
          "end_hour": {
            "type": "integer",
            "description": "The ending hour (exclusive, 24-hour format)."
          },
          "day": {
            "type": "string",
            "description": "The target day (e.g., 'Thursday')."
          }
        },
        "required": ["category", "start_hour", "end_hour", "day"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "process_log",
      "description": "Processes a log file to identify the top IP address by volume of downloads on a specific date for a given category.",
      "parameters": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string",
            "description": "The category of the URL (e.g., 'hindi')."
          },
          "target_date": {
            "type": "string",
            "description": "The date in 'YYYY-MM-DD' format to filter logs."
          }
        },
        "required": ["category", "target_date"]
      }
    }
  },{
    "type": "function",
    "function": {
      "name": "count_units_sold_in_city",
      "description": "Counts the total units of a specific product sold in a target city, considering fuzzy matching and a sales threshold.",
      "parameters": {
        "type": "object",
        "properties": {
          "target_city": {
            "type": "string",
            "description": "The name of the target city for which sales data needs to be analyzed (e.g., 'Tokyo')."
          },
          "product": {
            "type": "string",
            "description": "The name of the product to filter sales data (e.g., 'Pants')."
          },
          "sales_threshold": {
            "type": "integer",
            "description": "The minimum sales threshold to consider for counting units."
          }
        },
        "required": ["target_city", "product", "sales_threshold"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "count_key_occurrences",
      "description": "Counts occurrences of a specific key in a nested JSON structure.",
      "parameters": {
        "type": "object",
        "properties": {
          "json_data": {
            "type": "object",
            "description": "The nested JSON structure in which to count occurrences of the key."
          },
          "key_to_count": {
            "type": "string",
            "description": "The key to search for in the JSON data."
          }
        },
        "required": ["json_data", "key_to_count"]
      }
    }
  },{
  "type": "function",
  "function": {
    "name": "youtube_transcribe",
    "description": "Downloads audio from a YouTube video, extracts a segment, and transcribes it.",
    "parameters": {
      "type": "object",
      "properties": {
        "youtube_url": {
          "type": "string",
          "description": "The URL of the YouTube video."
        },
        "start_time": {
          "type": "integer",
          "description": "Start time of the segment in seconds."
        },
        "end_time": {
          "type": "integer",
          "description": "End time of the segment in seconds."
        }
      },
      "required": ["youtube_url", "start_time", "end_time"]
    }
  }
}
]