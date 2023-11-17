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
  const records = await getContactsfromAirtable();
  const requestBodies = createRequestBodies(records);
  const hubspotIDs = await performMultipleBatchContactsCreationInHubspot(
    requestBodies
  );
  console.log(hubspotIDs);
  // updateAirtableRecord("123124124adf");
}

async function getContactsfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?sort%5B0%5D%5Bfield%5D=Create%20Date`;
  console.log(airtablegetRecordsUrl);

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });
  airtablePageOffset = response.data.offset;

  return response.data.records;

  // for (record of response.data.records) {
  //   console.log(record.fields["Create Date"]);
  // }
}

function createRequestBodies(airtableRecords) {
  let recordBundle = [];
  let requestBodies = [];

  for (let i = 0; i < airtableRecords.length; i++) {
    airtableRecord = airtableRecords[i];
    recordBundle.push(airtableRecord);

    if (recordBundle.length == 10 || i == airtableRecords.length - 1) {
      const requestBody = createRequestBody(recordBundle);
      requestBodies.push(requestBody);
      recordBundle = [];
    }
  }

  console.log(requestBodies);
  return requestBodies;
}

function createRequestBody(airtableRecords) {
  requestBody = {
    inputs: airtableRecords.map((airtableRecord) => {
      return {
        properties: createProperties(airtableRecord.fields),
        associations: [],
      };
    }),
  };

  console.log(requestBody.inputs[0]);
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

function performMultipleBatchContactsCreationInHubspot(requestBodies) {
  for (const requestBody of requestBodies) {
    console.log(requestBody);
    batchCreateContactsInHubspot(requestBody);
    break;
  }
}

async function batchCreateContactsInHubspot(requestBody) {
  try {
    const apiResponse = await axios.post(
      "https://api.hubapi.com/crm/v3/objects/contacts/batch/create",
      requestBody,
      { headers: hubspotHeaders }
    );

    return apiResponse;
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
