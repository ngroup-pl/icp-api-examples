import os
import sys
from uuid import uuid4
import requests
import csv
import json
from os.path import join, dirname
from dotenv import load_dotenv
import logging

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv(join(dirname(__file__), '.env'))

# Konfiguracja logowania (debug)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Pobieranie tokena autoryzacji i slug instancji ICP z pliku .env
icp_authorization_token = os.environ.get("ICP_AUTHORIZATION_TOKEN")
icp_instance_slug = os.environ.get("ICP_INSTANCE_SLUG")

# Nagłówki autoryzacyjne do API ICP
headers = {
    'X-Auth-Token': icp_authorization_token,
    # 'Authorization': "Bearer ",
    'Accept': 'application/json',
    'Content-type': 'application/json'
}

# URL API ICP
icp_api_url = f"https://app.icproject.com/api/instance/{icp_instance_slug}"

# Nazwa pliku CSV podawana jako argument
csv_fn = sys.argv[1]
ids_fn = f'{csv_fn}_ids.json'

project_name = None

# Jeśli plik z zapisanymi identyfikatorami istnieje, wczytaj treść. W przeciwnym razie zainicjuj pustą strukturę.
if os.path.exists(ids_fn):
    logging.info(f"Loading existing IDs from {ids_fn}")
    ids = json.load(open(ids_fn, 'r'))
else:
    logging.info("Initializing a new IDs structure")
    ids = {
        'projects': {},
        'stages': {},
        'boards': {},
        'columns': {},
        'tasks': {},
        'checklists': {},
        'checklist_items': {}
    }


# Funkcja zapisująca identyfikatory do pliku JSON
def save_ids():
    logging.debug(f"Saving IDs to {ids_fn}")
    with open(ids_fn, 'w') as f:
        json.dump(ids, f, indent=4)

_task_name = None

# Przetwarzanie pliku CSV
with open(csv_fn) as f:
    reader = csv.reader(f, delimiter=',')
    next(reader, None)  # Pomijanie nagłówków CSV

    for project_name, stage_name, board_name, task_name, checklist_name, checklist_item in reader:
        logging.info(f"Parsing data for Project: {project_name}, Stage: {stage_name}, Task: {task_name}")

        # Tworzenie klucza projektu
        project_key = project_name

        if not task_name:
            task_name = _task_name

        _task_name = task_name

        # Tworzenie projektu, jeśli jeszcze nie istnieje
        if project_key not in ids['projects']:
            logging.debug(f"Creating project: {project_name}")
            project_data = {
                "name": project_name,
                "dateStartPlanned": '2024-01-01',
                "dateEndPlanned": '2024-12-31',
                "description": "",
                "isBlameableRemovalEnabled": True,
                "status": 'open',
                "budget": 0
            }
            response = requests.post(f"{icp_api_url}/project/projects", headers=headers, json=project_data)
            if response.status_code == 201:
                ids['projects'][project_key] = response.json()['id']
                save_ids()
                logging.debug(f"Project created successfully: {project_name}")
            else:
                logging.error(f"Error creating project {project_name}: {response.status_code}, {response.text}")
                sys.exit(1)

        project_id = ids['projects'][project_key]

        # Tworzenie klucza dla etapu projektu
        stage_key = f"{project_id}-{stage_name}"

        # Tworzenie etapu (stage), jeśli nie istnieje
        if stage_key not in ids['stages']:
            logging.debug(f"Creating stage: {stage_name}")
            stage_data = {
                "name": stage_name,
                "project": project_id,
                "dateStart": '2024-01-01',
                "dateEnd": '2024-12-31',
                "description": "",
                "isBlameableRemovalEnabled": True,
                "status": 'open',
            }
            response = requests.post(f"{icp_api_url}/project/stages", headers=headers, json=stage_data)
            if response.status_code == 201:
                ids['stages'][stage_key] = response.json()['id']
                save_ids()
                logging.debug(f"Stage created successfully: {stage_name}")
            else:
                logging.error(f"Error creating stage {stage_name}: {response.status_code}, {response.text}")
                sys.exit(1)

        stage_id = ids['stages'][stage_key]

        # Tworzenie klucza dla tablicy (board)
        board_key = f"{project_id}-{stage_id}-{board_name}"

        # Tworzenie tablicy (board), jeśli nie istnieje
        if board_key not in ids['boards']:
            logging.debug(f"Creating board: {board_name}")
            board_data = {
                "name": board_name,
                "stage": stage_id,
                "dateStart": '2024-01-01',
                "dateEnd": '2024-12-31',
                "description": "",
                "isBlameableRemovalEnabled": True,
                "status": 'open',
            }
            response = requests.post(f"{icp_api_url}/project/boards", headers=headers, json=board_data)
            if response.status_code == 201:
                ids['boards'][board_key] = response.json()['id']
                save_ids()
                logging.debug(f"Board created successfully: {board_name}")
            else:
                logging.error(f"Error creating board {board_name}: {response.status_code}, {response.text}")
                sys.exit(1)

        board_id = ids['boards'][board_key]

        # Pobranie kolumny, jeśli nie istnieje
        if board_id not in ids['columns']:
            logging.debug(f"Fetching columns for board: {board_name}")
            response = requests.get(f"{icp_api_url}/project/boards/{board_id}/get-kanban-tasks", headers=headers)
            if response.status_code == 200:
                ids['columns'][board_id] = response.json()['boardColumns'][0]['id']
                save_ids()
                logging.debug(f"Columns fetched successfully for board: {board_name}")

        # Tworzenie zadania (task)
        task_key = f"{board_id}-{task_name}"
        if task_key not in ids['tasks']:
            logging.debug(f"Creating task: {task_name}")
            task_data = {
                "identifier": uuid4().__str__(),
                "name": task_name[:100],
                "boardColumn": ids['columns'][board_id],
                "dateStart": '2024-01-01',
                "dateEnd": '2024-12-31',
                "description": task_name if len(task_name) > 100 else "",
            }
            response = requests.post(f"{icp_api_url}/project/tasks", headers=headers, json=task_data)
            if response.status_code == 201:
                task_id = response.json()['id']
                ids['tasks'][task_key] = task_id
                save_ids()
                logging.debug(f"Task created successfully: {task_name}")
            else:
                logging.error(f"Error creating task {task_name}: {response.status_code}, {response.text}")
                sys.exit(1)

        task_id = ids['tasks'][task_key]

        # Jeśli brak checklisty lub elementu, przejdź dalej
        if not checklist_name or not checklist_item:
            continue

        # Tworzenie checklisty
        checklist_key = f"{task_id}-{checklist_name}"
        if checklist_key not in ids['checklists']:
            logging.debug(f"Creating checklist: {checklist_name}")
            response = requests.post(f"{icp_api_url}/project/task-checklists", headers=headers, json={
                "identifier": uuid4().__str__(),
                "name": checklist_name,
                "task": task_id
            })
            if response.status_code == 201:
                ids['checklists'][checklist_key] = response.json()['id']
                save_ids()
                logging.debug(f"Checklist created successfully: {checklist_name}")
            else:
                logging.error(f"Error creating checklist {checklist_name}: {response.status_code}, {response.text}")
                sys.exit(1)

        checklist_id = ids['checklists'][checklist_key]

        # Tworzenie pozycji w checklisty
        checklist_item_key = f"{checklist_id}-{checklist_item}"
        if checklist_item_key not in ids['checklist_items']:
            logging.debug(f"Creating checklist item: {checklist_item}")
            response = requests.post(f"{icp_api_url}/project/task-checklist-items", headers=headers, json={
                "identifier": uuid4().__str__(),
                "name": checklist_item,
                "taskChecklist": checklist_id
            })
            if response.status_code == 201:
                ids['checklist_items'][checklist_item_key] = response.json()['id']
                save_ids()
                logging.debug(f"Checklist item created successfully: {checklist_item}")
            else:
                logging.error(
                    f"Error creating checklist item {checklist_item}: {response.status_code}, {response.text}")
