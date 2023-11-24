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
  for (let i = 0; i < 10; i++) {
    const airtableRecords = await getContactsfromAirtable();
    await addContactsToHubspot(airtableRecords);
  }
}

async function getContactsfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}?view=Contacts%20To%20Upload`;

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
    const response = await addContactToHubspot(requestBody);

    await updateAirtableRecord(response, airtableRecord.id);
    // break;
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
    return apiResponse;
  } catch (e) {
    e.message === "Request failed with status code 409"
      ? console.error(JSON.stringify(e.response.data, null, 2))
      : console.error("Hubspot error"); // e.response.data

    return e.response;
  }
}

async function updateAirtableRecord(response, airtableID) {
  // console.log(response);
  if (response.status === 409 && response.data.category === "CONFLICT") {
    const message = response.data.message;
    const words = message.split(" ");
    const hubspotID = words[words.length - 1];

    const originalContact = await getOriginalHubspotContactInAirtable(
      hubspotID
    );

    if (originalContact == null) {
      console.log("Contact does not exist in Airtable");
      addHubspotIDToContact(hubspotID, airtableID);
    } else {
      console.log("DOES EXIST");
      await addOriginalContactActIDtoRecord(originalContact, airtableID);
    }

    return;
  }
  if (response.status === 400) {
    addErrorCodeToContact(response.status, airtableID);
    return;
  }
  if (response.data != null) {
    const hubspotID = response.data.id;
    addHubspotIDToContact(hubspotID, airtableID);
  }
}

async function getOriginalHubspotContactInAirtable(hubspotID) {
  // const hubspotID = "234801";
  const formula = `{Hubspot ID} = "${hubspotID}"`;
  airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}?view=Admin%20View&filterByFormula=${encodeURI(
    formula
  )}`;

  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });

  return response.data.records[0];
}

async function addHubspotIDToContact(hubspotID, airtableID) {
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}/${airtableID}`;
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
      hubspotID == null ? "Duplicate" : hubspotID
    );

    return response.data;
  } catch (error) {
    console.log("Airtable Error");
  }
}

async function addErrorCodeToContact(errorCode, airtableID) {
  console.log(errorCode);
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}/${airtableID}`;
  try {
    response = await axios.patch(
      airtableputRecordUrl,
      {
        fields: {
          "Error Code": errorCode.toString(),
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
      response.data.fields["Error Code"]
    );

    return response.data;
  } catch (error) {
    console.log("Airtable Error");
    console.log(error.response.data);
  }
}

async function addOriginalContactActIDtoRecord(airtableRecord, airtableID) {
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${contactsTableName}/${airtableID}`;
  try {
    response = await axios.patch(
      airtableputRecordUrl,
      {
        fields: {
          "Original Contact Act ID": airtableRecord.fields["Act ID"],
        },
      },

      {
        headers: airtableHeaders,
      }
    );

    console.log(response.status);
  } catch (error) {
    console.log(error);
  }
}

migrateAirtableContactsToHubspot();
