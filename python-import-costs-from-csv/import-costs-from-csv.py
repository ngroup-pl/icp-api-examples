import csv
import requests
from datetime import datetime

# Function to fetch existing cost categories from the API
def get_existing_cost_categories(api_url, headers):
    response = requests.get(f"{api_url}/finance/cost-categories", headers=headers)
    if response.status_code == 200:
        return {category['name']: category for category in response.json()}
    else:
        print(f"Error fetching cost categories: {response.status_code}")
        return {}

# Function to fetch existing tax rates from the API
def get_existing_tax_rates(api_url, headers):
    response = requests.get(f"{api_url}/finance/tax-rates", headers=headers)
    if response.status_code == 200:
        return {tax_rate['name']: tax_rate for tax_rate in response.json()}
    else:
        print(f"Error fetching tax rates: {response.status_code}")
        return {}

# Function to fetch existing projects from the API
def get_existing_projects(api_url, headers):
    response = requests.get(f"{api_url}/project/projects", headers=headers)
    if response.status_code == 200:
        return {project['name']: project for project in response.json()}
    else:
        print(f"Error fetching projects: {response.status_code}")
        return {}

# Function to create a new cost category
def create_cost_category(name, api_url, headers):
    data = {
        "name": name,
    }
    response = requests.post(f"{api_url}/finance/cost-categories", headers=headers, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating cost category {name}: {response.status_code}, {response.text}")
        return None

# Function to create a new tax rate
def create_tax_rate(name, value, api_url, headers):
    data = {
        "name": name,
        "value": value,
        "isDefault": False
    }
    response = requests.post(f"{api_url}/finance/tax-rates", headers=headers, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Error creating tax rate {name}: {response.status_code}, {response.text}")
        return None

# Function to convert CSV data to JSON format for costs
def csv_to_costs(file_path, api_url, headers):
    # Fetch existing cost categories, tax rates, and projects
    existing_categories = get_existing_cost_categories(api_url, headers)
    existing_tax_rates = get_existing_tax_rates(api_url, headers)
    existing_projects = get_existing_projects(api_url, headers)

    costs = []

    # Open the CSV file
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)

        # Iterate through rows in the CSV
        for row in csv_reader:
            # Check if cost category already exists; create new one if not
            category_name = row['category']
            if category_name not in existing_categories:
                new_category = create_cost_category(category_name, api_url, headers)
                if new_category:
                    existing_categories[category_name] = new_category
            cost_category = existing_categories.get(category_name, {})

            # Check if tax rate already exists; create new one if not
            tax_rate_name = row['taxRate']
            tax_rate_value = float(row['taxRateValue'])
            if tax_rate_name not in existing_tax_rates:
                new_tax_rate = create_tax_rate(tax_rate_name, tax_rate_value, api_url, headers)
                if new_tax_rate:
                    existing_tax_rates[tax_rate_name] = new_tax_rate
            tax_rate = existing_tax_rates.get(tax_rate_name, {})

            # Check if project exists
            project_name = row.get('project', '')
            project_id = existing_projects.get(project_name, {}).get('id') if project_name else None

            cost = {
                "name": row['name'],  # Cost name
                "description": row['description'],  # Cost description
                "priceNet": float(row['priceNet']),  # Net price
                "priceGross": float(row['priceGross']),  # Gross price
                "date": row['date'],  # Date
                "isBilled": row['isBilled'].lower() == 'true',  # Is billed
                "isPosted": row['isPosted'].lower() == 'true',  # Is posted
                "createdAt": datetime.now().isoformat(),  # Created at
                "updatedAt": datetime.now().isoformat(),  # Updated at
                "costCategory": cost_category.get('id'),  # Cost category
                "taxRate": tax_rate.get('id'),  # Tax rate
                "financeProject": project_id  # Project ID, if exists
            }

            costs.append(cost)

    return costs

# Function to send cost data to the API
def send_costs_to_api(costs, api_url, headers):
    # Iterate through each cost and send data to the API
    for cost in costs:
        response = requests.post(f"{api_url}/finance/costs", headers=headers, json=cost)
        if response.status_code == 201:
            print(f"Success: Cost {cost['name']} was sent.")
        else:
            print(f"Error: Failed to send cost {cost['name']}. Response code: {response.status_code}, error: {response.text}")

# Example usage
csv_file = 'sample-costs.csv'  # Path to the CSV file
instance_slug = 'your-instance-slug'  # Your instance slug
api_url = f'https://app.icproject.com/api/instance/{instance_slug}'  # API endpoint
api_key = 'your-api-key'  # Your API key

# Headers for authorization and content type
headers = {
    'X-Auth-Token': api_key,  # Authorization token
    'Content-Type': 'application/json',  # Content type for the request
    'Accept': 'application/json',  # Expected response type
}

# Convert CSV data
costs_data = csv_to_costs(csv_file, api_url, headers)

# Send data to the API
send_costs_to_api(costs_data, api_url, headers)
