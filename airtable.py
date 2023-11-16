import json
import requests
import time
import datetime

api_token = ''
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}
endpoint_root = 'https://api.airtable.com/v0'
rate_limit = {
    'number': 5,  # Number of calls per unit time
    'time_value': 1,  # The quantity of time in seconds
    'wait_time': 30  # How long to wait if 429 triggered (seconds)
}


def find_or_create(base_id, table_id, view_name, list_of_formula_dicts, fields):
    formula = formula_constructor(list_of_formula_dicts)
    response = search_for_record(base_id, table_id, view_name, formula, 1)
    try:
        first_result = response.get('records')[0]
    except IndexError:
        print(f'Error parsing Airtable search response:\n{response}')

    try:
        return first_result.get('id')
    except:
        result = create_record(base_id, table_id, fields)
    return result.get('id')


def search_and_upsert(base_id, table_id, view_name, list_of_formula_dicts, fields):
    formula = formula_constructor(list_of_formula_dicts)
    first_result = search_for_record(base_id, table_id, view_name, formula, 1).get('records')[0]
    try:
        record_id = first_result.get('id')
    except:
        record_id = None

    return upsert_record(base_id, table_id, record_id, fields)


def formula_constructor(list_of_formula_dicts):
    """
  Create a formula for searching Airtable records.
  Structure of data
  { 'field':'field name', 'field_type':'string, number, bool', 'operator':'symbol (=, >, <)', 'value':'value to search for' }
  { 'logic': 'AND, OR', 'conditions':[] }
  """
    formula_str = ''
    for formula_dict in list_of_formula_dicts:
        # if formula_str != '':
        # 	formula_str = f'{formula_str}'
        if formula_dict.get('logic'):
            # This has a list of conditions to nest into a logical aggregator AND or OR
            nested_conditions_str = formula_constructor(formula_dict.get('conditions'))
            new_condition_str = f'{formula_dict.get("logic")}({nested_conditions_str})'
        else:
            if formula_dict.get("field_type") == 'string':
                value_str = f'"{formula_dict.get("value")}"'
            else:
                value_str = f'{formula_dict.get("value")}'

            new_condition_str = '{' \
                                + formula_dict.get('field') \
                                + '}' \
                                + f'{formula_dict.get("operator")}' \
                                + value_str

        if formula_str != '':
            formula_str = f'{formula_str},{new_condition_str}'
        else:
            formula_str = f'{new_condition_str}'

    return formula_str


def upsert_record(base_id, table_id, record_id, fields):
    if record_id:
        return update_record(base_id, table_id, record_id, fields)
    else:
        return create_record(base_id, table_id, fields)


def update_record(base_id, table_id, record_id, fields):
    """Create a new record"""
    # Set up request objects
    endpoint = f'{endpoint_root}/{base_id}/{table_id}/{record_id}'
    data = {"fields": fields}
    data = json.dumps(data)

    # Make the request
    response = requests.patch(
        url=endpoint,
        data=data,
        headers=headers
    ).json()

    return response


def create_record(base_id, table_id, fields):
    """Create a new record"""
    # Set up request objects
    endpoint = f'{endpoint_root}/{base_id}/{table_id}'
    data = {"fields": fields}
    data = json.dumps(data)

    # Make the request
    response = requests.post(
        url=endpoint,
        data=data,
        headers=headers
    ).json()

    return response


def create_multiple_records(base_id, table_id, records):
    """Create multiple new records, pass records as array of collections."""
    # Set up request objects
    endpoint = f'{endpoint_root}/{base_id}/{table_id}'
    data = {"records": records}
    data = json.dumps(data)

    # Make the request
    response = requests.post(
        url=endpoint,
        data=data,
        headers=headers
    ).json()

    return response


def get_record(base_id, table_id, record_id):
    """If record_id is omitted a new record is created"""
    # Set up request objects
    endpoint = f'{endpoint_root}/{base_id}/{table_id}/{record_id}'

    # Make the request
    response = requests.get(
        url=endpoint,
        headers=headers
    ).json()

    return response


def search_for_record(base_id, table_id, view_name, formula, max_results):
    """Search the specified table using the formula.  Formula is a string.  view_name is optional (pass None to ignore)"""
    # Set up request objects
    endpoint = f'{endpoint_root}/{base_id}/{table_id}/listRecords'

    # url_parameters = {}
    # if view_name:
    # 	url_parameters['view'] = view_name
    payload = {
        "filterByFormula": formula,
        "maxRecords": max_results
        # "view": view_name
    }
    payload = json.dumps(payload)

    # Make the request
    response = requests.post(
        url=endpoint,
        headers=headers,
        # params=url_parameters,
        data=payload
    ).json()

    return response
