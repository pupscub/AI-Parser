import streamlit as st
import os
from parser.api import parse
from parser.api import ParserType
from dotenv import load_dotenv
from parser.core.utils import get_token_count ,calculate_price
# Load environment variables
load_dotenv()

# Initialize Streamlit app
st.set_page_config(page_title="AI-Scraper")
st.title("AI-Scraper")


# Function to parse PDF from path
def parse_pdf_path(pdf_path: str, model_name: str,parser_type: str,framework: str = None) -> str:
    file_name = pdf_path.split('/')[-1]
    file_name = os.path.splitext(file_name)[0]

    file = parse(path=pdf_path, 
                 parser_type=parser_type, 
                 raw=True, 
                 model=model_name,
                 framework=framework)
    return file, file_name

# Function to parse PDF from URL
def parse_pdf_url(pdf_url: str, model_name: str):
    file_name = pdf_url.split('/')[-1]
    file_name = os.path.splitext(file_name)[0]
    file = parse(pdf_url, parser_type="LLM_PARSE", raw=True, model=model_name)
    return file, file_name

# Convert parsed markdown to CSV and save the file in output directory
def convert_md_to_csv(file_content, file_name):
    output_dir = "output"
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create the full path for the output file
    output_file_path = os.path.join(output_dir, file_name + ".csv")
    
    # Write the content to a CSV file
    with open(output_file_path, "w") as f:
        f.write(file_content)
    print(f"CSV file saved at: {output_file_path}")
    return output_file_path

def main():
    st.title('Parser')

    # Field to enter Page URL or upload PDF
    url = st.text_input('Enter Page URL')
    uploaded_file = st.file_uploader('Upload a PDF file', type='pdf')
    parser_type = st.selectbox("Select the Parser Type",["LLM_PARSE", "STATIC_PARSE","AUTO"])
    if parser_type == "AUTO" or parser_type == "LLM_PARSE":
        framework = None
    if parser_type == "STATIC_PARSE":
        framework = st.selectbox("Pick any of the following Python Libraries",["pymupdf","pdfminer","pdfplumber"])  # Replace with actual parser types

    # Select model name (assuming you have multiple models)
    model_name = st.selectbox("Select Model", ["gemini-1.5-flash", "gpt-4o-mini","gpt-4o-2024-08-06","deepseek-chat", "deepseek-reasoner"])  # Replace with actual model names

    if st.button('Process'):
        if url:
            with st.spinner('Processing URL...'):
                try:
                    parsed_content, file_name = parse_pdf_url(url, 
                                                              model_name,
                                                              parser_type,
                                                              framework)
                    csv_path = convert_md_to_csv(parsed_content, file_name)
                    st.success('Processing complete!')
                    
                    # Provide download link for the processed CSV file
                    with open(csv_path, 'rb') as f:
                        st.download_button(
                            label="Download Processed CSV",
                            data=f,
                            file_name=file_name + ".csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    print("This is the value stored in e:",e)
                    st.error(f"Error processing URL: {e}")

        elif uploaded_file is not None:
            with st.spinner('Processing File...'):
                try:
                    # Save uploaded file temporarily
                    if not os.path.exists("input"):
                         os.makedirs("input/")
                    temp_file_path = os.path.join("input", uploaded_file.name)
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.read())
                    parsed_content, file_name = parse_pdf_path(temp_file_path, 
                                                               model_name,
                                                               parser_type,
                                                               framework)
                    csv_path = convert_md_to_csv(parsed_content, file_name)
                    st.success('Processing complete!')
                    
                    # Provide download link for the processed CSV file
                    with open(csv_path, 'rb') as f:
                        st.download_button(
                            label="Download Processed CSV",
                            data=f,
                            file_name=file_name + ".csv",
                            mime="text/csv"
                        )
                    token_counts = get_token_count(input_file_path=temp_file_path, 
                                                   output=parsed_content,
                                                   model_name=model_name)
                    total_input_tokens = token_counts["input_tokens"]
                    total_output_tokens = token_counts["output_tokens"]
                    total_cost = calculate_price(token_counts = token_counts,
                                                 model_name=model_name)
                    # Show the pricing of the selected model in random colors 
                except Exception as e:
                    st.error(f"Error processing uploaded file: {e}")
                st.markdown("#### Token Usage and Pricing")
                st.markdown(f"*Input Tokens:* {total_input_tokens}")
                st.markdown(f"*Output Tokens:* {total_output_tokens}")
                st.markdown(f"**Total Cost:** :green-background[**${total_cost:.4f}**]")
if __name__ == '__main__':
    main()
