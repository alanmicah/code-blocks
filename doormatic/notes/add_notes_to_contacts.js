/////////////////////// IMPORTS ///////////////////////

const axios = require("axios");
require("dotenv").config();
/////////////////////// HUBSPOT DETAILS ///////////////////////

const hubspotAccessToken = process.env.DOORMATIC_HUBSPOT_ACCESS_TOKEN;
const hubspotHeaders = { Authorization: `Bearer ${hubspotAccessToken}` };

/////////////////////// AIRTABLE DETAILS ///////////////////////

const airtableKey = process.env.DOORMATIC_AIRTABLE_KEY;
const baseId = "appga9Mr4rk0qIOy5";
const tableIdOrName = "Opportunities";
const airtableHeaders = { Authorization: `Bearer ${airtableKey}` };

const notesBaseID = "appWegstR7Zgo3Izd";
const notesTableName = "Notes";

/////////////////////// SCRIPT ///////////////////////

let airtablePageOffset = null;

async function migrateNotesToHubspot() {
  for (let i = 0; i < 1; i++) {
    const opportunityRecords = await getOpportunitiesfromAirtable();
    await addNotesToHubspot(opportunityRecords);
    break;
  }
}

async function getOpportunitiesfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?view=Synced%20Opportunities`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });
  airtablePageOffset = response.data.offset;

  return response.data.records;
}

async function addNotesToHubspot(opportunityRecords) {
  let i = 0;
  for (const opportunityRecord of opportunityRecords) {
    console.log(opportunityRecord);
    const noteRecords = await getOpportunityNotes(opportunityRecord);
    console.log(noteRecords);
    // const requestBody = createRequestBody(opportunityRecord);
    // // console.log(requestBody);
    // const hubspotID = await addOpportunityToHubspot(requestBody);
    // await updateAirtableRecord(hubspotID, opportunityRecord.id);
    i++;
    // if (i > 5) {
    //   break;
    // }
  }
}

async function getOpportunityNotes(opportunityRecord) {
  console.log(opportunityRecord.fields.contactID);
  if (opportunityRecord.fields.contactID != null) return null;
  const formula = `{Act Contact ID} = ${opportunityRecord.fields.contactID}`;

  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${notesBaseID}/${notesTableName}?view=Notes%20To%20process&filterByFormula=${encodeURI(
    formula
  )}`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });

  return response.data.records;
}

function createRequestBody(airtableRecord) {
  requestBody = addContactToRequestBody(
    requestBody,
    airtableRecord.fields.contactHubspotID
  );
  return requestBody;
}

function addContactToRequestBody(requestBody, contactID) {
  if (contactID == null) return requestBody;

  requestBody["association"] = [
    {
      to: {
        id: "416461",
      },
      types: [
        {
          associationCategory: "HUBSPOT_DEFINED",
          associationTypeId: 3,
        },
      ],
    },
  ];
  console.log(requestBody.association);
  return requestBody;
}

async function updateDeal(requestBody) {
  try {
    const apiResponse = await axios.post(
      "https://api.hubapi.com/crm/v3/objects/deals",
      requestBody,
      { headers: hubspotHeaders }
    );
    return apiResponse.data.id;
  } catch (e) {
    console.log(e.message);
    e.message === "Request failed with status code 400"
      ? console.error(JSON.stringify(e.response.data, null, 2))
      : console.error("error");
  }
}

async function updateAirtableRecord(hubspotID, airtableID) {
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}/${airtableID}`;
  try {
    response = await axios.patch(
      airtableputRecordUrl,
      {
        fields: {
          contactAdded: true,
        },
      },

      {
        headers: airtableHeaders,
      }
    );

    // console.log(response.data.records);
    console.log(
      response.data.fields["opportunity name"],
      hubspotID == null ? "NA" : hubspotID
    );

    return response.data;
  } catch (error) {
    console.log(error.response.data);
    console.log("Airtable Error");
  }
}

migrateNotesToHubspot();
