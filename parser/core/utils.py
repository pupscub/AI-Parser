import io
import mimetypes
import os
import re
import sys
from difflib import SequenceMatcher
from typing import Union, List, Dict
from urllib.parse import urlparse
import pikepdf
import pypdfium2
import requests
from bs4 import BeautifulSoup
from markdown import markdown
from markdownify import markdownify as md
from PIL import Image
from PyQt5.QtCore import QMarginsF, QUrl
from PyQt5.QtGui import QPageLayout, QPageSize
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication
from parser.core.pricing import PRICING
import tiktoken

print(PRICING)

# Source: https://stackoverflow.com/a/12982689
HTML_TAG_PATTERN = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")


def split_pdf(input_path: str, output_dir: str, pages_per_split: int):
    paths = []
    with pikepdf.open(input_path) as pdf:
        total_pages = len(pdf.pages)
        for start in range(0, total_pages, pages_per_split):
            end = min(start + pages_per_split, total_pages)
            output_path = os.path.join(
                output_dir, f"split_{str(start + 1).zfill(4)}_{end}.pdf"
            )
            with pikepdf.new() as new_pdf:
                new_pdf.pages.extend(pdf.pages[start:end])
                new_pdf.save(output_path)
                paths.append(output_path)
    return paths


def convert_image_to_pdf(image_path: str) -> bytes:
    with Image.open(image_path) as img:
        img_rgb = img.convert("RGB")
        pdf_buffer = io.BytesIO()
        img_rgb.save(pdf_buffer, format="PDF")
        return pdf_buffer.getvalue()


def remove_html_tags(text: str):
    html = markdown(text, extensions=["tables"])
    return re.sub(HTML_TAG_PATTERN, "", html)


def calculate_similarity(text1: str, text2: str, ignore_html=True) -> float:
    """Calculate similarity ratio between two texts using SequenceMatcher."""
    if ignore_html:
        text1 = remove_html_tags(text1)
        text2 = remove_html_tags(text2)
    return SequenceMatcher(None, text1, text2).ratio()


def convert_pdf_page_to_image(
    pdf_document: pypdfium2.PdfDocument, page_number: int
) -> bytes:
    """Convert a PDF page to an image."""
    page = pdf_document[page_number]
    # Render with 4x scaling for better quality
    pil_image = page.render(scale=4).to_pil()

    # Convert to bytes
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()


def is_supported_file_type(url: str) -> bool:
    """
    Check if the file type from the URL is supported.

    Args:
        url (str): The URL of the file.

    Returns:
        bool: True if the file type is supported, False otherwise.
    """
    supported_extensions = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"]
    parsed_url = urlparse(url)
    ext = os.path.splitext(parsed_url.path)[1].lower()

    if ext in supported_extensions:
        return True

    # If no extension in URL, try to get content type from headers
    response = requests.head(url)
    content_type = response.headers.get("Content-Type", "")
    ext = mimetypes.guess_extension(content_type)

    return ext in supported_extensions


def download_file(url: str, temp_dir: str) -> str:
    """
    Downloads a file from the given URL and saves it to a temporary directory.

    Args:
        url (str): The URL of the file to download.
        temp_dir (str): The temporary directory to save the file.

    Returns:
        str: The path to the downloaded file.
    """
    response = requests.get(url)
    file_name = os.path.basename(urlparse(url).path)
    if not file_name:
        content_type = response.headers.get("Content-Type", "")
        ext = mimetypes.guess_extension(content_type)
        file_name = f"downloaded_file{ext}" if ext else "downloaded_file"

    file_path = os.path.join(temp_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(response.content)
    return file_path


def find_dominant_heading_level(markdown_content: str) -> str:
    """
    Finds the most common heading level that occurs more than once.
    Also checks for underline style headings (---).

    Args:
        markdown_content (str): The markdown content to analyze

    Returns:
        str: The dominant heading pattern (e.g., '##' or 'underline')
    """
    # Check for underline style headings first
    underline_pattern = r"^[^\n]+\n-+$"
    underline_matches = re.findall(underline_pattern, markdown_content, re.MULTILINE)
    if len(underline_matches) > 1:
        return "underline"

    # Find all hash-style headings in the markdown content
    heading_patterns = ["#####", "####", "###", "##", "#"]
    heading_counts = {}

    for pattern in heading_patterns:
        # Look for headings at the start of a line
        regex = f"^{pattern} .*$"
        matches = re.findall(regex, markdown_content, re.MULTILINE)
        if len(matches) > 1:  # Only consider headings that appear more than once
            heading_counts[pattern] = len(matches)

    if not heading_counts:
        return "#"  # Default to h1 if no repeated headings found

    return min(heading_counts.keys(), key=len)


def split_by_headings(
    url: str, markdown_content: str, heading_pattern: str
) -> List[Dict]:
    """
    Splits markdown content by the specified heading pattern and structures it.

    Args:
        url (str): The URL of the HTML page
        markdown_content (str): The markdown content to split
        heading_pattern (str): The heading pattern to split on (e.g., '##' or 'underline')

    Returns:
        List[Dict]: List of dictionaries containing metadata and content
    """
    structured_content = []

    if heading_pattern == "underline":
        # Split by underline headings
        pattern = r"^([^\n]+)\n-+$"
        sections = re.split(pattern, markdown_content, flags=re.MULTILINE)
        # Remove empty sections and strip whitespace
        sections = [section.strip() for section in sections if section.strip()]

        # Handle content before first heading if it exists
        if sections and not re.match(r"^[^\n]+\n-+$", sections[0], re.MULTILINE):
            structured_content.append(
                {
                    "metadata": {"title": url, "page": "Introduction"},
                    "content": sections.pop(0),
                }
            )

        # Process sections pairwise (heading, content)
        for i in range(0, len(sections), 2):
            if i + 1 < len(sections):
                structured_content.append(
                    {
                        "metadata": {"title": url, "page": sections[i]},
                        "content": sections[i + 1],
                    }
                )
    else:
        # Split by hash headings
        regex = f"^{heading_pattern} .*$"
        sections = re.split(regex, markdown_content, flags=re.MULTILINE)
        headings = re.findall(regex, markdown_content, flags=re.MULTILINE)

        # Remove empty sections and strip whitespace
        sections = [section.strip() for section in sections if section.strip()]

        # Handle content before first heading if it exists
        if len(sections) > len(headings):
            structured_content.append(
                {
                    "metadata": {"title": url, "page": "Introduction"},
                    "content": sections.pop(0),
                }
            )

        # Process remaining sections
        for heading, content in zip(headings, sections):
            clean_heading = heading.replace(heading_pattern, "").strip()
            structured_content.append(
                {"metadata": {"title": url, "page": clean_heading}, "content": content}
            )

    return structured_content


def read_html_content(url: str, raw: bool = False) -> Union[str, List[Dict]]:
    """
    Reads the content of an HTML page from the given URL and converts it to markdown or structured content.

    Args:
        url (str): The URL of the HTML page.
        raw (bool): Whether to return raw markdown text or structured data.

    Returns:
        Union[str, List[Dict]]: Either raw markdown content or structured data with metadata and content sections.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="iso-8859-1")
    markdown_content = md(str(soup))

    if raw:
        return markdown_content

    # Find the dominant heading level
    heading_pattern = find_dominant_heading_level(markdown_content)

    # Split content by headings and structure it
    return split_by_headings(url, markdown_content, heading_pattern)


def extract_urls_from_markdown(content: str) -> List[str]:
    """
    Extracts URLs from markdown content using regex.
    Matches both [text](url) and bare http(s):// URLs.

    Args:
        content (str): Markdown content to search for URLs

    Returns:
        List[str]: List of unique URLs found
    """
    # Match markdown links [text](url) and bare URLs
    markdown_pattern = r"\[([^\]]+)\]\((https?://[^\s\)]+)\)"
    bare_url_pattern = r"(?<!\()(https?://[^\s\)]+)"

    urls = []
    # Extract URLs from markdown links
    urls.extend(match.group(2) for match in re.finditer(markdown_pattern, content))
    # Extract bare URLs
    urls.extend(match.group(0) for match in re.finditer(bare_url_pattern, content))

    return list(set(urls))  # Remove duplicates


def recursive_read_html(
    url: str, depth: int, raw: bool, visited_urls: set = None
) -> Union[str, List[Dict]]:
    """
    Recursively reads HTML content from URLs up to specified depth.

    Args:
        url (str): The URL to parse
        depth (int): How many levels deep to recursively parse
        raw (bool): Whether to return raw text or structured data
        visited_urls (set): Set of already visited URLs to prevent cycles

    Returns:
        Union[str, List[Dict]]: Combined content from all parsed URLs
    """
    if visited_urls is None:
        visited_urls = set()

    if url in visited_urls:
        return "" if raw else []

    visited_urls.add(url)

    try:
        content = read_html_content(url, raw)
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return "" if raw else []

    if depth <= 1:
        return content

    # Extract URLs from the content
    if raw:
        urls = extract_urls_from_markdown(content)
    else:
        # Extract URLs from all content sections
        urls = []
        for doc in content:
            urls.extend(extract_urls_from_markdown(doc["content"]))

    # Recursively process each URL
    for sub_url in urls:
        if sub_url not in visited_urls:
            sub_content = recursive_read_html(sub_url, depth - 1, raw, visited_urls)

            if raw:
                if sub_content:
                    content += f"\n\n--- Begin content from {sub_url} ---\n\n"
                    content += sub_content
                    content += f"\n\n--- End content from {sub_url} ---\n\n"
            else:
                if isinstance(sub_content, list):
                    content.extend(sub_content)

    return content


def save_webpage_as_pdf(url: str, output_path: str) -> str:
    """
    Saves a webpage as a PDF file using PyQt5.

    Args:
        url (str): The URL of the webpage.
        output_path (str): The path to save the PDF file.

    Returns:
        str: The path to the saved PDF file.
    """
    app = QApplication(sys.argv)
    web = QWebEngineView()
    web.load(QUrl(url))

    def handle_print_finished(filename, status):
        print(f"PDF saved to: {filename}")
        app.quit()

    def handle_load_finished(status):
        if status:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(output_path)

            page_layout = QPageLayout(
                QPageSize(QPageSize.A4), QPageLayout.Portrait, QMarginsF(15, 15, 15, 15)
            )
            printer.setPageLayout(page_layout)

            web.page().printToPdf(output_path)
            web.page().pdfPrintingFinished.connect(handle_print_finished)

    web.loadFinished.connect(handle_load_finished)
    app.exec_()

    return output_path


def convert_to_pdf(input_path: str, output_path: str) -> str:
    """
    Converts a file or webpage to PDF.

    Args:
        input_path (str): The path to the input file or URL.
        output_path (str): The path to save the output PDF file.

    Returns:
        str: The path to the saved PDF file.
    """
    if input_path.startswith(("http://", "https://")):
        return save_webpage_as_pdf(input_path, output_path)
    elif input_path.lower().endswith(
        (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")
    ):
        img_data = convert_image_to_pdf(input_path)
        with open(output_path, "wb") as f:
            f.write(img_data)
    else:
        # Assume it's already a PDF, just copy it
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())

    return output_path


def has_image_in_pdf(path: str):
    with open(path, "rb") as fp:
        content = fp.read()
    return "Image".lower() in list(
        map(lambda x: x.strip(), (str(content).lower().split("/")))
    )


def has_hyperlink_in_pdf(path: str):
    with open(path, "rb") as fp:
        content = fp.read()
    # URI tag is used if Links are hidden.
    return "URI".lower() in list(
        map(lambda x: x.strip(), (str(content).lower().split("/")))
    )


def router(path: str):
    # Naive routing strategy for now.
    # Current routing strategy,
    # 1. If the PDF has hidden hyperlinks (as alias) and no images: STATIC_PARSE
    # 2. Other scenarios: LLM_PARSE
    # If you have other needs, do reach out or create an issue.
    if not has_image_in_pdf(path) and has_hyperlink_in_pdf(path):
        return "STATIC_PARSE"
    return "LLM_PARSE"


def get_uri_rect(path):
    with open(path, "rb") as fp:
        byte_str = str(fp.read())
    pattern = r"\((https?://[^\s)]+)\)"
    uris = re.findall(pattern, byte_str)
    rect_splits = byte_str.split("/Rect [")[1:]
    rects = [
        list(map(float, rect_split.split("]")[0].split())) for rect_split in rect_splits
    ]
    return {uri: rect for uri, rect in zip(uris, rects)}


# encoder = tiktoken.encoding_for_model(selected_model)
# input_token_count = len(encoder.encode(USER_MESSAGE + data))


def calulcate_price(token_counts, model):
    input_token_count = token_counts.get("input_tokens", 0)
    output_token_count = token_counts.get("output_tokens", 0)
    
    # Calculate the costs
    input_cost = input_token_count * PRICING[model]["input"]
    output_cost = output_token_count * PRICING[model]["output"]
    total_cost = input_cost + output_cost
    
    return input_token_count, output_token_count, total_cost