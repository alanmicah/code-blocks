# from ...platforms.act_crm imp
import requests
import os
from dotenv import load_dotenv
import json
import time

print()
print()
print()
load_dotenv()


###################### ACT DETAILS ######################

api_base_url = "https://apiuk.act.com/act.web.api"
act_opportunities_url = "https://apiuk.act.com/act.web.api/api/opportunities"
act_get_auth_token_url = "https://apiuk.act.com/act.web.api/authorize"

bearer_token = os.environ.get("DOORMATIC_ACT_BEARER_KEY")
temporary_bearer_token = ""
# params = {
#     "$filter": "created gt 2023-08-01T08:00:00Z and created lt 2023-09-01T08:00:00Z"
# }
auth_headers = {
    "Act-Database-Name": "Doormatic",
    "Authorization": f"Bearer {bearer_token}",
}

###################### AIRTABLE DETAILS ######################

airtable_key = os.environ.get("DOORMATIC_AIRTABLE_KEY")
baseId = "appga9Mr4rk0qIOy5"
tableIdOrName = "Opportunities"
airtable_create_records_url = f"https://api.airtable.com/v0/{baseId}/{tableIdOrName}"
airtable_headers = {"Authorization": f"Bearer {airtable_key}"}

###################### SCRIPT ######################


def upload_months_act_data_to_airtable(start_date, end_date):
    opportunities = get_act_opportunities(start_date, end_date)
    print(len(opportunities))
    add_opportunities_to_airtable(opportunities)

def get_act_opportunities(start_date, end_date):

  opportunities_url = f"{api_base_url}/api/opportunities"

  params = {
      "$filter":
      f"created gt {start_date['year']}-{str(start_date['month']).zfill(2)}-01T08:00:00Z and created lt {end_date['year']}-{str(end_date['month']).zfill(2)}-01T08:00:00Z"
  }
  headers = get_up_to_date_authorisation()
  print(params)
  response = requests.get(opportunities_url,
                          params=params,
                          headers=headers)

  opportunities = response.json()
  
  return opportunities


def get_up_to_date_authorisation():
    response = requests.get(act_get_auth_token_url, headers=auth_headers)

    temporary_bearer_token = response.text
    headers = {
        "Act-Database-Name": "Doormatic",
        "Authorization": f"Bearer {temporary_bearer_token}",
    }
    return headers


def add_opportunities_to_airtable(opportunities):
    records = []
    for i in range(len(opportunities)):
        opportunity = opportunities[i]
        record = create_record_object(opportunity)
        records.append(record)

        if (i + 1) % 10 == 0 or i + 1 == len(opportunities):
            request_body = create_request_body(records)
            post_data_to_airtable(request_body)
            print()

            for record in records:
                print(
                    record["fields"]["contactNames"],
                
                    record["fields"]["actID"],
                )

            records = []

            print()


def create_record_object(opportunity):

    contact_id = opportunity['contacts'][0]['id'] if len(opportunity['contacts']) > 0 else None
    record  = {
        "fields": {
        'actID': opportunity['id'],
        'opportunity name': opportunity['name'],
        'actualCloseDate': opportunity['actualCloseDate'],
        'contactNames': opportunity['contactNames'],
        'contactID': contact_id,
        'creator': opportunity['creator'],
        'daysOpen': opportunity['daysOpen'],
        'daysInStage': opportunity['daysInStage'],
        'estimatedCloseDate': opportunity['estimatedCloseDate'],
        'stageStartDate': opportunity['stageStartDate'],
        'grossMargin': opportunity['grossMargin'],
        'manager': opportunity['manager'],
        'openDate': opportunity['openDate'],
        'probability': opportunity['probability'],
        'productTotal': opportunity['productTotal'],
        'stageID': opportunity['stage']['id'],
        'stageName': opportunity['stage']['name'],
        'processID': opportunity['stage']['process']['id'],
        'processName': opportunity['stage']['process']['name'],
        'totalPerContact': opportunity['totalPerContact'],
        'weightedTotal': opportunity['weightedTotal'],
        'created': opportunity['created'],
        'edited': opportunity['edited']
            }
        }
    return record


def create_request_body(records):
    request_body = {"records": records}
    return request_body


def post_data_to_airtable(data):
    response = requests.post(
        airtable_create_records_url,
        json=data,
        headers=airtable_headers,
    )

    print()
    print()
    print(response.status_code)
    return response.json()



dates = [
    {"year": 2023, "month": 9},
    {"year": 2023, "month": 8},
    {"year": 2023, "month": 7},
    {"year": 2023, "month": 6},
    {"year": 2023, "month": 5},
    {"year": 2023, "month": 4},
    {"year": 2023, "month": 3},
    {"year": 2023, "month": 2},
    {"year": 2023, "month": 1},
    {"year": 2022, "month": 12},
    {"year": 2022, "month": 11},
    {"year": 2022, "month": 10},
    {"year": 2022, "month": 9},
    {"year": 2022, "month": 8},
    {"year": 2022, "month": 7},
    {"year": 2022, "month": 6},
    {"year": 2022, "month": 5},
    {"year": 2022, "month": 4},
    {"year": 2022, "month": 3},
    {"year": 2022, "month": 2},
    {"year": 2022, "month": 1},
    {"year": 2021, "month": 12},
    {"year": 2021, "month": 11},
    {"year": 2021, "month": 10},
    {"year": 2021, "month": 9},
    {"year": 2021, "month": 8},
    {"year": 2021, "month": 7},
    {"year": 2021, "month": 6},
    {"year": 2021, "month": 5},
    {"year": 2021, "month": 4},
    {"year": 2021, "month": 3},
    {"year": 2021, "month": 2},
    {"year": 2021, "month": 1},
    {"year": 2020, "month": 12},
    {"year": 2020, "month": 11},
    {"year": 2020, "month": 10},
    {"year": 2020, "month": 9},
    {"year": 2020, "month": 8},
    {"year": 2020, "month": 7},
    {"year": 2020, "month": 6},
    {"year": 2020, "month": 5},
    {"year": 2020, "month": 4},
    {"year": 2020, "month": 3},
    {"year": 2020, "month": 2},
    {"year": 2020, "month": 1},
    {"year": 2019, "month": 12},
    {"year": 2019, "month": 11},
    {"year": 2019, "month": 10},
    {"year": 2019, "month": 9},
    {"year": 2019, "month": 8},
    {"year": 2019, "month": 7},
    {"year": 2019, "month": 6},
    {"year": 2019, "month": 5},
    {"year": 2019, "month": 4},
    {"year": 2019, "month": 3},
    {"year": 2019, "month": 2},
    {"year": 2019, "month": 1},
    
]



for i in range(0, len(dates) - 1):
    start_date = dates[i + 1]
    end_date = dates[i]

    upload_months_act_data_to_airtable(start_date, end_date)



print()
print()
print()

# opportunity = {'id': '7be4a0d6-8f05-4f5f-9c6f-80e268af29f0', 'name': '[23101] John Atkins', 'actualCloseDate': '9999-12-31T00:00:00+00:00', 
#                'companies': [], 'competitor': None, 'contactNames': 'John Atkins', 'contacts': [{'id': '09d8fec6-0ccd-46d7-b32c-860a930b3088', 'displayName': 'John Atkins', 'company': None}],
#                  'creator': 'System', 'daysOpen': 91, 'daysInStage': 91, 'estimatedCloseDate': '2023-08-17T00:00:00+00:00', 'stageStartDate': '2023-08-17T00:00:00+00:00',
#                    'grossMargin': 2096.4, 'manager': 'System', 'openDate': '2023-08-17T00:00:00+00:00', 'probability': 100, 'productTotal': 2096.4, 
#                    'stage': {'id': 'f47b54dc-6463-423c-b04f-a523fe3cc93d', 'name': 'Installation Booked', 'description': '',  'probability': 100, 'number': 4, 
#                 'process': {'id': '3c8fd817-06ab-46c9-813b-5a7e70216319', 'name': 'DM Orders', 'description': '', 'status': 'Active', 'stagesCount': 5, 'stages': []}}, 
#                 'status': 0, 'importDate': None, 'totalPerContact': 2096.4, 'weightedTotal': 2096.4,
#                 'relatedEntitiesResolver': True, 'created': '2023-08-17T15:50:18+00:00', 'edited': '2023-09-22T14:08:32+00:00'}


# # print(record['fields'].values())

# opportunity_csv_headers = {'id': '7be4a0d6-8f05-4f5f-9c6f-80e268af29f0', 'name': '[23101] John Atkins', 'actualCloseDate': '9999-12-31T00:00:00+00:00', 
#              'contactNames': 'John Atkins', 'contactID': '09d8fec6-0ccd-46d7-b32c-860a930b3088',
#                  'creator': 'System', 'daysOpen': 91, 'daysInStage': 91, 'estimatedCloseDate': '2023-08-17T00:00:00+00:00', 'stageStartDate': '2023-08-17T00:00:00+00:00',
#                    'grossMargin': 2096.4, 'manager': 'System', 'openDate': '2023-08-17T00:00:00+00:00', 'probability': 100, 'productTotal': 2096.4, 
                   
#                    "stageID" :'f47b54dc-6463-423c-b04f-a523fe3cc93d', "stageName":  'Installation Booked', "processID": "3c8fd817-06ab-46c9-813b-5a7e70216319", "processName": 'DM Orders',  
#                 'totalPerContact': 2096.4, 'weightedTotal': 2096.4,
#                'created': '2023-08-17T15:50:18+00:00', 'edited': '2023-09-22T14:08:32+00:00'}





"""



for year in range(2023, 2015, -1):
    for month in range(12, 0, -1):
        dates.append({"year": year, "month": month})
        # upload_months_act_data_to_airtable(year, month)
        # print(f"created gt {year}-{str(month).zfill(2)}-01T08:00:00Z")
print(dates)

"""

# {"year": 2023, "month": 12},
# {"year": 2023, "month": 11},
# {"year": 2023, "month": 10},
# {"year": 2023, "month": 9},
# {"year": 2023, "month": 8},
# {"year": 2023, "month": 7},
# {"year": 2023, "month": 6},
# {"year": 2023, "month": 5},
# {"year": 2023, "month": 4},
# {"year": 2023, "month": 3},
# {"year": 2023, "month": 2},
# {"year": 2023, "month": 1},
# {"year": 2022, "month": 12},
# {"year": 2022, "month": 11},
# {"year": 2022, "month": 10},
# {"year": 2022, "month": 9},
# {"year": 2022, "month": 8},
# {"year": 2022, "month": 7},
# {"year": 2022, "month": 6},
# {"year": 2022, "month": 5},
# {"year": 2022, "month": 4},
# {"year": 2022, "month": 3},
