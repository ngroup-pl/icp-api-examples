"""
An example of downloading a list of projects from the IC Project API and saving them to a CSV file

https://developers.icproject.com/api-documentation/#tag/Project/operation/getProjectCollection
"""
import csv
import sys

import requests

"""
You can find authorization token and instance slug in your instance settings panel.
"""
authorization_token = ""
instance_slug = ""

# necessary headers
headers = {
    'X-Auth-Token': authorization_token,
    'Accept': 'application/json',
}

# make a request
response = requests.get(
    f"https://app.icproject.com/api/instance/{instance_slug}/project/projects?pagination=0",
    headers=headers,
)

# check response status code
if response.status_code != 200:
    print(response.status_code, response.content)
    sys.exit()

# columns to export, consecutively key, label and optional value formatting function
columns = (
    ('id', 'ID', None),
    ('no', 'Number', None),
    ('name', 'Name', None),
    ('contractorId', 'Contractor ID', None),
    ('contractorName', 'Contractor', None),
    ('status', 'Status', None),
    ('userPermissions', 'Permissions', lambda x: ", ".join(x)),
    ('category', 'Category', lambda x: x['name'] if x else None),
    ('dateStart', 'Start date', None),
    ('dateEnd', 'End date', None),
    ('dateStartPlanned', 'Planned start date', None),
    ('dateEndPlanned', 'Planned end date', None),
    ('isFavorite', 'Favourite?', None),
    ('assignedProjectUsers', 'Assigned users',
     lambda x: ", ".join([u['projectUser']['firstName'] + " " + u['projectUser']['lastName'] for u in x])),
    ('progress', 'Progress', None),
    ('budget', 'Budget', None),
    ('taskCountTotal', 'Total tasks', None),
    ('taskCountDone', 'Done tasks', None),
    ('timePlanned', 'Planned time', None),
    ('timeReported', 'Reported time', None),
    ('shortCode', 'Short code', None),
    ('tags', 'Tags', lambda x: ", ".join([t['name'] for t in x]))
)

# open file
with open('projects.csv', 'w', newline='') as csv_file:
    # csv writer
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')

    # header
    writer.writerow([k[1] for k in columns])

    # loop
    for project in response.json():
        # some debug
        print(project['name'])

        row = []
        for key, label, formatter in columns:
            value = project[key]

            # some columns need to be formatted
            if formatter:
                value = formatter(value)

            # append value to current row
            row.append(value)

        # append row to csv
        writer.writerow(row)
