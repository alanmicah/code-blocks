/////////////////////// IMPORTS ///////////////////////

const axios = require("axios");
require("dotenv").config();

/////////////////////// HUBSPOT DETAILS ///////////////////////

const hubspotAccessToken = process.env.DOORMATIC_HUBSPOT_ACCESS_TOKEN;
const hubspotHeaders = {
  Authorization: `Bearer ${hubspotAccessToken}`,
  "Content-Type": "application/json",
};

/////////////////////// AIRTABLE DETAILS ///////////////////////

const airtableKey = process.env.DOORMATIC_AIRTABLE_KEY;
const baseId = "appga9Mr4rk0qIOy5";
const contactsBaseID = "appRTap2n6PrB3JXt";
const tableIdOrName = "Opportunities";
const contactsTableName = "Contacts";
const airtableHeaders = { Authorization: `Bearer ${airtableKey}` };

/////////////////////// SCRIPT ///////////////////////

async function addAllContactsInfoDeal() {
  for (let i = 0; i < 30; i++) {
    const opportunityRecords = await getOpportunitiesfromAirtable();
    for (const opportunityRecord of opportunityRecords) {
      await addContactInfoToDeal(opportunityRecord);

      // break;
    }
    // break;
  }
}

async function getOpportunitiesfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?view=Opportunities%20To%20Upload`;
  try {
    response = await axios.get(airtablegetRecordsUrl, {
      headers: airtableHeaders,
    });
  } catch (error) {
    console.log(error);
  }

  return response.data.records;
}

async function addContactInfoToDeal(opportunityRecord) {
  const contactID = getContactActID(opportunityRecord);
  const actContact = await getActContact(contactID);
  // console.log(actContact);

  const requestbody = createRequestBody(actContact, opportunityRecord);
  await updateDeal(opportunityRecord.fields.hubspotID, requestbody);
  await updateAirtableRecord(opportunityRecord.id);
  // return true;
}

function getContactActID(opportunityRecord) {
  return opportunityRecord.fields.contactID;
}

async function getActContact(contactID) {
  const formula = `{Act ID} = "${contactID}"`;

  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${contactsBaseID}/${contactsTableName}?filterByFormula=${encodeURI(
    formula
  )}`;

  try {
    response = await axios.get(airtablegetRecordsUrl, {
      headers: airtableHeaders,
    });

    return response.data.records[0];
  } catch (error) {
    console.log(error);
  }
}

function createRequestBody(contactRecord, opportunityRecord) {
  // console.log(contactRecord);
  // console.log(opportunityRecord);
  if (contactRecord == null) return;

  const contactFields = contactRecord.fields;
  const doorType = getDoorType(contactFields["Door Make"]);
  const supplyAndFit = getSupplyAndFit(contactFields["Supply"]);
  const motorManufacturer = getMotorManufacturer(
    contactFields["Motor Manufacturer"]
  );
  const requestBody = {
    properties: {
      order_number: opportunityRecord.fields.orderNumber,
      supply_and_fit: supplyAndFit,
      door_type: doorType,
      motor_manufacturer: motorManufacturer,
    },
  };
  return requestBody;
}

function getDoorType(doorType) {
  if (doorType == null) return null;
  doorTypes = {
    canopy: "Canopy",
    retractable: "Retractable",
    sectional: "Sectional",
    roller: "Roller",
    "side sliding": "Side sliding",
    "side hinged": "Side Hinged",
  };

  return doorTypes[doorType.toLowerCase()];
}

function getSupplyAndFit(supplyAndFit) {
  if (supplyAndFit == null) return null;

  fields = {
    "supply & fit": "Supply and fit",
    "supply only": "Supply only",
  };
  return fields[supplyAndFit.toLowerCase().trim()];
}

function getMotorManufacturer(motorManufacturer) {
  if (motorManufacturer == null) return null;

  fields = {
    "novoferm 423": "Novoferm 423",
    "novoferm 563": "Novoferm 563",
    "doormatic novoferm 563": "Novoferm 563",
    "carteck drive 500nm": "Carteck Drive 500Nm",
    "carteck drive 600nm": "Carteck Drive 600Nm",
    "hormann promatic": "Hormann Promatic",
    "hormann supramatic": "Hormann Supramatic",
    garamatic: "Garamatic",
    liftmaster: "Liftmaster",
    marantec: "Marantec",
    somfy: "Somfy",
    manual: "Manual",
    "use customers": "Use Customers",
  };

  return fields[motorManufacturer.toLowerCase().trim()];
}

async function updateDeal(hubspotID, requestBody) {
  console.log(requestBody);
  try {
    const apiResponse = await axios.patch(
      `https://api.hubapi.com/crm/v3/objects/deals/${hubspotID}`,
      requestBody,
      { headers: hubspotHeaders }
    );
    return apiResponse.data.id;
  } catch (e) {
    console.log(e.message);
    console.error(e.response.data);
  }
}

async function updateAirtableRecord(airtableID) {
  const airtableputRecordUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}/${airtableID}`;
  try {
    response = await axios.patch(
      airtableputRecordUrl,
      {
        fields: {
          contactInfoAdded: true,
        },
      },

      {
        headers: airtableHeaders,
      }
    );
    // console.log(response.data.records);
    console.log(
      response.data.fields["opportunity name"],
      response.data.fields.contactInfoAdded
    );

    return response.data;
  } catch (error) {
    console.log(error.response.data);
    console.log("Airtable Error");
  }
}

addAllContactsInfoDeal();
