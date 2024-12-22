# Finance App README

## Installation Guide

1. **Clone the Repository**
   - Ensure you have `git` installed. Clone the repository by running:
     ```bash
     git clone <repository-url>
     cd <repository-folder>
     ```

2. **Install Required Libraries**
   - Make sure you have Python 3.7+ installed. Then, install the dependencies listed in the `requirements.txt` file by running:
     ```bash
     pip install -r requirements.txt
     ```

3. **Set Up API Keys**
   - The application requires API keys to function properly. These keys should be stored in the following files:
     
     - **`OAI_CONFIG_LIST`**: Add your OpenAI-related configurations in this file. Format each line with proper configurations like API keys, settings, etc.
     - **`config_api_keys`**: Store other API keys or configuration details here.

     Make sure the contents of these files follow the expected structure of the application.

4. **Run the Application**
   - Once setup is complete, start the web application by running:
     ```bash
     python fin_app.py
     ```

5. **Access the Web Application**
   - Open your browser and navigate to the local URL displayed in the terminal (typically `http://127.0.0.1:8000` or similar) to interact with the application.

## File Overview

- `finance_report.py`: Handles backend logic for generating financial reports.
- `fin_app.py`: The main script to run the web application.
- `forcaster.py`: Contains forecasting logic for financial predictions.
- `requirements.txt`: Lists all required Python libraries and dependencies.
- `OAI_CONFIG_LIST`: File to store OpenAI-related API keys and settings.
- `config_api_keys`: File to store general API keys and configuration settings.
- `README.md`: This installation and usage guide.

