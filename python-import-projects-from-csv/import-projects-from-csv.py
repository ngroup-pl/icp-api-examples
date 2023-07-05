import csv
import requests

"""
You can find authorization token and instance slug in your instance settings panel.
"""
authorization_token = ""
instance_slug = ""

# open csv file
with open('sample-projects.csv') as csvfile:
    # csv reader
    reader = csv.reader(csvfile, delimiter=',')

    # skip first row (header)
    next(reader, None)

    # loop
    for project_name, date_start, date_end, description, status in reader:
        print(f"Creating project: {project_name}", end="")

        # https://developers.icproject.com/api-documentation/#tag/Project/operation/postProjectCollection
        params = {
            "name": project_name,
            "dateStartPlanned": date_start,
            "dateEndPlanned": date_end,
            "category": None,
            "tags": None,
            "description": description,
            "isBlameableRemovalEnabled": True,
            "status": status,
            "budget": 0
        }

        # necessary headers
        headers = {
            'X-Auth-Token': authorization_token,
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

        # make a request
        response = requests.post(
            f"https://app.icproject.com/api/{instance_slug}/project/projects",
            json=params,
            headers=headers,
        )

        print("\t", response.status_code)

        # errors?
        if response.status_code != 200:
            print(response.content)
