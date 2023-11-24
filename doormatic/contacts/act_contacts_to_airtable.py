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

act_get_filtered_contacts_url = "https://apiuk.act.com/act.web.api/api/contacts"
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
baseId = "appRTap2n6PrB3JXt"
tableIdOrName = "Contacts"
airtable_create_records_url = f"https://api.airtable.com/v0/{baseId}/{tableIdOrName}"
airtable_headers = {"Authorization": f"Bearer {airtable_key}"}

###################### SCRIPT ######################


def upload_months_act_data_to_airtable(start_date, end_date):
    contacts = get_contacts_from_act(start_date, end_date)
    # print(len(contacts))
    # add_contacts_to_airtable(contacts)


def get_contacts_from_act(start_date, end_date):
    params = {
        "$filter": f"created gt {start_date['year']}-{str(start_date['month']).zfill(2)}-01T08:00:00Z and created lt {end_date['year']}-{str(end_date['month']).zfill(2)}-01T08:00:00Z"
    }
    headers = get_up_to_date_authorisation()
    print(params)
    response = requests.get(
        act_get_filtered_contacts_url, params=params, headers=headers
    )
    # if response.status_code == 401:
    #     raise Exception("401")

    contacts = response.json()
    return contacts


def get_up_to_date_authorisation():
    response = requests.get(act_get_auth_token_url, headers=auth_headers)

    temporary_bearer_token = response.text
    
    print(temporary_bearer_token)
    headers = {
        "Act-Database-Name": "Doormatic",
        "Authorization": f"Bearer {temporary_bearer_token}",
    }
    return headers


def add_contacts_to_airtable(contacts):
    records = []
    for i in range(len(contacts)):
        # print(json.dumps(contact))
        contact = contacts[i]
        record = create_record_object(contact)
        records.append(record)

        if (i + 1) % 10 == 0 or i + 1 == len(contacts):
            request_body = create_request_body(records)
            post_data_to_airtable(request_body)
            print()

            for record in records:
                print(
                    record["fields"]["First Name"],
                    record["fields"]["Surname"],
                    record["fields"]["Act ID"],
                )

            records = []

            print()


def create_record_object(contact):
    record = {
        "fields": {
            "Act ID": contact["id"],
            "E-mail": contact["emailAddress"],
            "First Name": contact["firstName"],
            "Surname": contact["lastName"],
            "Salutation": contact["salutation"],
            "Name Prefix": contact["namePrefix"],
            "Mobile Phone": contact["mobilePhone"],
            "AEM Opt Out": contact["aemOptOut"],
            "Favorite": contact["isFavorite"],
            "Is User": contact["isUser"],
            "Private Contact": contact["isPrivate"],
            "Is Imported": contact["isImported"],
            "Address 1": contact["businessAddress"]["line1"],
            "Address 2": contact["businessAddress"]["line2"],
            "Address 3": contact["businessAddress"]["line3"],
            "Postcode": contact["businessAddress"]["postalCode"],
            "County": contact["businessAddress"]["state"],
            "City": contact["businessAddress"]["city"],
            "Company": contact["company"],
            "Create Date": contact["created"],
            "Edit Date": contact["edited"],
            "Last Edited By": contact["editedBy"],
            "Referred By": contact["referredBy"],
            "Record Manager": contact["recordManager"],
            "Record Manager ID": contact["recordManagerID"],
            "Last Reach": contact["lastReach"],
            "Supply": contact["customFields"]["user4"],
            "Motors": contact["customFields"]["motors"],
            "Door Make": contact["customFields"]["user5"],
            "Motor Manufacturer": contact["customFields"]["user6"],
            "Type of Contact": contact["customFields"]["user7"],
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
    ).json()
    return response


dates = [
    {"year": 2014, "month": 2},
    {"year": 2014, "month": 1},
    {"year": 2013, "month": 12},
    {"year": 2013, "month": 11},
    {"year": 2013, "month": 10},
    {"year": 2013, "month": 9},
    {"year": 2013, "month": 8},
    {"year": 2013, "month": 7},
    {"year": 2013, "month": 6},
    {"year": 2013, "month": 5},
    {"year": 2013, "month": 4},
    {"year": 2013, "month": 3},
    {"year": 2013, "month": 2},
    {"year": 2013, "month": 1},
    {"year": 2012, "month": 12},
    {"year": 2012, "month": 11},
    {"year": 2012, "month": 10},
    {"year": 2012, "month": 9},
    {"year": 2012, "month": 8},
    {"year": 2012, "month": 7},
    {"year": 2012, "month": 6},
    {"year": 2012, "month": 5},
    {"year": 2012, "month": 4},
    {"year": 2012, "month": 3},
    {"year": 2012, "month": 2},
    {"year": 2012, "month": 1},
    {"year": 2011, "month": 12},
    {"year": 2011, "month": 11},
    {"year": 2011, "month": 10},
    {"year": 2011, "month": 9},
    {"year": 2011, "month": 8},
    {"year": 2011, "month": 7},
    {"year": 2011, "month": 6},
    {"year": 2011, "month": 5},
    {"year": 2011, "month": 4},
    {"year": 2011, "month": 3},
    {"year": 2011, "month": 2},
    {"year": 2011, "month": 1},
    {"year": 2010, "month": 12},
    {"year": 2010, "month": 11},
    {"year": 2010, "month": 10},
    {"year": 2010, "month": 9},
    {"year": 2010, "month": 8},
    {"year": 2010, "month": 7},
    {"year": 2010, "month": 6},
    {"year": 2010, "month": 5},
    {"year": 2010, "month": 4},
    {"year": 2010, "month": 3},
    {"year": 2010, "month": 2},
    {"year": 2010, "month": 1},
    {"year": 2009, "month": 12},
    {"year": 2009, "month": 11},
    {"year": 2009, "month": 10},
    {"year": 2009, "month": 9},
    {"year": 2009, "month": 8},
    {"year": 2009, "month": 7},
    {"year": 2009, "month": 6},
    {"year": 2009, "month": 5},
    {"year": 2009, "month": 4},
    {"year": 2009, "month": 3},
    {"year": 2009, "month": 2},
    {"year": 2009, "month": 1},
    {"year": 2008, "month": 12},
    {"year": 2008, "month": 11},
    {"year": 2008, "month": 10},
    {"year": 2008, "month": 9},
    {"year": 2008, "month": 8},
    {"year": 2008, "month": 7},
    {"year": 2008, "month": 6},
    {"year": 2008, "month": 5},
    {"year": 2008, "month": 4},
    {"year": 2008, "month": 3},
    {"year": 2008, "month": 2},
    {"year": 2008, "month": 1},
]

for i in range(0, len(dates) - 1):
    start_date = dates[i + 1]
    end_date = dates[i]

    upload_months_act_data_to_airtable(start_date, end_date)
    break

print()
print()
print()

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
