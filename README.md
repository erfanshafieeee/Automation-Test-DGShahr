
# Automation-Test-DGShahr

This repository contains automated test scripts for the loan application flow in the "DGShahr" project, utilizing Selenium WebDriver and Pytest in Python. The automation suite thoroughly tests the entire loan request process, including user login, document submission, and integrates with Kiwi TCMS for comprehensive test reporting.

---

## 🧪 Project Overview

The **Automation-Test-DGShahr** repository is designed to automate the testing of the loan application workflow within the DGShahr platform. The automation covers:

* **Loan and Guarantee Request Flow Testing**: Automated tests for user flows related to loan and guarantee requests using Selenium and Pytest. Selenium tests ensure frontend flow integrity, while Pytest handles backend testing. Integrated with Kiwi TCMS via `tcms_api` for tracking and visualizing test results. Created test runners in Kiwi TCMS, with test plans, test cases, and real-time pass/fail status updates for enhanced visual reporting.

* **Random Product Image Test on Market Page**: A test that randomly selects 10 products every 20 minutes on the DGShahr market page to ensure all product images load correctly. In case of errors, failing image URLs are reported to a Google Sheet for tracking. The next test run cross-checks the reported errors, updating the status if issues are resolved.

* **Product Purchase Flow Testing**: An automated test to simulate and verify the product purchase flow on DGShahr. Results are visualized and tracked in Kiwi TCMS, ensuring the accuracy and efficiency of the purchase process.

By automating these crucial workflows, the project helps ensure the stability and performance of key features within the DGShahr platform. The integration with Kiwi TCMS allows for streamlined test case management, reporting, and visibility into test execution status.

---

## ⚙️ Technologies Used

* **Selenium WebDriver**: For automating web browser interaction.

* **Pytest**: For structuring and running the test cases.

* **Kiwi TCMS**: For test case management and reporting.

* **Python**: Programming language for writing the test scripts.

---

## 📁 Project Structure

The repository is organized as follows:

```
Automation-Test-DGShahr/
├── TCMS_tools/
│   └── make_tcms_maps.py
│   └── make_testcases.py
│   └── tcms_fuctions.py
│   └── tcms_helper.py
│   └── tcms_maps.py
├── .gitignore
├── README.md
├── api_collections.py
├── chromedriver.exe
├── common_functions.py
├── constants.py
├── functions.py
├── high_size.jpg
├── low_size.png
├── main.py
├── requirements.txt
├── sel_lend_assurance_flow_from_zero.py
├── sel_lend_loan_flow_from_zero.py
├── sel_market_check_pay.py
├── sel_market_check_pdp.py
├── test_lend_assurance_flow_from_zero.py
├── test_lend_loan_flow_from_zero.py
└── test_lend_user_login.py


```

* **TCMS\_tools/**: Contains scripts for integrating with Kiwi TCMS.

* **.gitignore**: Specifies files and directories to be ignored by Git.

* **README.md**: This file.

* **api\_collections.py**: Houses API-related test scripts.

* **chromedriver.exe**: WebDriver executable for Chrome browser.

* **common\_functions.py**: Contains utility functions used across tests.

* **constants.py**: Defines constant values used in the tests.

* **functions.py**: Additional helper functions for test execution.

* **high\_size.jpg** & **low\_size.png**: Sample image files for testing.

* **main.py**: Entry point for executing the tests.

* **requirements.txt**: Lists Python dependencies for the project.

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

* Python 3.x

* pip (Python package installer)

* Google Chrome browser

* ChromeDriver compatible with your browser version

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/erfanshafieeee/Automation-Test-DGShahr.git
   cd Automation-Test-DGShahr
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure that `chromedriver.exe` is located in the project directory or specify its path in your test scripts.

---

## 🧪 Running the Tests

To execute the automated tests, run the following command:

```bash
python3 main.py
```
---

## 📊 Test Reporting with Kiwi TCMS

The project integrates with Kiwi TCMS for test case management and reporting. Upon test execution, results are automatically uploaded to the Kiwi TCMS instance specified in the integration script. This allows for centralized tracking of test outcomes and facilitates test case management.

Built on **`tcms_api`**: this integration uses the official client library. Since there wasn’t a clear, developer-friendly reference for `tcms_api`, I authored a **comprehensive guide** that covers prerequisites, installation, connection & authentication, common usage patterns, and a **complete, no-omissions API reference**. The guide also walks through how to wire your test suite to Kiwi TCMS step-by-step with Python examples.

📖 Read the guide: **[End-to-End Guide: Connecting Your Tests to Kiwi TCMS via tcms_api](https://github.com/erfanshafieeee/Automation-Test-DGShahr/blob/main/TCMS_tools/DOCUMENT.md)**.



