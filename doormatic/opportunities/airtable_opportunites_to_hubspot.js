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
  requestBody = {
    properties: createProperties(airtableRecord.fields),
  };

  return requestBody;
}

function createProperties(contactFields) {
  const estimatedCloseDate = setDateToMidnight(
    contactFields.estimatedCloseDate
  );
  const openDate = setDateToMidnight(contactFields.openDate);
  const stageStartDate = setDateToMidnight(contactFields.stageStartDate);
  const created = setDateToMidnight(contactFields.created);
  const edited = setDateToMidnight(contactFields.edited);
  const ownerID = getRecordManagerHubspotID(contactFields["manager"]);

  const probability = contactFields.probability / 100;

  let properties = {
    act_id: contactFields.actID,
    dealname: "ORDER NUMBER | Client Name - POSTCODE",
    act_record_manager: contactFields.manager,
    act_days_open: contactFields.daysOpen,
    act_days_in_stage: contactFields.daysInStage,
    act_estimated_closed_date: estimatedCloseDate,
    act_stage_start_date: stageStartDate,
    act_gross_margin: contactFields.grossMargin,
    act_open_date: openDate,
    hs_deal_stage_probability: probability,
    amount: contactFields.productTotal,
    act_deal_stage_name: contactFields.stageName,
    act_process_name: contactFields.processName,
    act_create_date: created,
    act_last_edited: edited,
    hubspot_owner_id: ownerID,
  };

  console.log(properties);
  return properties;
}

function setDateToMidnight(date) {
  const createdDate = new Date(Date.parse(date.split("T")[0]));

  return createdDate;
  // createdDate.setHours(0, 0, 0, 0);
}

function getRecordManagerHubspotID(managerName) {
  const users = [
    {
      userId: 1361913057,
      fullName: "Edward Wallace",
    },
    {
      userId: 1424333045,
      fullName: "Mr Marc Sebo",
    },
    {
      userId: 1471807445,
      fullName: "Emma Ablewhite",
    },
    {
      userId: 1475309010,
      fullName: "Bot",
    },
    {
      userId: 1486492370,
      fullName: "Ollie Bishop",
    },
    {
      userId: 1486492616,
      fullName: "Joe Oakley",
    },
    {
      userId: 1486492867,
      fullName: "Steve Dearnaley",
    },
    {
      userId: 1486506218,
      fullName: "Chris Power",
    },
    {
      userId: 1486506976,
      fullName: "Justine Wyatt",
    },
    {
      userId: 1486506989,
      fullName: "James Gourlay",
    },
    {
      userId: 1486506997,
      fullName: "Chris Smith",
    },
    {
      userId: 1486507239,
      fullName: "Paul Hollylee",
    },
  ];

  let contactOwner = users.filter((user) => user.fullName == managerName)[0];
  let contactOwnerID = contactOwner == null ? 1475309010 : contactOwner.userId;

  return contactOwnerID;
}

async function addOpportunityToHubspot(requestBody) {
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
          hubspotID: hubspotID == null ? "NA" : hubspotID,
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
