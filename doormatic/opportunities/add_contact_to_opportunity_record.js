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
  const hubspotID = await getContactHubspotID(contactID);

  updateOpportunity(opportunityRecord.id, hubspotID);
  return true;
}

function getContactActID(opportunityRecord) {
  return opportunityRecord.fields.contactID;
}

async function getContactHubspotID(contactID) {
  const formula = `{Act ID} = "${contactID}"`;
  const airtablegetRecordsUrl = `https://api.airtable.com/v0/${contactsBaseID}/${contactsTableName}?filterByFormula=${encodeURI(
    formula
  )}`;

  try {
    response = await axios.get(airtablegetRecordsUrl, {
      headers: airtableHeaders,
    });

    const noContactExists = response.data.records[0] == null;
    if (noContactExists) {
      console.log("no contact");
      return null;
    }

    const contact = response.data.records[0];
    let hubspotID = contact.fields["Hubspot ID"];
    console.log("hubspotID", hubspotID);
    const contactHasNoHubspotID = contact.fields["Hubspot ID"] == undefined; //contactHasNoHubspotID

    if (contactHasNoHubspotID) {
      console.log(
        "original contact ID",
        contact.fields["Original Contact Act ID"]
      );
      hubspotID = await getContactHubspotID(
        contact.fields["Original Contact Act ID"]
      );
      console.log(hubspotID);
    }

    return hubspotID;
  } catch (error) {
    console.log(error);
  }
}

async function updateOpportunity(opportunityRecordID, hubspotID) {
  const airtableRecordUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}/${opportunityRecordID}`;

  hubspotID = hubspotID == null ? "No contact 1" : hubspotID;

  const requestBody = {
    fields: {
      contactHubspotID: hubspotID,
    },
  };

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
