import uuid
import requests

# Configuration for Apilo API
APILO_INSTANCE_SLUG = "YOUR_APILO_INSTANCE_SLUG"
APILO_ACCESS_TOKEN = "YOUR_APILO_ACCESS_TOKEN"

# Configuration for IC Project API
IC_PROJECT_INSTANCE_SLUG = "YOUR_IC_PROJECT_INSTANCE_SLUG"
IC_PROJECT_API_KEY = "YOUR_IC_PROJECT_API_KEY"
IC_PROJECT_BOARD_LINK = "YOUR_IC_PROJECT_BOARD_LINK"

def get_orders_from_apilo():
    url = f"https://{APILO_INSTANCE_SLUG}.apilo.com/rest/api/orders"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {APILO_ACCESS_TOKEN}",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error retrieving orders: {e}")
        return {}

def get_board_slug(url):
    parts = url.rstrip('/').split('/')
    return parts[-1]

def get_board_column_id(board_slug):
    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/boards/s/{board_slug}/get-kanban-board"
    headers = {
        'X-Auth-Token': IC_PROJECT_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        board_id = response.json().get('id')
        if not board_id:
            raise ValueError("Board ID not found in the response")
    except requests.RequestException as e:
        print(f"Error retrieving board ID: {e}")
        return None
    except ValueError as e:
        print(e)
        return None

    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/boards/{board_id}/board-columns"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()[0].get('id')  # Assuming you want the first column's ID
    except requests.RequestException as e:
        print(f"Error retrieving board columns: {e}")
        return None

def create_task_in_ic_project(order):
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
        print(f"Error retrieving task templates: {e}")
        return

    board_slug = get_board_slug(IC_PROJECT_BOARD_LINK)
    column_id = get_board_column_id(board_slug)
    if not column_id:
        print(f"Error: Unable to find column for board_slug {board_slug}")
        return

    url = f"https://app.icproject.com/api/instance/{IC_PROJECT_INSTANCE_SLUG}/project/tasks"
    headers = {
        'X-Auth-Token': IC_PROJECT_API_KEY,
        'Accept': 'application/json',
    }

    task_data = {
        "identifier": str(uuid.uuid4()),
        "boardColumn": column_id,
        "name": f"Order ID: {order['idExternal']}",
        "description": f"Order from customer: {order['addressCustomer']['name']}",
        "dateStart": f"{order['createdAt']}",
        "dateEnd": "DATE END",
        "priority": "normal"
    }

    try:
        response = requests.post(url, json=task_data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 201:
            print(f"Task for order {order['idExternal']} created successfully.")
        else:
            print(f"Error creating task for order {order['idExternal']}: {response.status_code}")
            print(response.json())
    except requests.RequestException as e:
        print(f"Error creating task: {e}")

def integrate_apilo_with_ic_project():
    orders = get_orders_from_apilo()
    for order in orders.get('orders', []):
        create_task_in_ic_project(order)

# Run the integration
integrate_apilo_with_ic_project()
