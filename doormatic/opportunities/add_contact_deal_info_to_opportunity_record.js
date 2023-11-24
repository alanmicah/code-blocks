/////////////////////// IMPORTS ///////////////////////

const axios = require("axios");
require("dotenv").config();

/////////////////////// AIRTABLE DETAILS ///////////////////////

const airtableKey = process.env.DOORMATIC_AIRTABLE_KEY;
const baseId = "appga9Mr4rk0qIOy5";
const contactsBaseID = "appRTap2n6PrB3JXt";
const tableIdOrName = "Opportunities";
const contactsTableName = "Contacts";
const airtableHeaders = { Authorization: `Bearer ${airtableKey}` };

/////////////////////// SCRIPT ///////////////////////

async function addContactsToOpportunities() {
  for (let i = 0; i < 50; i++) {
    const opportunityRecords = await getOpportunitiesfromAirtable();
    for (const opportunityRecord of opportunityRecords) {
      await addContactToOpportunity(opportunityRecord);
      // break;
    }
  }
}

async function getOpportunitiesfromAirtable() {
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}?view=Contactless%20Opportunities`;
  try {
    response = await axios.get(airtablegetRecordsUrl, {
      headers: airtableHeaders,
    });
  } catch (error) {
    console.log(error);
  }

  return response.data.records;
}

async function addContactToOpportunity(opportunityRecord) {
  const contactID = getContactActID(opportunityRecord);
  const actContact = await getActContact(contactID);

  updateDeal(opportunityRecord.fields.hubspotID, actContact);
  return true;
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

async function updateDeal(hubspotID, actContact, opportunityID) {
  if (actContact == null) return;
  hubspotID = hubspotID == null ? "No contact" : hubspotID;

  try {
    const apiResponse = await axios.patch(airtableRecordUrl, requestBody, {
      headers: airtableHeaders,
    });

    console.log();
    console.log(
      apiResponse.data.fields["opportunity name"],
      apiResponse.data.fields.contactHubspotID
    );
    console.log();
  } catch (error) {
    console.log(error);
  }
}

async function updateOpportunity(hubspotID, actContact, opportunityID) {
  if (actContact == null) return;
  hubspotID = hubspotID == null ? "No contact" : hubspotID;

  try {
    const apiResponse = await axios.patch(airtableRecordUrl, requestBody, {
      headers: airtableHeaders,
    });

    console.log();
    console.log(
      apiResponse.data.fields["opportunity name"],
      apiResponse.data.fields.contactHubspotID
    );
    console.log();
  } catch (error) {
    console.log(error);
  }
}

addContactsToOpportunities();
