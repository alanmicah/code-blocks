import os, json, urllib.request, requests, re, csv
from dotenv import load_dotenv
from pyairtable import Api
import pandas as pd
from datetime import datetime

load_dotenv()

api = Api(os.environ['AIRTABLE_API_KEY'])
baseId = os.environ['AIRTABLE_BASE_ID']
# tableId = os.environ['TBL_ID_QUOTES']
tableId = 'transactions'
table = api.table(baseId, tableId)
xano = os.environ['XANO_API']
# print(table.all())

# with open('airtable_transactions_get.json', 'w') as filehandle:
#   json.dump(table.all(), filehandle)

# print(table.all(fields=['startTime', 'endTime']))

table_n = ["notifications"]

table_name_list = ["fcm_tokens",
"profiles",
"notifications",
"purchases",
"quotes",
"recording",
"rehearsal",
"recording_enquiries"
]
table_name_list_2 = [
  "studio-sign-ups-typeform",
  "rehearsal_enquiries",
  "test-quotes",
  "test-recording",
  "test-rehearsal",
  "transactions"
]

airtable_names = table_name_list + table_name_list_2

# table_name = "recording_enquiraies"
xano_table_data = requests.get(f'{xano}transactions')
# print(xano_table_data.status_code)
# print(json.loads(xano_table_data.text))

"""
Live function
"""
def create_json(name, data):
  with open(f'data/{name}.json', 'w') as filehandle:
    json.dump(data, filehandle)

"""
Live function
"""
def convert_json_to_csv(item, link, name):
  # for item in tables:
    # item += '_merge'
    if '-' in item:
       item = item.replace('-', '_')
    with open(f'data/{link}/{item}{name}.json', encoding='utf-8') as inputfile:
      df = pd.read_json(inputfile)
    df.to_csv(f'data/{link}/{item}{name}.csv', encoding='utf-8', index=False)

"""
Live function
"""
def is_iso_timestamp(timestamp):
  iso8601_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
  return re.match(iso8601_pattern, str(timestamp)) is not None

"""
Live function
"""
def create_json_per_table(tables):
  baseId = os.environ['AIRTABLE_BASE_ID']
  api = Api(os.environ['AIRTABLE_API_KEY'])
  data_tables = {}
  # table_data = []
  nested_dict = []
  for item in tables:
    table = api.table(baseId, item)
    table_data = table.all()
    nested_dict = [d['fields'] for d in table_data]
    print(item)
    for dict in nested_dict:
      for key, value in dict.items():
        if is_iso_timestamp(value):
          timestamp_str = value.rstrip('Z')
          timestamp_obj = datetime.fromisoformat(timestamp_str)
          # Convert to Epoch time (Unix timestamp)
          epoch_time = int(timestamp_obj.timestamp() * 1000)
          dict[key] = epoch_time 
      if 'id' in dict:
         dict['custom_id'] = dict.pop('id')
      if 'duration' in dict:
        dict['duration'] = str(dict['duration'])
    create_json('/air_c/'+item+'_airc', nested_dict)

def compare_key_per(tables, xano):
  baseId = os.environ['AIRTABLE_BASE_ID']
  api = Api(os.environ['AIRTABLE_API_KEY'])

  missing_data = []
  missing_keys_per_table = []
  n = 0
  for item in tables:
    n+=1
    print(n)
    table = api.table(baseId, item)
    if "-" in item:
      item = item.replace("-", "_")
      print(item)
      xano_table_data = requests.get(f'{xano}{item}')
      print(xano_table_data.status_code)
    else:
      xano_table_data = requests.get(f'{xano}{item}')
    if xano_table_data.status_code == 200:
      # print(xano_table_data.text)
      data = json.loads(xano_table_data.text)
      # Extract keys from the dictionaries in both lists
      keys_list1 = set().union(*[d['fields'].keys() for d in table.all()])
      # print(keys_list1)
      keys_list2 = set().union(*[d.keys() for d in data])
      # print('--------------------')
      # Find missing keys by taking the symmetric difference
      missing_keys_in_list1 = keys_list2 - keys_list1
      missing_keys_in_list2 = keys_list1 - keys_list2
      # print(missing_keys_in_list1)
      print('--------------------')
      print(missing_keys_in_list2)
      # print('')
      # print("Missing keys in list1:", missing_keys_in_list1)
      # print("Missing keys in list2:", missing_keys_in_list2)

      missing_keys = keys_list1.symmetric_difference(keys_list2)
      # print(missing_keys)
      missing_keys_per_table.append({item: missing_keys})
      
      create_json('/airtable/'+item+'_air', missing_keys_in_list2)
    # with open(f'{item}_keys.json', 'w') as filehandle:
    #     json.dump(missing_keys_in_list2, filehandle)
  # print(missing_keys_per_table)


def get_missing(table_name_list):
  baseId = os.environ['AIRTABLE_BASE_ID']
  api = Api(os.environ['AIRTABLE_API_KEY'])
  xano = os.environ['XANO_API']

  missing_data = []
  missing_keys_per_table = []
  xano = os.environ['XANO_API']
  table = api.table(baseId, item)
  for item in table_name_list:
    xano_table_data = requests.get(f'{xano}{item}')
    if xano_table_data.status_code == 200:
      # print(xano_table_data.text)
      data = json.loads(xano_table_data.text)
      # Extract keys from the dictionaries in both lists
      keys_list1 = set().union(*[d['fields'].keys() for d in table.all()])
      keys_list2 = set().union(*[d.keys() for d in data])

      # Find missing keys by taking the symmetric difference
      missing_keys_in_list1 = keys_list2 - keys_list1
      missing_keys_in_list2 = keys_list1 - keys_list2

      # print("Missing keys in list1:", missing_keys_in_list1)
      # print("Missing keys in list2:", missing_keys_in_list2)

      missing_keys = keys_list1.symmetric_difference(keys_list2)
      # print(missing_keys)
      missing_keys_per_table.append({item: missing_keys})

      # Initialize a dictionary to store missing keys and their values
      missing_values_dict = {}

      # Iterate through the dictionaries and find missing key-value pairs
      for key in missing_keys:
          for d in table.all():
              if key not in d['fields']:
                  continue
              missing_values_dict[key] = (d['fields'][key], None)
          for d in data:
              if key not in d:
                  continue
              if key in missing_values_dict:
                  missing_values_dict[key] = (missing_values_dict[key][0], d[key])
              else:
                  missing_values_dict[key] = (None, d[key])
      
      # missing_data.append(item)
      missing_data.append({item: missing_values_dict})
    else:
      print(xano_table_data.status_code)
      print(item, xano_table_data)
  missing_data[:0] = missing_keys_per_table
  create_json(missing_data)

  # with open('missing_data.json', 'w') as filehandle:
  #   json.dump(missing_data, filehandle)
# print(missing_keys_per_table)
###############
###############

# print(list_d[0]['fields'])

# for i in list_d:
#   print(i['fields'])

def compare_keys(air, xano):
  # Extract keys from the dictionaries in both lists

  keys_list1 = set().union(*[d.keys() for d in air])
  keys_list2 = set().union(*[d.keys() for d in xano])

  # Find missing keys by taking the symmetric difference
  missing_keys_in_list1 = keys_list2 - keys_list1
  missing_keys_in_list2 = keys_list1 - keys_list2

  # print("Missing keys in list1:", missing_keys_in_list1)
  # print("Missing keys in list2:", missing_keys_in_list2)

  missing_keys = keys_list1.symmetric_difference(keys_list2)
  # print(missing_keys)

  # Initialize a dictionary to store missing keys and their values
  missing_values_dict = {}

  # Iterate through the dictionaries and find missing key-value pairs
  # for key in missing_keys:
  #     for d in air:
  #         if key not in d:
  #             continue
  #         missing_values_dict[key] = (d[key], None)
  #     for d in xano:
  #         if key not in d:
  #             continue
  #         if key in missing_values_dict:
  #             missing_values_dict[key] = (missing_values_dict[key][0], d[key])
  #         else:
  #             missing_values_dict[key] = (None, d[key])
  # create_json('/xano_c/'++'_xanoc', data) 
  create_json("missing/profile_missing", missing_keys_in_list2)
  return missing_keys_in_list2

"""
Live function
"""
def compare_tables(tables):
  # n = 0
  for item in tables:
    # while n < 1:
    # Opening JSON file
    # print(item)
    a = open(f'data/air_c/{item}_airc.json')
    airData = json.load(a)
    if '-' in item:
      item = item.replace('-', '_')
    x = open(f'data/xano_c/{item}_xanoc.json')
    xanoData = json.load(x)
    # print(xanoData)
    # compare_keys(airData, xanoData)
    # merge_json(airData, xanoData, item)
    merge_data(airData, xanoData, item)
    # merge_only_missing(airData, xanoData, item)
    # n+=1
    # missing_keys(airData, xanoData, item)
    # find_missing_keys(xanoData, airData, item)


def data_types(table):
  field = table.all(fields=['snoozedUntil'])
  # print(type(field[0]))
  snoozeList = []
  for item in field:
    # print(item['id'], item['snoozedUntil'])
    snoozeList.append({"id": item['id'], "snoozedUntil": item['fields']['snoozedUntil']})

  return snoozeList

"""
Live function
"""
def get_xano(tablelist):
  xano = os.environ['XANO_API']
  for item in tablelist:
    if "-" in item:
      item = item.replace("-", "_")
    xano_table_data = requests.get(f'{xano}{item}')
    if xano_table_data.status_code == 200:
      data = json.loads(xano_table_data.text)
      create_json('/xano_c/'+item+'_xanoc', data)
    else:
      print(xano_table_data.status_code)
    # table = api.table(baseId, item)


def merge_json(airData, xanoData, name):
  # dict1_map = {d["id_1"]: d for d in xanoData if ('id_1' in d) or d == 'studio' ('studio_id')}
  dict1_map = {}

  for d in xanoData:
    if "custom_id" in d:
        dict1_map[d["custom_id"]] = d
    elif 'studios_id' in d:
       dict1_map[d["studio_id"]] = d
    elif 'Contact Name' in d:
       dict1_map[d["Contact Name"]] = d
  # Iterate through dict2
  for item in airData:
      print(item)
      if 'custom_id' in item:
        custom_id = item["custom_id"]
      elif 'studios_id' in d:
        custom_id = item['studio_id']
      elif 'Contact Name' in d:
        custom_id = item['Contact Name']
      else:
         continue
      if custom_id in dict1_map:
          # Get the corresponding dictionary in dict1
          dict1_item = dict1_map[custom_id]
          # print(dict1_item)
          # Iterate through the items in dict2 and add missing keys to dict1_item
          for key, value in item.items():
              # print(key)
              if key in dict1_item:
                  # print("if key in dict1_item")
                  # print(key)
                  if str(dict1_item[key]) == 'null':
                    dict1_item[key] = value
              if key != "custom_id" and key not in dict1_item:
                  dict1_item[key] = value
                  # print("if key not it dict1_item")
                  # print(key)
      else:
         continue
  
  # print(dict1_item)
  # # Iterate through each dictionary in dict2
  # for d2 in airData:
  #   # Iterate through the key-value pairs in the current dictionary
  #   for key, value in d2.items():
  #       # Check if the key is not in dict1
  #       if key not in xanoData[n]:
  #           # If the key is not in dict1, add it to dict1 with its value
  #           xanoData[n][key] = value
  #   n+=1
  # create_json('dict1_item', dict1_map)
  # create_json('/merged/'+name+'_merge', dict1_item)


"""
Live function
"""
def merge_data(airData, xanoData, name):
  # dict2_lookup = {item[id]: item for item in airData}
  # Create a dictionary to store airData entries by id for faster lookup
  # "id" in airTable_lookup is determined based on conditions using item.get() to handle different keys ('custom_id', 'studios_id', 'Contact Name')
  airTable_lookup = {item.get('custom_id', item.get('studios_id', item.get('Contact Name'))): item for item in airData}
  # if name == 'recording':
    # Iterate through xanoData and update its entries using airData
  for item in xanoData:
      # assigns 'id' the first non-empty value among 'custom_id', 'studios_id', and 'Contact Name
      id = item.get('custom_id') or item.get('studios_id') or item.get('Contact Name')
      if id in airTable_lookup:
        dict2_item = airTable_lookup[id]
        for key, value in dict2_item.items():
            # if key in item:
              # if item[key] is None or item[key] == [None]:
              #   print(key, ": ", item[key])
            if key in item and type(item[key]) == list:
                if item[key] == [None]:
                  item[key].remove(None)
                  item[key] += value
                elif not any(item[key]):
                   item[key] == None
                elif 0 in item[key] or "0" in item[key]:
                  # item[key].remove(0)
                  item[key] = value
                else:
                  item[key] += value
            if key not in item or item[key] is None or item[key] == [None]:
                item[key] = value
  create_json('/merged/'+name+'_merge', xanoData)
  convert_json_to_csv(name,'merged', '_merge')


def merge_only_missing(airData, xanoData, name):
     # dict2_lookup = {item[id]: item for item in airData}
  # Create a dictionary to store airData entries by id for faster lookup
  # "id" in airTable_lookup is determined based on conditions using item.get() to handle different keys ('custom_id', 'studios_id', 'Contact Name')
  airTable_lookup = {item.get('custom_id', item.get('studios_id', item.get('Contact Name'))): item for item in airData}
  if name == 'recording':
    # Iterate through xanoData and update its entries using airData
    for item in xanoData:
        # assigns 'id' the first non-empty value among 'custom_id', 'studios_id', and 'Contact Name
        id = item.get('custom_id') or item.get('studios_id') or item.get('Contact Name')
        if id in airTable_lookup:
          dict2_item = airTable_lookup[id]
          for key, value in dict2_item.items():
              # if key in item:
                # if item[key] is None or item[key] == [None]:
                #   print(key, ": ", item[key])
              if key in item and (key != 'id' or key != 'custom_id') and item[key] is not [None]:
                 if item[key] == value:
                    del item[key]
              if key in item and type(item[key]) == list:
                 if item[key] == [None]:
                    item[key].remove(None)
                 item[key] += value
              if key not in item or item[key] is None or item[key] == [None]:
                  item[key] = value
    create_json('/merged/'+name+'_merge_missing', xanoData)
    convert_json_to_csv(name+'_merge_missing')


def missing_keys(air, xano, name):
  unique_keys_list = []
  airTable_lookup = {item.get('custom_id', item.get('studios_id', item.get('Contact Name'))): item for item in xano}
  # Create a set of keys from dict1 for efficient lookup
  # dict1_keys = set(item1.keys() for item1 in xano)
  print(airTable_lookup)

  """# Iterate through dict2
  for item2 in air:
    if item2 == "quotes":
      id = item2.get('custom_id') or item2.get('studios_id') or item2.get('Contact Name')
      id_value = item2[id]
      if id_value in airTable_lookup:
          dict1_item = next(item1 for item1 in xano if item1[id] == id_value)
          unique_keys = [key for key in item2.keys() if key not in dict1_item]
          unique_keys_list.append(unique_keys)
      
      with open("data/missing/"+name+"missing.json", "w") as json_file:
        json.dump(unique_keys_list, json_file)
"""

def find_missing_keys(dict1, dict2,name):
    missing_keys = []
    n = 0
    airTable_lookup = {item.get('custom_id', item.get('studios_id', item.get('Contact Name'))): item for item in dict1}
    while n < 1:
      for key in dict1:
        key.get('custom_id', key.get('studios_id', key.get('Contact Name')))
      # for key in dict2:
      #     print(key)
      #     if key not in dict1:
      #         missing_keys.append(key)
      #     else:
      #         print("not in dict1")
          # n+=1
    # with open("data/missing/"+name+"missing.json", "w") as json_file:
    #     json.dump(missing_keys, json_file)

def convert_csv_to_json():
  # Replace 'input.csv' with your CSV file's name or path.
  csv_file = 'data/xano_import_downloads/dbo-profiles-247976-live.1698069582.csv'
  json_file = 'xano_c/profiles_output'

  # Convert CSV to JSON
  data = []

  with open(csv_file, 'r') as csv_file:
      csv_reader = csv.DictReader(csv_file)
      for row in csv_reader:
          data.append(row)

  # Write JSON data to a file
  create_json(json_file, data)
  # with open(json_file, 'w') as json_file:
  #     json_file.write(json.dumps(data, indent=4))

  print(f'Conversion complete. JSON data saved to {json_file}')

def merge_csv():
  import pandas as pd
   # Load the two CSV files
  file1 = 'data/xano_import_downloads/dbo-profiles-247976-live.1697791355.csv'
  file2 = 'data/merged/profiles_merge.csv'

  # Load both CSV files into DataFrames
  df1 = pd.read_csv(file1)
  df2 = pd.read_csv(file2)

  # Merge the two DataFrames based on a common column
  # Replace 'common_column' with the actual name of the column you want to match on.
  merged_data = pd.merge(df1, df2, on='custom_id', how='inner')

  # Save the merged data to a new CSV file
  merged_data.to_csv('data/merged/profiles_merge_id.csv', index=False)
  print("Merged data saved to merged.csv")


def filter_json(input_file, output_file, desiredKeys):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        data = json.load(infile)
        for item in data:
          # Create a list of keys to be removed
          keys_to_remove = [key for key in item.keys() if key not in desiredKeys]
          
          # Remove the keys and their values
          for key in keys_to_remove:
            del item[key]
        json.dump(data, outfile)

    convert_json_to_csv("rehearsal", "merged", "_filtered")

# def remove_key(d):
#     with open(f'data/merged/recording_merge.json', encoding='utf-8') as inputfile:
#       d = pd.read_json(inputfile)
#     if isinstance(d, dict):
#         for k in d.keys():
#            if k == 'id' or k == 'matchedWith' or k == 'interestedIn' or k == 'acceptedQuote' or k == 'recording_enquiries' or k == 'likedBy':
#               continue
#            else:
#               del d[k]
#               for v in d.values():
#                  remove_key(v)
#         if 'badKey' in d:
#             del d['badKey']
#         for v in d.values():
#             remove_key(v)
#     elif isinstance(d, list):
#         for v in d:
#             remove_key(v)

#   data = json.loads(json_string.decode('utf-8'))
#   remove_key(data)


"""
-------------------
call functions
"""
exact_tables = ["rehearsal"]
desiredKeys = ["id", "custom_id", "enquiries", "likedBy"]
# convert_csv_to_json()
# merge_csv()
# compare_tables(exact_tables)
# filter_json("data/merged/rehearsal_merge.json", "data/merged/rehearsal_filtered.json", desiredKeys)
# get_xano(exact_tables)
# compare_key_per(table_name_list_2, xano)
# create_json_per_table(exact_tables)     
convert_json_to_csv("rehearsal", "merged", "_filtered")
# create_json_per_table(table_name_list)