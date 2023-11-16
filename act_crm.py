
import requests
import json
import os
from dotenv import load_dotenv


api_base_url = "https://apiuk.act.com/act.web.api"
act_get_filtered_contacts_url = f"{api_base_url}/api/contacts"

bearer_token = ""  # os.environ.get("DOORMATIC_ACT_BEARER_KEY")
# print(f'Act! TKN loaded')
temporary_bearer_token = ""

auth_headers = {
    "Act-Database-Name": "Doormatic",
    "Authorization": f"Bearer {bearer_token}",
}


def get_up_to_date_authorisation():
  endpoint = f"{api_base_url}/authorize"
  response = requests.get(endpoint, headers=auth_headers)

  temporary_bearer_token = response.text
  headers = {
      "Act-Database-Name": "Doormatic",
      "Authorization": f"Bearer {temporary_bearer_token}",
  }
  return headers


def get_contacts_from_act(start_date, end_date):
  params = {
      "$filter":
      f"created gt {start_date['year']}-{str(start_date['month']).zfill(2)}-01T08:00:00Z and created lt {end_date['year']}-{str(end_date['month']).zfill(2)}-01T08:00:00Z"
  }
  headers = get_up_to_date_authorisation()
  print(params)
  response = requests.get(act_get_filtered_contacts_url,
                          params=params,
                          headers=headers)
  # if response.status_code == 401:
  #     raise Exception("401")

  contacts = response.json()
  return contacts


def get_act_notes(object_type, object_id):
  """
  Gets all notes from Act CRM for a given object (e.g. contacts, opportunities, companies).
  """
  headers = get_up_to_date_authorisation()
  endpoint = f"{api_base_url}/api/{object_type}/{object_id}/notes"
  response = requests.get(endpoint, headers=headers)
  notes = response.json()
  return notes
