/////////////////////// IMPORTS ///////////////////////

const axios = require("axios");
require("dotenv").config();

/////////////////////// HUBSPOT DETAILS ///////////////////////

const hubspotAccessToken = process.env.DOORMATIC_HUBSPOT_ACCESS_TOKEN;
const hubspotHeaders = { Authorization: `Bearer ${hubspotAccessToken}` };

/////////////////////// AIRTABLE DETAILS ///////////////////////

const airtableKey = process.env.DOORMATIC_AIRTABLE_KEY;
const baseId = "appRTap2n6PrB3JXt";
const contactsTableName = "Contacts";
const airtableHeaders = { Authorization: `Bearer ${airtableKey}` };

/////////////////////// SCRIPT ///////////////////////

let airtablePageOffset = null;

async function migrateAirtableContactsToHubspot() {
  for (let i = 0; i < 52; i++) {
    const airtableRecords = await getContactsfromAirtable();
    await addOriginalContactsToDuplicateRecord(airtableRecords);
  }
}

async function getContactsfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}?view=Duplicates`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });
  airtablePageOffset = response.data.offset;

  return response.data.records;
}

async function addOriginalContactsToDuplicateRecord(airtableRecords) {
  for (const airtableRecord of airtableRecords) {
    addOriginContactToRecord(airtableRecord);
  }
}

async function addOriginContactToRecord(airtableRecord) {
  // const hubspotID = "234801";
  const formula = `and({E-mail} = ${airtableRecord}, {Hubspot ID} != "Duplicate")`;
  airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}?view=Admin%20View&filterByFormula=${encodeURI(
    formula
  )}`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });

  return response.data.records[0];
}

// async function hubspotUsers() {
//   try {
//     const apiResponse = await axios.get(
//       "https://api.hubapi.com/crm/v3/owners/?limit=100&archived=false",
//       { headers: hubspotHeaders }
//     );

//     console.log(apiResponse.data);
//     return apiResponse.data;

//   } catch (e) {
//     e.message === "HTTP request failed"
//       ? console.error(JSON.stringify(e.response.data, null, 2))
//       : console.error(e.response.data);

//     console.log("Hubspot error");
//   }
// }

async function updateAirtableRecord(hubspotID, airtableID) {
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}/${airtableID}`;
  try {
    response = await axios.patch(
      airtableputRecordUrl,
      {
        fields: {
          "Hubspot ID": hubspotID == null ? "Duplicate" : hubspotID,
        },
      },

      {
        headers: airtableHeaders,
      }
    );

    // console.log(response.data.records);
    console.log(
      response.data.fields["First Name"],
      response.data.fields["Surname"],
      hubspotID == null ? "Duplicate" : hubspotID
    );

    return response.data;
  } catch (error) {
    console.log("Airtable Error");
  }
}

migrateAirtableContactsToHubspot();
