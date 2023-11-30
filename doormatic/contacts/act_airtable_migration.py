# Contact from 31 October 2018 to now

import os
from dotenv import load_dotenv
import pandas as pd
import requests
import json

print()
print()
print()

load_dotenv()

airtable_key = os.environ.get("DOORMATIC_AIRTABLE_KEY")
baseId = "appga9Mr4rk0qIOy5"
tableIdOrName = "Contacts Table"
airtable_create_record_url = f"https://api.airtable.com/v0/{baseId}/{tableIdOrName}"


def read_and_clean_csv():
    contacts_df = pd.read_csv("assets/contacts-2019.csv", low_memory=False)

    # Filter contacts that have been imported
    contacts_df = contacts_df[contacts_df["Imported"] != True]
    contacts_df[["Business Latitude", "Business Longitude"]] = contacts_df[
        ["Business Latitude", "Business Longitude"]
    ].fillna(0)
    contacts_df = contacts_df.fillna("")

    # #
    # contacts_df["Business Latitude"] = (
    #     contacts_df[["Business Latitude"]]fillna(0)
    # )
    # .apply(pd.to_numeric).

    print(contacts_df["Business Latitude"])

    # replace bools with strings
    mask = contacts_df.applymap(type) != bool
    bool_to_string = {True: "TRUE", False: "FALSE"}
    contacts_df = contacts_df.where(mask, contacts_df.replace(bool_to_string))

    return contacts_df


def create_request_body(start_index, end_index, contacts_df):
    records = []

    for i in range(start_index, end_index):
        contact = contacts_df.iloc[i]
        record = {
            "fields": {
                "Surname": contact["Surname"],
                "Business Latitude": contact["Business Latitude"],
                "Favorite": contact["Favorite"],
                "Mobile Phone": contact["Mobile Phone"],
                "E-mail": contact["E-mail"],
                "Create Date": contact["Create Date"],
                "Access Level": contact["Access Level"],
                "Postcode": contact["Postcode"],
                "AEM Opt Out": contact["AEM Opt Out"],
                "Is User": contact["Is User"],
                "Record Manager": contact["Record Manager"],
                "Contact": contact["Contact"],
                "Address 1": contact["Address 1"],
                "AEM Bounce Back": contact["AEM Bounce Back"],
                "Address 3": contact["Address 3"],
                "Private Contact": contact["Private Contact"],
                "Is Imported": contact["Is Imported"],
                "City": contact["City"],
                "Salutation": contact["Salutation"],
                "Last Reach": contact["Last Reach"],
                "Record Creator": contact["Record Creator"],
                "First Name": contact["First Name"],
                "Edit Date": contact["Edit Date"],
                "Business Longitude": contact["Business Longitude"],
                "Machine Compliance Cert": contact["Machine Compliance Cert"],
                "Last Edited By": contact["Last Edited By"],
            }
        }
        records.append(record)

    print(records)

    data = {"records": records}
    # print(json.dumps(data))
    return data


def post_data_to_airtable(data):
    response = requests.post(
        airtable_create_record_url,
        json=data,
        headers={"Authorization": f"Bearer {airtable_key}"},
    ).json()

    print(response)
    return


def update_csv_row(i):
    contact = contacts_df.loc[i]
    contacts_df.loc[i, "Imported"] = "True"
    # print(contact)


contacts_df = read_and_clean_csv()

for i in range(0, len(contacts_df), 10):
    data = create_request_body(0, 3, contacts_df)
    post_data_to_airtable(data)
    # update_csv_row(i)
    break


# contacts_df.to_csv("assets/contacts-2023.csv")
