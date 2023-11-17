/////////////////////// IMPORTS ///////////////////////

const axios = require("axios");
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
  for (let i = 0; i < 1000; i++) {
    const airtableRecords = await getContactsfromAirtable();
    await addContactsToHubspot(airtableRecords);
  }
}

async function getContactsfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?view=Contacts%20To%20Upload`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });
  airtablePageOffset = response.data.offset;

  return response.data.records;
}

async function addContactsToHubspot(airtableRecords) {
  for (const airtableRecord of airtableRecords) {
    const requestBody = createRequestBody(airtableRecord);
    // console.log(requestBody);

    // await hubspotUsers();
    const hubspotID = await addContactToHubspot(requestBody);

    await updateAirtableRecord(hubspotID, airtableRecord.id);
  }
}

function createRequestBody(airtableRecord) {
  requestBody = {
    properties: createProperties(airtableRecord.fields),
  };

  return requestBody;
}

function createProperties(contactFields) {
  const createdDate = setDateToMidnight(contactFields["Create Date (Parsed)"]);

  const ownerID = getRecordManagerHubspotID(contactFields["Record Manager"]);
  let properties = {
    hubspot_owner_id: ownerID,
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
      fullName: "Doormatic Bot",
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

async function addContactToHubspot(requestBody) {
  try {
    const apiResponse = await axios.post(
      "https://api.hubapi.com/crm/v3/objects/contacts",
      requestBody,
      { headers: hubspotHeaders }
    );
    return apiResponse.data.id;
  } catch (e) {
    e.message === "Request failed with status code 409"
      ? console.error(JSON.stringify(e.response.data, null, 2))
      : console.error("error");
  }
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
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}/${airtableID}`;
  try {
    response = await axios.patch(
      airtableputRecordUrl,
      {
        fields: {
          "Hubspot ID": hubspotID == null ? "NA" : hubspotID,
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
      hubspotID == null ? "NA" : hubspotID
    );

    return response.data;
  } catch (error) {
    console.log("Airtable Error");
  }
}

migrateAirtableContactsToHubspot();
