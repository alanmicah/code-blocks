import os
from dotenv import load_dotenv
import pandas as pd
from airtable import airtable


load_dotenv()
airtable_key = os.environ.get('DOORMATIC_AIRTABLE_KEY')
at = airtable.Airtable('appga9Mr4rk0qIOy5', airtable_key)

print(at.get("Contacts Table"))

contacts_df = pd.read_csv('assets/contacts-2023.csv')

# print(contacts_d0f)
# 31 October 2018

