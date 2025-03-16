# Automation Test
## Overview
This repository contains automated test scripts for a loan application flow using Selenium WebDriver in Python. The automation covers the entire loan request process from user login to document submission.

<<<<<<< HEAD
# Loan Automation Testing Project

This repository contains automated tests for a loan processing system's API endpoints.

## Overview

The project provides automated testing for various API endpoints including:
- Assurance operations
- Branch management 
- Document handling
- File operations
- Transaction processing
- User authentication

## Key Components

- `api_collections.py`: Contains API client classes for different service endpoints
- `constants.py`: Stores configuration values and credentials
- `common_functions.py`: Includes utility functions for schema validation, token management etc.

## Setup

1. Clone the repository
2. Install dependencies:
=======
## Key Features
- Automated login with phone number and OTP verification
- Loan request submission
- Primary information form filling
- Credit approval validation
- Guarantee type selection and configuration 
- Document uploads (identity, residence, job documents)
- Support for different flow paths based on request status
>>>>>>> 893b345 (update: rewrite README.md to provide a comprehensive overview of the automation test project, including key features, main components, flow steps, and requirements)

## Main Components

<<<<<<< HEAD

=======
### Core Files
- `sel_lend_loan_flow_from_zero.py`: Main test script implementing the loan flow
- `sel_lend_guaranty_flow_from_zero.py`: Main test script implementing the guaranty flow  
- `functions.py`: Helper functions for common operations
- `constants.py`: Configuration constants and test data

### Key Functions
- Login and authentication
- Form filling and validation
- Document upload handling
- Database connectivity for request status tracking
- Flow control based on current application state

## Flow Steps
1. User login with phone number
2. OTP verification
3. Loan request initiation 
4. Primary information submission
5. Credit approval check
6. Guarantee selection and configuration
7. Document uploads:
   - Identity documents
   - Residence documents 
   - Job documents

## Requirements
- Python 3.x
- Selenium WebDriver
- PostgreSQL database connection
- Chrome WebDriver

## Usage
The script automatically detects the current request step from the database and continues the flow from the appropriate point. This allows for resuming incomplete applications and testing different scenarios.

>>>>>>> 893b345 (update: rewrite README.md to provide a comprehensive overview of the automation test project, including key features, main components, flow steps, and requirements)
