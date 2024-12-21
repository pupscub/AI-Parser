
## Setup Instructions

### Prerequisites
- Python 3.8 or higher installed on your system.
- `pip` package manager.

### Steps to Set Up the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/pupscub/AI-Parser.git
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   make setup
   ```

3. (Optional) Install development dependencies:
   ```bash
   make dev
   ```

### Running the Streamlit App

To run the demo application:

1. Ensure you've completed the setup steps above.

2. **Activate the virtual environment**:
   - On **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     .venv\Scripts\activate
     ```

3. Execute the following command to start the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Open the URL provided by Streamlit in your browser to access the app.

### Cleaning Up

To remove the virtual environment:
```bash
make clean
```