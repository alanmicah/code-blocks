import requests
import os
from dotenv import load_dotenv
import json
import time
import act_crm
import csv

print()
print()
print()
load_dotenv()

###################### GLOBALS ######################
main_directory = "doormatic/"
data_directory = "data/"
data_store_filename = "data_store.json"
contacts_filename = "contacts.csv"
notes_filename = "notes.csv"

number_of_contacts = 1

###################### ACT DETAILS ######################

act_bearer_token = os.environ.get("DOORMATIC_ACT_BEARER_KEY")
act_crm.bearer_token = act_bearer_token  # Set token in act_crm
print(f'Act! TKN loaded')

###################### AIRTABLE DETAILS ######################

airtable_key = os.environ.get("DOORMATIC_AIRTABLE_PAT")
print(f'AT TKN loaded')
baseId = "appWegstR7Zgo3Izd"
tableIdOrName = "Notes"


###################### SCRIPT ######################


def import_csv_file(csv_file_path):
    try:
        csv_file = open(csv_file_path, 'r')
    except FileNotFoundError:
        return []
    output_array = []

    with csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row[0][0] != '#':  # Ignore comment lines
                output_array.append(row)

    return output_array


def store_dict(dict_payload, filename):
    dict_as_str = json.dumps(dict_payload)
    with open(filename, 'w') as file:
        file.write(dict_as_str)
    file.close()

    return 'success'


def retrieve_dict(filepath):
    try:
        with open(filepath, "r") as file:
            output_str = ''
            for line in file:
                # print(f'line = {line}')
                # line = line.decode('utf-8','ignore').encode("utf-8")
                output_str = output_str + line
            # print(f'str 1 = {output_str}')

        # print(f'str 2 = {output_str}')
        dict_payload = json.loads(output_str)
    # print(f'dict loaded')
    except:
        dict_payload = {}
    return dict_payload


def check_rate_limit_ok(rate_limit_data):
    now = time.time()
    start_time = rate_limit_data.get('start_time')
    if not rate_limit_data.get('start_time'):
        rate_limit_data['start_time'] = now
        rate_limit_data['counter'] = 1
        return True

    time_delta = now - start_time
    if time_delta > rate_limit_data.get('time_value'):
        # Have crossed into new time unit - reset counter
        rate_limit_data['counter'] = 1
        rate_limit_data['start_time'] = now
        # rate_limit_data['reset_delta'] = None
        return True
    elif rate_limit_data.get('counter') < rate_limit_data.get('number'):
        # Below limit
        counter = rate_limit_data.get('counter')
        rate_limit_data['counter'] = counter + 1
        return True
    else:
        # Have exceeded limit, append reset_delta
        reset_delta = rate_limit_data.get('time_value') - time_delta
        # rate_limit_data['reset_delta'] = rate_limit_data.get('time_value') - time_delta
        time.sleep(reset_delta)
        rate_limit_data['start_time'] = time.time()
        rate_limit_data['counter'] = 1
        return True


def headline(text, symbol, width):
    return f" {text} ".center(width, symbol)


def upload_months_act_data_to_airtable(start_date, end_date):
    contacts = get_contacts_from_act(start_date, end_date)
    print(len(contacts))
    add_contacts_to_airtable(contacts)


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


def create_record_object(note):
    record = {
        "fields": {
            "Act Note ID": note["id"],
            "Act Contact ID": note["contacts"][0]["id"],
            "Act Creator ID": note["createUserID"],
            "Act Company ID": note["companies"][0]["id"],
            "Act Opportunity ID": note["opportunities"][0]["id"],
            "Note Text": contact["noteText"],
            "Note Type ID": contact["noteTypeID"],
            "Private Note": contact["isPrivate"],
            "Create Date": contact["created"],
            "Edit Date": contact["edited"]
        }
    }

    return record


def main():
# Get contacts from csv

# Iterate N contacts and retrieve notes associated with each contact id

# Map Notes data into Airtable structure

# Save Notes data into json file

# Upload notes to Airtable

# Store processed contact ids in data_store
