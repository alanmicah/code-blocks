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

/////////////////////// SCRIPT ///////////////////////

let airtablePageOffset = null;

async function migrateAirtableOpportunitiesToHubspot() {
  for (let i = 0; i < 1; i++) {
    const airtableRecords = await getOpportunitiesfromAirtable();
    await addOpportunitiesToHubspot(airtableRecords);
  }
}

async function getOpportunitiesfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?view=Opportunities%20To%20Upload`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });
  airtablePageOffset = response.data.offset;

  return response.data.records;
}

async function addOpportunitiesToHubspot(airtableRecords) {
  for (const airtableRecord of airtableRecords) {
    const requestBody = createRequestBody(airtableRecord);
    // console.log(requestBody);
    const hubspotID = await addOpportunityToHubspot(requestBody);
    await updateAirtableRecord(hubspotID, airtableRecord.id);

    break;
  }
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

migrateAirtableOpportunitiesToHubspot();
