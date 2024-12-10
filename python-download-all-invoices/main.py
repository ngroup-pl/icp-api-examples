import os
import sys
from os.path import join, dirname
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(join(dirname(__file__), '.env'))

icp_authorization_token = os.environ.get("ICP_AUTHORIZATION_TOKEN")
icp_instance_slug = os.environ.get("ICP_INSTANCE_SLUG")

headers = {
    'X-Auth-Token': icp_authorization_token,
    'Accept': 'application/json',
    'Content-type': 'application/json'
}

icp_api_url = f"https://app.icproject.com/api/instance/{icp_instance_slug}"



def retrieve_invoices_list() -> list:
    page = 1
    per_page = 100
    date_start = datetime.today().replace(day=1).replace(month=1).replace(hour=0, minute=0, second=0, microsecond=0)
    date_end = datetime.today().replace(day=31).replace(month=12)
    items = []
    while True:
        print(f"Retrieving invoices, page: {page}")
        response = requests.get(
            f"{icp_api_url}/finance/invoices",
            params={
                "page": page,
                "itemsPerPage": per_page,
                "dateIssue[after]": date_start.isoformat(),
                "dateIssue[before]": date_end.isoformat(),
                "order[number]": "asc"
            },
            headers=headers,
            timeout=10
        )

        items += response.json()

        if len(response.json()) < per_page:
            break

        page = page + 1

    return items



if __name__ == '__main__':

    try:
        items = retrieve_invoices_list()
    except Exception as e:
        print(e)
        sys.exit(1)

    for item in items:
        print(f"Downloading {item['no']}", end=" ")
        if not item['fileGenerated']:
            requests.patch(f"{icp_api_url}/finance/invoices/{item['id']}/generate-pdf", headers=headers)
            print("file is not generated, try to run script once again")
            continue

        fn = f"faktury/{item['no'].replace('/', '-')}.pdf"

        if os.path.exists(fn):
            print("file already exists")
            continue

        res = requests.get(f"{icp_api_url}/finance/invoices/{item['id']}/download-file", headers=headers)
        download_url = res.json()['downloadUrl']

        res = requests.get(download_url)

        with open(fn, 'wb') as f:
            f.write(res.content)
        print("done")




