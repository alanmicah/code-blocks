import requests
import os
# from dotenv import load_dotenv
import json
import time
import act_crm
import csv

import airtable
import utilities

print()
print()
print()
# load_dotenv()
auth = utilities.retrieve_dict('.env2')

###################### GLOBALS ######################
main_directory = "doormatic/"
data_directory = "data/"
data_store_filename = "data_store.json"
processed_contacts_store_filename = "processed_contacts.json"
processed_objects_store_filename = "processed_<OBJECT_TYPE>.json"
contact_note_records_store_filename = "contacts_note_records.json"
object_note_records_store_filename = "<OBJECT_TYPE>_note_records.json"

objects_csv_filename = "<OBJECT_TYPE>.csv"
contacts_filename = "contacts.csv"
notes_filename = "notes.csv"

max_number_of_contacts = 5000

contact_id_column = 1  # Zero indexed
total_contacts_processed = 0  # For console logging

###################### ACT DETAILS ######################

act_bearer_token = os.environ.get("DOORMATIC_ACT_BEARER_KEY")
act_bearer_token = auth.get("DOORMATIC_ACT_BEARER_KEY")
act_crm.auth_headers["Authorization"] = f"Bearer {act_bearer_token}"  # Set token in act_crm
print(f'Act! TKN loaded')

###################### AIRTABLE DETAILS ######################

airtable_key = os.environ.get("DOORMATIC_AIRTABLE_PAT")
act_bearer_token = auth.get("DOORMATIC_AIRTABLE_PAT")
airtable.headers["Authorization"] = f"Bearer {airtable_key}"  # Set token in airtable
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
            first_column = row[0]
            if not first_column == '':
                if first_column[0] != '#':  # Ignore comment lines
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


def add_notes_to_airtable(mapped_notes):
    """ mapped_notes are mapped to record fields"""
    records = []
    for index, note in enumerate(mapped_notes):
        records.append(note)
        if (index + 1) % 10 == 0 or index + 1 == len(mapped_notes):
            try:
                # Batch upload every ten records
                airtable_response = airtable.create_multiple_records(baseId, tableIdOrName, records)
                print(utilities.headline(f'Batch Uploaded to Airtable', '>', 100) + '\n\n')
            except:
                print(utilities.headline(f'Error When Uploading to Airtable', '<', 100) + '\n\n')

            for record in records:
                print(
                    f'Note: {record["fields"]["Act Note ID"]}'
                )
            # Re-initialise the records list
            records = []


def create_record_object(note):
    # Handle arrays which may be empty
    try:
        note_contact = note["contacts"][0]["id"]
    except TypeError:
        note_contact = None

    try:
        note_company = note["companies"][0]["id"]
    except TypeError:
        note_company = None

    try:
        note_opportunity = note["opportunities"][0]["id"]
    except TypeError:
        note_opportunity = None

    record = {
        "fields": {
            "Act Note ID": note["id"],
            "Act Contact ID": note_contact,
            "Act Creator ID": note["createUserID"],
            "Act Company ID": note_company,
            "Act Opportunity ID": note_opportunity,
            "Note Text": note["noteText"],
            "Note Type ID": str(note["noteTypeID"]),
            "Private Note": str(note["isPrivate"]),
            "Create Date": note["created"],
            "Edit Date": note["edited"]
        }
    }

    return record


def download_notes(object_type):
    # Initialise array of notes
    all_notes = []
    all_mapped_notes = []
    mapped_notes_for_csv = []
    new_processed_objects = []
    # Initialise data store json files
    # data_store_filepath = f'{data_directory}{data_store_filename}'
    # data_store = utilities.retrieve_dict(data_store_filepath)
    # processed_contacts = data_store.get('processed_contact_ids')
    processed_contacts_store = utilities.retrieve_dict(f'{data_directory}{processed_contacts_store_filename}')
    processed_contacts = processed_contacts_store.get('processed_contact_ids')
    existing_notes_store = utilities.retrieve_dict(f'{data_directory}{contact_note_records_store_filename}')
    # print(f'Existing notes:\n{existing_notes_store}')
    if not processed_contacts:
        processed_contacts = []
    # Get contacts from csv
    all_contacts = utilities.import_csv_file(f'{data_directory}{contacts_filename}')

    # Iterate N contacts and retrieve notes associated with each contact id
    contact_counter = 0
    for row_num, contact in enumerate(all_contacts):
        if row_num > 0:  # Skip header
            if contact_counter < max_number_of_contacts + 1:
                contact_id = contact[contact_id_column]
                if contact_id not in processed_contacts:
                    contact_notes = act_crm.get_act_notes('contacts', contact_id)
                    print(f'Contact notes: {json.dumps(contact_notes)}')
                    try:
                        # Append notes to list of all_notes
                        all_notes = all_notes + contact_notes
                        # Append contact_id to processed_contacts
                        new_processed_objects.append(contact_id)
                    except TypeError:
                        print(headline(f'ERROR with ID : {contact_id}', '*', 100))
                    contact_counter += 1

                    if contact_counter == max_number_of_contacts:
                        break

    # Map Notes data into Airtable structure
    for note in all_notes:
        mapped_note = create_record_object(note)
        all_mapped_notes.append(mapped_note)
        mapped_notes_for_csv.append(mapped_note.get('fields'))

    # Upload notes to Airtable
    add_notes_to_airtable(all_mapped_notes)
    # Save notes in csv
    if len(mapped_notes_for_csv) > 0:
        utilities.write_to_csv(f'{data_directory}{notes_filename}', mapped_notes_for_csv)

    # Save Notes and processed contact ids data into json file
    # existing_notes = data_store.get('note_records')
    existing_notes = existing_notes_store.get('note_records')
    if not existing_notes:
        existing_notes = []
    if not processed_contacts:
        processed_contacts = []
    # data_store['note_records'] = existing_notes + all_mapped_notes
    # data_store['processed_contact_ids'] = processed_contacts + new_processed_contacts
    existing_notes_store['note_records'] = existing_notes + all_mapped_notes
    processed_contacts_store['processed_contact_ids'] = processed_contacts + new_processed_objects
    try:
        # print(headline(f"{len(data_store['processed_contact_ids'])} contacts processed", '=', 100))
        print(headline(f"{len(processed_contacts_store['processed_contact_ids'])} contacts processed", '=', 100))
    except:
        ''
    utilities.store_dict(processed_contacts_store, f'{data_directory}{processed_contacts_store_filename}')
    utilities.store_dict(existing_notes_store, f'{data_directory}{contact_note_records_store_filename}')


start_time = time.time()
print(headline(f'Process start', '=', 100))
download_notes("contacts")
end_time = time.time()
time_delta = int((end_time - start_time) * 1000) / 1000
print(headline(f'Process end ({time_delta} s)', '=', 100))

