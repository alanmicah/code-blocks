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
  for (let i = 0; i < 55; i++) {
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
  let i = 0;

  for (const airtableRecord of airtableRecords) {
    const requestBody = createRequestBody(airtableRecord);
    // console.log(requestBody);
    const hubspotID = await addOpportunityToHubspot(requestBody);

    const asssociationRequestBody = createAssociationRequestBody(
      hubspotID,
      airtableRecord.fields.contactHubspotID
    );

    // await sleep(2000);

    console.log(asssociationRequestBody);
    await associateContactToDeal(asssociationRequestBody);

    await updateAirtableRecord(hubspotID, airtableRecord.id);

    // i++;
    // if (i > 5) {
    // break;
    // }
  }
}

function createRequestBody(airtableRecord) {
  requestBody = {
    properties: createProperties(airtableRecord.fields),
  };

  return requestBody;
}

function createProperties(opportunityFields) {
  const estimatedCloseDate = setDateToMidnight(
    opportunityFields.estimatedCloseDate
  );
  const openDate = setDateToMidnight(opportunityFields.openDate);
  const stageStartDate = setDateToMidnight(opportunityFields.stageStartDate);
  const created = setDateToMidnight(opportunityFields.created);
  const edited = setDateToMidnight(opportunityFields.edited);
  const ownerID = getRecordManagerHubspotID(opportunityFields["manager"]);

  const probability = opportunityFields.probability / 100;
  const stageID = getStageID(opportunityFields.statusUpdated);

  const orderNumber = opportunityFields.orderNumber;

  const dealName = `${
    orderNumber != null ? orderNumber : "Act Opportunity"
  } | ${opportunityFields.contactNames}`;

  let properties = {
    act_id: opportunityFields.actID,
    dealname: dealName,
    pipeline: "213932003",
    act_record_manager: opportunityFields.manager,
    act_days_open: opportunityFields.daysOpen,
    act_days_in_stage: opportunityFields.daysInStage,
    act_estimated_closed_date: estimatedCloseDate,
    act_stage_start_date: stageStartDate,
    act_gross_margin: opportunityFields.grossMargin,
    act_open_date: openDate,
    hs_deal_stage_probability: probability,
    amount: opportunityFields.productTotal,
    act_deal_stage_name: opportunityFields.stageName,
    act_process_name: opportunityFields.processName,
    act_create_date: created,
    act_last_edited: edited,
    hubspot_owner_id: ownerID,
    dealstage: stageID,
  };

  return properties;
}

function setDateToMidnight(date) {
  if (date == null) return null;
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

function getStageID(stageName) {
  console.log();
  const stageNameIDs = {
    "New Lead": "372336847",
    "Initial meeting": "372483321",
    "Ballpark quote": "372483514",
    "Survey booked": "372483515",
    "Survey completed": "372483516",
    "Quote sent": "372371939",
    "Closed won": "372483517",
    "Closed lost": "372483518",
  };

  return stageNameIDs[stageName];
}

// function addContactToRequestBody(requestBody, contactID) {
//   if (contactID == null) return requestBody;

//   requestBody["association"] = [
//     {
//       to: {
//         id: "416461",
//       },
//       types: [
//         {
//           associationCategory: "HUBSPOT_DEFINED",
//           associationTypeId: 3,
//         },
//       ],
//     },
//   ];
//   console.log(requestBody.association);
//   return requestBody;
// }

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

function createAssociationRequestBody(hubspotID, contactID) {
  const requestBody = {
    fromObjectId: hubspotID,
    toObjectId: contactID,
    category: "HUBSPOT_DEFINED",
    definitionId: 3,
  };

  return requestBody;
}

async function associateContactToDeal(requestBody) {
  try {
    const apiResponse = await axios.put(
      "https://api.hubapi.com/crm-associations/v1/associations",
      requestBody,
      { headers: hubspotHeaders }
    );
    return apiResponse.data.id;
  } catch (e) {
    console.log(e.message);
    e.message === "Request failed with status code 400"
      ? console.error(JSON.stringify(e.response.data, null, 2))
      : console.error(e);
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

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

migrateAirtableOpportunitiesToHubspot();
