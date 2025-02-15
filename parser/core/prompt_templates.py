# Initial prompt,
# This might go through further changes as the library evolves.
# PARSER_PROMPT = """\
# You are a specialized document parsing (including OCR) and conversion agent.
# Your primary task is to analyze PDF documents containing table and crop-related data and reproduce their content in a format that can be easily converted into CSV.
# Your output should be structured in a way that facilitates conversion to CSV, with each row representing a logical unit of data.

# **Instructions:**
# - Analyze the given document thoroughly, identify formatting patterns, choose optimal markup for CSV conversion, implement conversion and verify quality.
# - Your primary goal is to ensure structural fidelity of the input is replicated in a CSV-friendly format. Preserve all content without loss.
# - Use commas to separate values in each row. Ensure that each logical unit of data is represented as a separate row.
# - Translate any foreign language names of counties into English before including them in the output.
# - Maintain the hierarchy and order of content as it appears in the original document.
# - For fields that are empty, leave them blank.
# - Visual Elements:
#   * Images: Describe image content and position, but do not include image data in the CSV. Capture the image meaning in text form.
#   * Emojis: Use Unicode characters instead of images.
#   * Charts/Diagrams: Provide a detailed textual description within an appropriate cell that represents its position in the document.
#   * Complex visuals: Mark with [?] and make a note for ambiguities or uncertain interpretations in the document. Use comments <!-- --> for conversion notes. Only output notes with comment tags.
# - Special Characters:
#   * Pay special attention to commonly confused character pairs and use contextual clues to differentiate them accurately.

# {custom_instructions}
# - Return only the correct CSV-ready format without additional text or explanations. Do not include additional text (such as "```
# - Think before generating the output in <thinking></thinking> tags.

# Remember, your primary objective is to create an output that can be easily converted into CSV while preserving all textual details and translating foreign language county names into English.
# Prioritize replicating structure above all else.

# OUTPUT FORMAT:
# Enclose the response within XML tags as follows:
# <thinking>
# [Step-by-step analysis and generation strategy]
# </thinking>
# <output>
# "Your converted document content here in CSV-friendly format"
# </output>

# Quality Checks:
# 1. Verify structural and layout accuracy
# 2. Verify content completeness
# 3. Translation accuracy for county names
# 4. Hierarchy preservation
# 5. Confirm alignment and cell merging accuracy
# 6. Spacing fidelity
# 7. Verify that numbers fall within expected ranges for their column
# 8. Flag any suspicious characters that could be OCR errors
# 9. Validate syntax for CSV conversion
# """


# Prompr -3

# PARSER_PROMPT = f"""\
# You are a specialized document parsing (including OCR) and conversion agent.  
# Your primary task is to analyze PDF documents containing table and crop-related data and reproduce their content in a format that can be easily converted into CSV or Excel format.  
# Your output should be structured in a way that facilitates conversion to CSV or Excel, with each row representing a logical unit of data.

# **Instructions:**  
# - Analyze the given document thoroughly, identify formatting patterns, choose optimal markup for CSV/Excel conversion, implement conversion, and verify quality.  
# - Your primary goal is to ensure structural fidelity of the input is replicated in a CSV/Excel-friendly format. Preserve all content without loss.  
# - Use commas to separate values in each row for CSV compatibility. Ensure that each logical unit of data is represented as a separate row.  
# - Translate any foreign language names of provinces, districts, or states into English before including them in the output.  
# - Maintain the hierarchy and order of content as it appears in the original document.  
# - For fields that are empty, leave them blank without using any filler like `<-- Missing -->`, `NA`, `NaN`, etc.

# **Fields (Columns) to Extract:**  
# 1. Province/District/State name (translated into English)  
# 2. Harvest month/year  
# 3. Crop type (+ any information about crop production, such as wet paddy rice vs. dry paddy rice or irrigated vs. unirrigated)  
# 4. Area Harvested (+units)  
# 5. Production (+units)  
# 6. Yield (+units)  

# **Exclusions:**  
# - **Ignore all visual elements** such as images, graphs, charts, or diagrams entirely. Do not include descriptions or notes about these elements in the output dataset.

# **Special Characters:**  
# - Pay special attention to commonly confused character pairs and use contextual clues to differentiate them accurately.

# **Additional Requirements:**  
# 1. Strictly use the specified fields (columns) as headers for the output dataset:  
#    - Province/District/State name  
#    - Harvest month/year  
#    - Crop type  
#    - Area Harvested (+units)  
#    - Production (+units)  
#    - Yield (+units)  
# 2. Ensure all extracted data is formatted correctly for direct export into Excel files.  
# 3. Validate that all numerical values fall within expected ranges for their respective columns (e.g., area harvested, production, yield).  
# 4. Flag any suspicious characters or potential OCR errors for review using comments <!-- -->.  
# 5. Ensure consistent units across columns where applicable (e.g., hectares for area, tons for production).  
# 6. Translate all non-English province/district/state names into English accurately.

# **Output Format:**  
# Enclose the response within XML tags as follows:  

# ```xml
# <thinking>
# [Step-by-step analysis and generation strategy]
# </thinking>
# <output>
# "Your converted document content here in CSV-friendly format"
# </output>
# ```

# **Quality Checks:**  
# 1. Verify structural and layout accuracy.  
# 2. Verify content completeness.  
# 3. Translation accuracy for province/district/state names.  
# 4. Hierarchy preservation.  
# 5. Confirm alignment and cell merging accuracy.  
# 6. Spacing fidelity.  
# 7. Verify that numbers fall within expected ranges for their column.  
# 8. Flag any suspicious characters that could be OCR errors using comments <!-- -->.
# 9. Validate syntax for CSV/Excel conversion.

# Remember:   
# - Your **primary objective** is to create an output that can be easily converted into CSV or Excel while preserving all textual details and translating foreign language province/district/state names into English.
# - **Ignore all visual elements** such as graphs, images, or charts.
# - Prioritize replicating structure above all else.
# """

#Prompt -4

# PARSER_PROMPT = f"""\
# You are a specialized agricultural data parser for Mongolian crop statistics. Your task is to extract and validate data with the following strict requirements:

# 1. Data Validation Rules:
# - Every cell must contain a value if present in source
# - Production values must never be left empty when available in source
# - Cross-validate values between related tables
# - Flag any suspicious patterns (e.g., identical values across years)
# - Verify unit consistency across all measurements

# 2. Value Association Rules:
# - Each production value must correspond to its exact year and province
# - Each area harvested must match its corresponding production value
# - Maintain parent-child relationships in hierarchical data
# - Never swap values between:
#   * Different years for same province
#   * Different provinces for same year
#   * Different crop types for same province/year

# 3. Required Output Format:
# Province/District,Year,Crop_Type,Area_Harvested,Production,Yield
# - Area_Harvested: Report in hectares
# - Production: Report in tonnes
# - Yield: Report in centner/hectare

# 4. Data Quality Checks:
# - Compare totals against regional subtotals
# - Verify year-over-year consistency
# - Validate against known agricultural patterns
# - Flag statistical outliers
# - Ensure no duplicate entries
# - Make sure all the data is scraped and considered nothing is left
# - Every row entry should be in single row and should not be merged with other rows

# 5. Translation Requirements:
# - Convert all Mongolian province names to standardized English names
# - Use official English translations for crop types
# - Maintain consistent naming across all entries

# Output Format:

# Enclose the response within XML tags as follows:
# <thinking>
# [Step-by-step analysis and generation strategy]
# </thinking>
# <output>
# "Your converted document content here in CSV-friendly format"
# </output>

# - CSV file with comma-separated values
# - Include column headers
# - One row per unique combination of province, year, and crop type
# - Consistent decimal notation
# - No text formatting or special characters
# - Make sure to complete Parsing the whole document and all the values
# """

# prompt template -5

PARSER_PROMPT = f"""\
You are a specialized agricultural data parser. Your primary task is to extract ALL tabular data from EVERY page of the PDF document with these strict requirements:

1. Table Parsing Rules:
- Parse EVERY table on EVERY page of the document completely
- Extract only the raw data present in tables - no interpretations or comments
- Process tables sequentially from top to bottom on each page
- Ensure no table rows or columns are skipped
- Do not merge or combine rows unless explicitly indicated in source

2. Data Extraction Focus:
- Focus EXCLUSIVELY on tabular data
- Extract ONLY what is visible in the tables
- Do not add any explanatory text or thinking process
- Do not make assumptions about missing data
- Do not skip any cells even if they appear empty
- Sometimes there might be multiple tables on a single page parse all of them

3. Required Output Format:
- Makes sure big numbers are parsed in double quotes (" ") to avoid any issues in CSV
- Each data point must be in its exact column
- Maintain consistent decimal notation
- Use only ASCII characters

4. Data Validation:
- Extract exact values as shown in tables
- Maintain original numerical precision
- Preserve empty cells as blank entries
- Do not round or modify numbers
- Flag any unreadable or corrupted values with "ERROR"
- If confused with a value just put empty quotes ""

Output Format:
<output>
[Raw CSV data only - one row per entry, numbers inside double quotes]
</output>

IMPORTANT:
- No explanations or thinking process
- No additional text or comments
- Parse ALL pages completely
- Extract ALL tables fully
- Focus ONLY on tabular data
"""

OPENAI_USER_PROMPT = """\

You are a specialized document parsing (including OCR) agent."""


REFORMAT_PROMPT = f"""\
Act as a data transformation expert. Transform the input dataframe to match the following master format:

Required Columns:
- country: Country name
- source_organization: Origin of the data (derived from source URL/table info)
- admin_0: Country-level region
- admin_1: State/province-level region
- admin_2: District/county-level region
- start_date: Primary date (minimum requirement: harvest year)
- period_date: Secondary date reference
- collection_date: Data collection timestamp
- season_date: Growing season timestamp
- season_year: Year of growing season
- indicator: One of [quantity produced, area planted, yield]
- value: Numeric value of the indicator
- product: Crop type
- unit: Unit of measurement for the indicator

Rules:
1. Map existing column names to the master format using fuzzy matching
2. Perform necessary pivoting/melting operations if data is in wide format
3. Standardize date columns to ISO format (YYYY-MM-DD)
4. Ensure indicator values are one of: quantity produced, area planted, or yield
5. Fill missing admin levels with appropriate higher-level values
6. Extract source organization from metadata if available
7. Validate units match the indicator type
"""


# INSTRUCTIONS_ADD_PG_BREAK = "Insert a `<page-break>` tag between the content of each page to maintain the original page structure."