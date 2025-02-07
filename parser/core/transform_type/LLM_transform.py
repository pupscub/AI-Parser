# # LLM_transform.py
# import base64
# import io
# import mimetypes
# import os
# from typing import Dict, List

# import pypdfium2 as pdfium
# import requests

# # from parser.core.prompt_templates import (
# #     # INSTRUCTIONS_ADD_PG_BREAK,
# #     OPENAI_USER_PROMPT,
# #     PARSER_PROMPT,
# #     REFORMAT_PROMPT
# # )

# from loguru import logger
# from openai import OpenAI


# REFORMAT_PROMPT = f"""\
# Act as a data transformation expert. Transform the input dataframe to match the following master format:

# Required Columns:
# - country: Country name
# - source_organization: Origin of the data (derived from source URL/table info)
# - admin_0: Country-level region
# - admin_1: State/province-level region
# - admin_2: District/county-level region
# - start_date: Primary date (minimum requirement: harvest year)
# - period_date: Secondary date reference
# - collection_date: Data collection timestamp
# - season_date: Growing season timestamp
# - season_year: Year of growing season
# - indicator: One of [quantity produced, area planted, yield]
# - value: Numeric value of the indicator
# - product: Crop type
# - unit: Unit of measurement for the indicator

# Rules:
# 1. Map existing column names to the master format using fuzzy matching
# 2. Perform necessary pivoting/melting operations if data is in wide format
# 3. Standardize date columns to ISO format (YYYY-MM-DD)
# 4. Ensure indicator values are one of: quantity produced, area planted, or yield
# 5. Fill missing admin levels with appropriate higher-level values
# 6. Extract source organization from metadata if available
# 7. Validate units match the indicator type
# """

# def transform_data(document, model: str, ):
#     if model.startswith("gemini"):
#         return transform_with_gemini(document, model)
#     elif model.startswith("gpt"):
#         return transform_with_gpt(document)
#     elif model.startswith("deepseek"):
#         return transform_with_deepseek(document)
#     else:
#         raise ValueError(f"Unsupported model: {model}")
    

# def transform_with_gemini(document: str, model: str):
#     api_key = os.environ.get("GOOGLE_API_KEY")
#     if not api_key:
#         raise ValueError("GOOGLE_API_KEY environment variable is not set")

#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

#     with open(document, "r") as file:
#         file_content = file.read()

#     encoded_content = base64.b64encode(file_content.encode()).decode()

#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {"text": "Please summarize the text below."},
#                     {
#                         "inline_data": {
#                             "mime_type": "text/plain",
#                             "data": encoded_content
#                         }
#                     }
#                 ]
#             }
#         ],
#         "generationConfig": {"temperature": 0.3}
#     }
#     headers = {"Content-Type": "application/json"}

#     response = requests.post(url, json=payload, headers=headers)
#     response.raise_for_status()
#     return response.json()


# def transform_with_gpt(document):
#     pass

# def transform_with_deepseek(document): # Temperate 1.0 for document cleaning task
#     pass


# # def parse_llm_doc(path: str, raw: bool, **kwargs) -> List[Dict] | str:
# #     if "model" not in kwargs:
# #         kwargs["model"] = "gemini-1.5-flash"
# #     model = kwargs.get("model")
# #     if model.startswith("gemini"):
# #         return parse_with_gemini(path, raw, **kwargs)
# #     elif model.startswith("gpt"):
# #         return parse_with_gpt(path, raw, **kwargs)
# #     else:
# #         raise ValueError(f"Unsupported model: {model}")


# # def parse_with_gemini(path: str, raw: bool, **kwargs) -> List[Dict] | str:
# #     api_key = os.environ.get("GOOGLE_API_KEY")
# #     if not api_key:
# #         raise ValueError("GOOGLE_API_KEY environment variable is not set")

# #     url = f"https://generativelanguage.googleapis.com/v1beta/models/{kwargs['model']}:generateContent?key={api_key}"

# #     # Check if the file is an image and convert to PDF if necessary
# #     mime_type, _ = mimetypes.guess_type(path)
# #     if mime_type and mime_type.startswith("image"):
# #         pdf_content = convert_image_to_pdf(path)
# #         mime_type = "application/pdf"
# #         base64_file = base64.b64encode(pdf_content).decode("utf-8")
# #     else:
# #         with open(path, "rb") as file:
# #             file_content = file.read()
# #             # print(file_content)
# #         base64_file = base64.b64encode(file_content).decode("utf-8")

# #     # Ideally, we do this ourselves. But, for now this might be a good enough.
# #     # custom_instruction = f"""- Total number of pages: {kwargs["pages_per_split"]}. {INSTRUCTIONS_ADD_PG_BREAK}"""
# #     if kwargs["pages_per_split"] == 1:
# #         custom_instruction = ""
# #     # print(PARSER_PROMPT)
# #     payload = {
# #         "contents": [
# #             {
# #                 "parts": [
# #                     {
# #                         # "text": PARSER_PROMPT.format(
# #                         #     custom_instructions=custom_instruction
# #                         # )
# #                         "text": PARSER_PROMPT
                        
# #                     },
# #                     {"inline_data": {"mime_type": mime_type, "data": base64_file}},
# #                 ]
# #             }
# #         ],
# #         "generationConfig": {
# #             "temperature": kwargs.get("temperature", 0.7),
# #         },
# #     }

# #     headers = {"Content-Type": "application/json"}

# #     response = requests.post(url, json=payload, headers=headers)
# #     response.raise_for_status()

# #     result = response.json()

# #     raw_text = "".join(
# #         part["text"]
# #         for candidate in result.get("candidates", [])
# #         for part in candidate.get("content", {}).get("parts", [])
# #         if "text" in part
# #     )

# #     result = ""
# #     if "<output>" in raw_text:
# #         result = raw_text.split("<output>")[1].strip()
# #     if "</output>" in result:
# #         result = result.split("</output>")[0].strip()

# #     if raw:
# #         return result

# #     return [
# #         {
# #             "metadata": {
# #                 "title": kwargs["title"],
# #                 "page": kwargs.get("start", 0) + page_no,
# #             },
# #             "content": page,
# #         }
# #         for page_no, page in enumerate(result.split("<page-break>"), start=1)
# #         if page.strip()
# #     ]


# # def convert_pdf_page_to_base64(
# #     pdf_document: pdfium.PdfDocument, page_number: int
# # ) -> str:
# #     """Convert a PDF page to a base64-encoded PNG string."""
# #     page = pdf_document[page_number]
# #     # Render with 4x scaling for better quality
# #     pil_image = page.render(scale=4).to_pil()

# #     # Convert to base64
# #     img_byte_arr = io.BytesIO()
# #     pil_image.save(img_byte_arr, format="PNG")
# #     img_byte_arr.seek(0)
# #     return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")


# # def parse_with_gpt(path: str, raw: bool, **kwargs) -> List[Dict] | str:
# #     client = OpenAI()

# #     # Handle different input types
# #     mime_type, _ = mimetypes.guess_type(path)
# #     if mime_type and mime_type.startswith("image"):
# #         # Single image processing
# #         with open(path, "rb") as img_file:
# #             image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
# #             images = [(0, image_base64)]
# #     else:
# #         # PDF processing
# #         pdf_document = pdfium.PdfDocument(path)
# #         images = [
# #             (page_num, convert_pdf_page_to_base64(pdf_document, page_num))
# #             for page_num in range(len(pdf_document))
# #         ]

# #     # Process each page/image
# #     all_results = []
# #     for page_num, image_base64 in images:
# #         messages = [
# #             {
# #                 "role": "system",
# #                 "content": PARSER_PROMPT,
# #             },
# #             {
# #                 "role": "user",
# #                 "content": [
# #                     {
# #                         "type": "text",
# #                         "text": f"{OPENAI_USER_PROMPT} (Page {page_num + 1})",
# #                     },
# #                     {
# #                         "type": "image_url",
# #                         "image_url": {"url": f"data:image/png;base64,{image_base64}"},
# #                     },
# #                 ],
# #             },
# #         ]

# #         # Get completion from GPT-4 Vision
# #         response = client.chat.completions.create(
# #             model=kwargs["model"],
# #             temperature=kwargs.get("temperature", 0.7),
# #             messages=messages,
# #         )

# #         # Extract the response text
# #         page_text = response.choices[0].message.content
# #         if kwargs.get("verbose", None):
# #             logger.debug(f"Page {page_num + 1} response: {page_text}")
# #         result = ""
# #         if "<output>" in page_text:
# #             result = page_text.split("<output>")[1].strip()
# #         if "</output>" in result:
# #             result = result.split("</output>")[0].strip()
# #         all_results.append((page_num, result))

# #     # Sort results by page number and combine
# #     all_results.sort(key=lambda x: x[0])
# #     all_texts = [text for _, text in all_results]
# #     combined_text = "<page-break>".join(all_texts)

# #     if raw:
# #         return combined_text

# #     return [
# #         {
# #             "metadata": {
# #                 "title": kwargs["title"],
# #                 "page": kwargs.get("start", 0) + page_no,
# #             },
# #             "content": page,
# #         }
# #         for page_no, page in enumerate(all_texts, start=1)
# #         if page.strip()
# #     ]


# output  = transform_with_gemini("/Users/adityasingh/Documents/Work/Havard/Parser/Parser/output/1960-69.csv","gemini-1.5-flash")
# print(output)
