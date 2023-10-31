import requests
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.environ.get('NAVI_WINGS_USERNAME')
KEY = os.environ.get('NAVI_WINGS_KEY')

input_data = {'First Name': 'TEST', 'Last Name': 'TEST2', 'Email': 'George.Lazenby@bondenterprises.co', 'Address Line 1': '38 The Drive', 'Town': 'Westbury', 'County': 'England', 'Postal Code': 'SE51 8AJ', 'Country': 'United Kingdom', 'Phone': '07123456789'}

email = input_data['Email']

get_url = f"https://data.donorfy.com/api/v1/BZWH1AY5D2/constituents/EmailAddress/{email}1"

constituent = requests.get(get_url, headers={"Authorization": "Basic U2hvcGlmeSBDdXN0b21lciBEYXRhOmRfMGlIMSQ/WDJEZWgydDlMP0AkQD90LVI="})

constituent_id = ""

if not constituent.text:
  
    print("doens't exist")

    body = {"EmailAddress": input_data.get('Email', None),
            "FirstName": input_data.get('First Name', None),
            "Last Name": input_data.get('Last Name', None),
            "AddressLine1": input_data.get('Address Line 1', None),
            "AddressLine2": input_data.get('Address Line 2', None),
            "Town": input_data.get('Town', None),
            "Country": input_data.get('Country', None),
            "MobilePhone": input_data.get('Phone', None),
            "ConstituentType": "Individual"}

    print(body)
    post_url = "https://data.donorfy.com/api/v1/BZWH1AY5D2/constituents"
    new_constituent = requests.post(post_url, json = body, headers={"Authorization": "Basic U2hvcGlmeSBDdXN0b21lciBEYXRhOmRfMGlIMSQ/WDJEZWgydDlMP0AkQD90LVI="})
    constituent_id = new_constituent.json()["ConstituentId"]


else:
    print('exists')
    constituent_id = constituent.json()[0]["ConstituentId"]

output = [{'ConstituentID': constituent_id}]

print('output', output)