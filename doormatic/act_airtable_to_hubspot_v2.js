/////////////////////// IMPORTS ///////////////////////

const hubspot = require("@hubspot/api-client");
const axios = require("axios");
const { log } = require("console");
require("dotenv").config();
/////////////////////// HUBSPOT DETAILS ///////////////////////

const hubspotAccessToken = process.env.DOORMATIC_HUBSPOT_ACCESS_TOKEN;
const hubspotHeaders = { Authorization: `Bearer ${hubspotAccessToken}` };

/////////////////////// AIRTABLE DETAILS ///////////////////////

const airtableKey = process.env.DOORMATIC_AIRTABLE_KEY;
const baseId = "appRTap2n6PrB3JXt";
const tableIdOrName = "Contacts";
const airtableHeaders = { Authorization: `Bearer ${airtableKey}` };

/////////////////////// SCRIPT ///////////////////////

let airtablePageOffset = null;

async function migrateAirtableContactsToHubspot() {
  const airtableRecords = await getContactsfromAirtable();
  const hubspotID = await addContactsToHubspot(airtableRecords);
  // console.log(hubspotIDs);
  updateAirtableRecord(hubspotID);
}

async function getContactsfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?sort%5B0%5D%5Bfield%5D=Create%20Date`;
  console.log(airtablegetRecordsUrl);

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });
  airtablePageOffset = response.data.offset;

  return response.data.records;
}

async function addContactsToHubspot(airtableRecords) {
  for (const airtableRecord of airtableRecords) {
    const requestBody = createRequestBody(airtableRecord);
    const hubspotID = addContactToHubspot(requestBody);
    // updateAirtableRecord(hubspotID);
    break;
  }

  console.log(123);
}

function createRequestBody(airtableRecord) {
  requestBody = {
    properties: createProperties(airtableRecord.fields),
  };

  return requestBody;
}

function createProperties(contactFields) {
  const createdDate = new Date(
    Date.parse(contactFields["Create Date (Parsed)"])
  );
  createdDate.setHours(0, 0, 0, 0);

  let properties = {
    act_contact_id: contactFields["Act ID"],
    address_line_1: contactFields["Address 1"],
    address_line_2: contactFields["Address 2"],
    address_line_3: contactFields["Address 3"],
    airtable_record_id: contactFields["airtable ID"],
    city: contactFields["City"],
    company: contactFields["Company"],
    act_create_date: createdDate,
    domestic: contactFields["Type of Contact"] === "Domestic" ? true : false,
    email: contactFields["E-mail"],
    firstname: contactFields["First Name"],
    jobtitle: contactFields["Title"],
    lastname: contactFields["Surname"],
    mobilephone: contactFields["Mobile Phone"],
    phone: contactFields["Mobile Phone"],
    prefix: contactFields["Name Prefix"],
    record_manager: contactFields["Record Manager"],
    referred_by: contactFields["Referred By"],
    salutation: contactFields["Salutation"],
    zip: contactFields["Postcode"],
  };
  return properties;
}

async function addContactToHubspot(requestBody) {
  try {
    const apiResponse = await axios.post(
      "https://api.hubapi.com/crm/v3/objects/contacts",
      requestBody,
      { headers: hubspotHeaders }
    );
    return apiResponse.data.id;
  } catch (e) {
    e.message === "HTTP request failed"
      ? console.error(JSON.stringify(e.response, null, 2))
      : console.error(e);
  }
}

async function updateAirtableRecord(hubspotID) {
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}`;

  response = await axios.patch(
    airtableputRecordUrl,
    {
      records: [
        {
          fields: {
            "Hubspot ID": hubspotID,
          },
          id: "recDB5vvDLgmpGR25",
        },
        {
          fields: {
            "Hubspot ID": hubspotID,
          },
          id: "rece4ODOKmJYz0SGG",
        },
      ],
    },

    {
      headers: airtableHeaders,
    }
  );

  // console.log(response.data.records);
  for (const record of response.data.records) {
    // console.log(record);
    console.log(
      record.fields["First Name"],
      record.fields["Surname"],
      hubspotID
    );
  }

  return response.data;
}

migrateAirtableContactsToHubspot();
