from jsonschema import validate
from jsonschema.exceptions import ValidationError
from api_collections import FileAPI

# Function to validate a JSON schema
def schema_validator(main_data, schema_data):
    try:
        validate(instance=main_data, schema=schema_data)  # Validating the structure of main_data against schema_data
    except ValidationError as e:
        assert False, f"Data Structure Did Not Match Schema: {e}"  # Raising an assertion error if validation fails

# Function to update the authorization token in constants.py
def update_token_in_constants(new_token):
    constants_file_path = "constants.py"  # Path to the constants file

    with open(constants_file_path, "r") as file:
        lines = file.readlines()  # Reading all lines from the file

    with open(constants_file_path, "w") as file:
        for line in lines:
            if line.startswith("AUTH_TOKEN ="):  # Checking for the AUTH_TOKEN line
                file.write(f'AUTH_TOKEN = "{new_token}"\n')  # Updating the token
            else:
                file.write(line)  # Writing back the unchanged lines

# Function to upload an image file using FileAPI
def upload_image(file_name, file_type, file_format):
    files = {
        'file': (f'{file_name}', open(f'{file_name}', 'rb'), 'image/jpeg'),  # Opening the file and specifying the MIME type
        'file_type': (None, f'{file_type}'),  # Adding file type
        'file_extension': (None, file_format),  # Adding file format
    }

    return FileAPI().upload(files)  # Uploading the file using FileAPI
