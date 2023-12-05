import sys
import html2text
# from admin import reformat_html_to_plain

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
pd.set_option('display.max_columns', None)


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

    notes_df = read_and_clean_csv(csv_file)
    print(notes_df.loc[: , "hubspot ID"])
    print(notes_df.columns)
    # notes_df = reformat_notes_to_plain_text(notes_df)
    # notes_df = notes_df.drop("Note Text", axis=1)

    # for _, note in notes_df.loc[pd.isna(notes_df["hubspot ID"])].iterrows():
        
    #     migrate_note_to_hubspot(note, notes_df)

    # save_csv(csv_file, notes_df)


def read_and_clean_csv(csv_file):
     
    filepath = f"doormatic/data/{csv_file}"

    notes_df = pd.read_csv(filepath, low_memory=False)
    # add_column_to_df(notes_df, "Plain Text Note")
    print("Read: ", filepath)

    notes_df['hubspot ID'] = notes_df['hubspot ID'].round().astype(int, errors='ignore')
    print(notes_df['hubspot ID'].dtype)

    return notes_df


def migrate_note_to_hubspot(note, notes_df):

    print()
    print()
    print()

    husbpot_id_exists = not pd.isna(note["hubspot ID"])
    if husbpot_id_exists:
        print(note["hubspot ID"], 'exists')
        return

    hubspot_ID = get_contact_hubspotID(note)     

    if hubspot_ID == None:
        print('skip')
        return
    
    notes_df.loc[notes_df['Act Contact ID'] == note['Act Contact ID'], ['hubspot ID']] = hubspot_ID
    
    print(hubspot_ID)   


def reformat_notes_to_plain_text(notes_df):

    for i, note in notes_df.iterrows():
        # print(reformat_html_to_plain(note['Note Text']))
        # print(note['Note Text'])
        notes_df.loc[i, "Plain Text Note"] = reformat_html_to_plain(note['Note Text'])

    return notes_df

def reformat_html_to_plain(html_text):
    # Handle some special characters
    # html_text = html_text.replace( / (< ([^ >]+) >) / gi, "");
    updated_text = html_text.replace('&pound;', '{GBP}')
    updated_text = updated_text.replace('&amp;', '{AND}')
    plain_text = html2text.html2text(updated_text)
    # Reinsert specials
    plain_text = plain_text.replace('{GBP}', '£')
    plain_text = plain_text.replace('{AND}', '&')
    # print(f'PLAIN:\n"{plain_text}\n\n"from HTML:\n"{html_text}"')
    return plain_text


def get_contact_hubspotID(note):

    params = get_airtable_params(note)
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


def get_airtable_params(note):
    
    act_contact_id = note["Act Contact ID"]
    formula = f"{{Act ID}} = \"{act_contact_id}\""
    params = {"filterByFormula": formula, "fields[]": "Hubspot ID"}
    return params


def add_column_to_df(dataframe, column_name):

    dataframe[column_name] = np.NAN
    return dataframe


def save_csv(csv_file, dataframe):
    
    filepath = f"doormatic/data/{csv_file}"

    dataframe.to_csv(filepath, index=False)
    print("Updates have been saved")

csv_files= ['notes_contacts_1s.csv', 'notes_contacts_2.csv', 'notes_contacts_3.csv', 'notes_contacts_4.csv', 'notes_contacts_5.csv', 'notes_contacts_6.csv', 'notes_contacts_7.csv', 'notes_contacts_8.csv', 'notes_contacts_9.csv', 'notes_contacts_10.csv', 'notes_contacts_11.csv', 'notes_contacts_12.csv']
csv_files= ['notes_contacts_3.csv']

migrate_notes_to_hubspot(csv_files)


test_note_string = '''const originalString = `
<span style="font-family:Arial; font-size: 13px;">1 x Novoferm Steel Made to Measure Georgian up &amp; over Retractable Garage Door finished in White  1 2638.00 25% Sales 20% (VAT on Income) 1978.50<br />
1 1 x Steel Frame finished in White 1 270.00 25% Sales 20% (VAT on Income) 202.50<br />
4 UPVC finishing trim in white 1 75.00 Sales - UPVC 20% (VAT on Income) 75.00<br />
6 Removal &amp; Disposal of existing garage door 1 30.00 Sales - Disposal 20% (VAT on Income) 30.00<br />
5 Installation 1 330.00 Sales 20% (VAT on Income) £330.00 & <br />
<br />
Total VAT 20.00%523.20<br />
TotalGBP &pound;3,139.20<br />
<br />
Optional Extras for Novoferm 1 x Novomatic 563 motor (c/w 2 remotes &amp; 1 internal wall unit): &pound;429+VAT 1 x Rubber Hump (fitted to the ground where the door will sit, helps prevent water from entering the garage): &pound;149+VAT 1 x Brush strip (prevent and debris from entering under the door): &pound;125+VAT</span>
`;'''
reformat_html_to_plain(test_note_string)
 