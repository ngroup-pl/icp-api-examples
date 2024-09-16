import uuid
import requests

# Apilo API configuration
APILO_INSTANCE_SLUG = "YOUR_APILO_INSTANCE_SLUG"  # Slug for your Apilo instance
APILO_ACCESS_TOKEN  = "YOUR_APILO_ACCESS_TOKEN"

# IC Project API configuration
IC_PROJECT_INSTANCE_SLUG = "YOUR_IC_PROJECT_INSTANCE_SLUG"  # Slug for IC Project instance
IC_PROJECT_API_KEY = "YOUR_IC_PROJECT_API_KEY"  # API key for IC Project
IC_PROJECT_BOARD_LINK = "YOUR_IC_PROJECT_BOARD_LINK"  # Link to the project board

# Function to retrieve orders from Apilo
def get_orders_from_apilo():
    """
    Retrieves orders from Apilo

    :return: Orders in JSON format
    """
    # url = f"https://{APILO_INSTANCE_SLUG}.apilo.com/rest/api/orders"
    # You can add eventual filters to the URL or use the non-filtered URL
    url = f"https://{APILO_INSTANCE_SLUG}.apilo.com/rest/api/orders&createdAfter=2022-03-01T14%3A40%3A33%2B0200"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        # Authorization token for Apilo stored in APILO_ACCESS_TOKEN
        'Authorization': f"Bearer {APILO_ACCESS_TOKEN}",
    }
    try:
        # Send GET request to fetch orders from Apilo
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        # Handle error if the request fails
        print(f"Error fetching orders: {e}")
        return {}

# Function to extract the board slug from the board URL
def get_board_slug(url):
    """
    Extracts the board slug from the given board link

    :param url: Link to the board
    :return: Board slug
    """
    parts = url.split('/')
    return parts[-1]

# Function to get the first column's ID of the board
def get_board_column_id(board_slug):
    """
    Retrieves the ID of the first column of the board based on the given board slug

    :param board_slug: Board slug
    :return: The ID of the first board column
    """
    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/boards/s/{board_slug}/get-kanban-board"
    headers = {
        'X-Auth-Token': IC_PROJECT_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        board_id = response.json().get('id')  # Get the board ID
        if not board_id:
            raise ValueError("No board ID found in response")
    except requests.RequestException as e:
        print(f"Error fetching board ID: {e}")
        return None
    except ValueError as e:
        print(e)
        return None

    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/boards/{board_id}/board-columns"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        # Assuming the first column's ID is needed
        return response.json()[0].get('id')
    except requests.RequestException as e:
        print(f"Error fetching board columns: {e}")
        return None

# Function to create a task in IC Project based on Apilo order
def create_task_in_ic_project(order):
    """
    Creates a task in IC Project based on Apilo order data

    :param order: Apilo order data
    :return: None
    """
    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/task-templates"
    headers = {
        'X-Auth-Token': IC_PROJECT_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        print(f"Error fetching task templates: {e}")
        return

    board_slug = get_board_slug(IC_PROJECT_BOARD_LINK)  # Extract board slug
    column_id = get_board_column_id(board_slug)  # Fetch the column ID of the board
    if not column_id:
        print(f"Error: Unable to find column for board_slug {board_slug}")
        return

    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/tasks"
    headers = {
        'X-Auth-Token': IC_PROJECT_API_KEY,
        'Accept': 'application/json',
    }

    # Create task data based on the order details
    task_data = {
        "identifier": str(uuid.uuid4()),  # Generate unique task identifier
        "boardColumn": column_id,  # Assign the task to the specified column
        "name": f"Order ID: {order['idExternal']}",  # Task name is based on external order ID
        "description": f"Order from customer: {order['addressCustomer']['name']}",  # Task description with customer details
        "dateStart": f"{order['createdAt']}",  # Task start date based on order creation time
        "dateEnd": "DATE END",  # Example end date
        "priority": "normal"  # Default task priority
    }

    try:
        # Send POST request to create a new task
        response = requests.post(url, json=task_data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 201:
            print(f"Task for order {order['idExternal']} created successfully.")
        else:
            print(f"Error creating task for order {order['idExternal']}: {response.status_code}")
            print(response.json())
    except requests.RequestException as e:
        print(f"Error creating task: {e}")

# Main function to integrate Apilo orders with IC Project tasks
def main():
    """
    Main function to integrate Apilo orders with IC Project tasks

    Retrieves orders from Apilo and creates a task for each order in IC Project.
    """
    orders = get_orders_from_apilo()  # Fetch orders from Apilo
    for order in orders.get('orders', []):
        # Create a task in IC Project for each order
        create_task_in_ic_project(order)

# Run the integration only if the script is being executed directly
if __name__ == "__main__":
    main()
