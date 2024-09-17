import csv
import requests

# Path to the CSV file and API details
CSV_FILE_PATH = 'sample-contractors.csv'  # Path to your CSV file
ICP_SLUG = 'your_ic_project_slug'  # Your IC Project slug
API_ENDPOINT = f'https://app.icproject.com/api/instance/{ICP_SLUG}/crm/contractors'
API_KEY = 'your_api_key'  # Your API key

# Headers required by the API
headers = {
    'X-Auth-Token': API_KEY,  # Authorization token
    'Content-Type': 'application/json',  # Content type for the request
    'Accept': 'application/json',  # Expected response type
}

# Function to read the CSV and send data to the API
def main(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            contractor_data = {
                'name': row['name'],  # Required field: contractor's name
                # Optional fields below, uncomment if needed:
                # 'email': row['email'],  # Optional: contractor's email
                # 'phoneNumber': row['phone'],  # Optional: phone number
                # "fullName": "string",  # Optional: full name
                # "vatId": "string",  # Optional: VAT ID
                # "paymentDays": 0,  # Optional: payment days
                # "description": "string",  # Optional: description
                # "tags": [ "497f6eca-6276-4993-bfeb-53cbbbba6f08" ],  # Optional: tags
                # "industryBranches": [ "497f6eca-6276-4993-bfeb-53cbbbba6f08" ],  # Optional: industry branches
                # "contactInfo": [
                #     { "type": "string", "value": "string", "isDefault": True }  # Optional: contact info
                # ],
            }
            # Sending POST request to the API
            response = requests.post(API_ENDPOINT, json=contractor_data, headers=headers)
            if response.status_code == 201:
                print(f"Contractor {row['name']} added successfully.")
            else:
                print(f"Error adding contractor {row['name']}: {response.status_code}, {response.text}")

# Load contractors from the CSV file and send data to the API
if __name__ == "__main__":
    main(CSV_FILE_PATH)
