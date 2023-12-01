import requests
import os
from dotenv import load_dotenv
import json
import time
import pandas as pd
import numpy as np
import os
import urllib

print()
print()
print()
load_dotenv()
# pd.set_option('display.max_columns', None)


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
airtable_headers = {"Authorization": f"Bearer {airtable_key}"}

###################### SCRIPT ######################

def migrate_notes_to_hubspot(csv_files):

    for csv_files in csv_files:
        
        migrate_csv_notes_to_hubspot(csv_files)
        break


def migrate_csv_notes_to_hubspot(csv_file):

    contacts_df = read_and_clean_csv(csv_file)
    for _, contact in contacts_df.loc[pd.isna(contacts_df["hubspot ID"])].iterrows():
        
        print()
        print()
        print()

        husbpot_id_exists = not pd.isna(contact["hubspot ID"])
        if husbpot_id_exists:
            print(contact["hubspot ID"], 'exists')
            continue

        hubspot_ID = get_contact_hubspotID(contact)     
        

        if hubspot_ID == None:
            print('skip')
            continue
     
        contacts_df.loc[contacts_df['Act Contact ID'] == contact['Act Contact ID'], ['hubspot ID']] = hubspot_ID
       
        print(hubspot_ID)

        # print(contact)
        # print(contacts_df)
        # break

    # contacts_df = add_hubspot_id_column(contacts_df)
    save_csv(csv_file, contacts_df)


def read_and_clean_csv(csv_file):
     
    filepath = f"doormatic/data/{csv_file}"

    contacts_df = pd.read_csv(filepath, low_memory=False)
    print("Read: ", filepath)

    print(contacts_df)
    return contacts_df


def get_contact_hubspotID(contact):

    params = get_airtable_params(contact)
    airtable_record_url = f"https://api.airtable.com/v0/{baseId}/{tableIdOrName}"

    try: 
        response = requests.get(airtable_record_url, params=params, headers=airtable_headers)
    

        if response.status_code != 200:
            return
        
        print("success")

        record_exists = len(response.json()['records']) >0
        if record_exists:
            record = response.json()['records'][0]
            return int(record["fields"]["Hubspot ID"]) 
        
    except:
        print("couldn't get hubspot ID")
        return 


def get_airtable_params(contact):
    
    act_contact_id = contact["Act Contact ID"]
    formula = f"{{Act ID}} = \"{act_contact_id}\""
    params = {"filterByFormula": formula, "fields[]": "Hubspot ID"}
    return params


def add_hubspot_id_column(dataframe):

    dataframe['hubspot ID'] = np.NAN
    return dataframe


def save_csv(csv_file, dataframe):
    
    filepath = f"doormatic/data/{csv_file}"

    dataframe.to_csv(filepath, index=False)
    print("Updates have been saved")

csv_files= ['notes_contacts_1s.csv', 'notes_contacts_2.csv', 'notes_contacts_3.csv', 'notes_contacts_4.csv', 'notes_contacts_5.csv', 'notes_contacts_6.csv', 'notes_contacts_7.csv', 'notes_contacts_8.csv', 'notes_contacts_9.csv', 'notes_contacts_10.csv', 'notes_contacts_11.csv', 'notes_contacts_12.csv']
csv_files= ['notes_contacts_3.csv']

migrate_notes_to_hubspot(csv_files)
