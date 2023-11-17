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
  for (let i = 0; i < 10; i++) {
    const opportunityRecords = await getOpportunitiesfromAirtable();
    for (const opportunityRecord of opportunityRecords) {
      await addContactToOpportunity(opportunityRecord);
      // if (i > 5) {
      //   break;
      // }
      // i++;
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
  const hubspotID = await getContactHubspotID(opportunityRecord);
  //   if (hubspotID == null) return null;

  updateOpportunity(opportunityRecord.id, hubspotID);
  return true;
}

async function getContactHubspotID(opportunityRecord) {
  const contactID = opportunityRecord.fields.contactID;

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
      return null;
    }

    return response.data.records[0].fields["Hubspot ID"];
  } catch (error) {
    console.log(error);
  }
}

async function updateOpportunity(opportunityRecordID, hubspotID) {
  const airtableRecordUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}/${opportunityRecordID}`;

  hubspotID = hubspotID == null ? "No contact" : hubspotID;

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
