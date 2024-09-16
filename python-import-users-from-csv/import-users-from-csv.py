import pandas as pd
import requests
import json

# Configuration
CSV_FILE_PATH = 'sample-users.csv'
ICP_SLUG = 'your_ic_project_slug'  # Replace with actual slug
API_ENDPOINT = f'https://app.icproject.com/api/instance/{ICP_SLUG}/user/users'
API_KEY = 'your_api_key'  # Replace with actual API key


# Function to transform a CSV row into JSON format
def transform_row(row):
    """
    Transforms a row from the CSV file into a JSON dictionary for a user.

    This function takes a row from the CSV file and returns a dictionary with user data in JSON format.
    Missing values are filled with default values.
    """
    # Create a JSON dictionary for the user
    return {
        "email": row['email'],  # User's email address
        "firstName": row['firstName'],  # User's first name
        "lastName": row['lastName'],  # User's last name
        "canLogIn": row.get('canLogIn', 'true').lower() == 'true',  # Whether the user can log in (default is true)
        "phoneNumber": row.get('phoneNumber', ''),  # User's phone number (optional)
        "jobPosition": row.get('jobPosition', 'default-job-position-id'),  # User's job position (optional)
        "department": row.get('department', 'default-department-id'),  # User's department (optional)
        "roleSets": [row.get('roleSets', 'default-role-set-id')],  # List of user roles (optional)
        "hourlyRate": float(row.get('hourlyRate', 0))  # User's hourly rate (optional, default is 0)
    }

# Load data from the CSV file
df = pd.read_csv(CSV_FILE_PATH)

# Process each row and send data to the API
for index, row in df.iterrows():
    user_data = transform_row(row)
    print(f"Preparing data for user: {user_data['email']}")

    headers = {
        'X-Auth-Token': API_KEY,  # Authorization header
        'Content-Type': 'application/json',  # Content type
        'Accept': 'application/json',  # Acceptable response type
    }

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(user_data))

    # Check the API response
    if response.status_code == 201:
        print(f"User {user_data['email']} has been successfully added.")
    else:
        print(f"Error adding user {user_data['email']}: {response.status_code} - {response.text}")

print("Import process completed.")
