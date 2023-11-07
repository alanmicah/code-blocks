/////////////////////// IMPORTS ///////////////////////

const hubspot = require("@hubspot/api-client");
const axios = require("axios");
const { log } = require("console");
require("dotenv").config();
/////////////////////// HUBSPOT DETAILS ///////////////////////

const hubspotAccessToken = process.env.DOORMATIC_HUBSPOT_ACCESS_TOKEN;

/////////////////////// AIRTABLE DETAILS ///////////////////////

const airtableKey = process.env.DOORMATIC_AIRTABLE_KEY;
const baseId = "appRTap2n6PrB3JXt";
const tableIdOrName = "Contacts";
const airtablegetRecordsUrl = `https://api.airtable.com/v0/${baseId}/${tableIdOrName}/recZ8yZm1QMK1s6Ww`;
const airtableHeaders = { Authorization: `Bearer ${airtableKey}` };

/////////////////////// SCRIPT ///////////////////////

async function migrateAirtableContactsToHubspot() {
  const response = await connectToAirtable();
  console.log(response);
}

async function connectToAirtable() {
  response = await axios.get(airtablegetRecordsUrl, {
    headers: airtableHeaders,
  });

  console.log(response.data);
  return response.data;
}

function connectToHubspot() {
  const hubspotClient = new hubspot.Client({
    accessToken: process.env.DOORMATIC_HUBSPOT_ACCESS_TOKEN,
  });
}

function createRequestBody() {
  const properties = {
    email: "bcooper@biglytics.net",
    lastname: "Cooper",
    firstname: "Bryan",
    company: "company",
    phone: "(877) 929-0687",
    company: "Biglytics",
    website: "biglytics.net",
  };
}

// Last Activity Date

async function createContactInHubspot() {
  const SimplePublicObjectInputForCreate = { associations: [], properties };

  try {
    const apiResponse = await hubspotClient.crm.contacts.basicApi.create(
      SimplePublicObjectInputForCreate
    );
    console.log(JSON.stringify(apiResponse, null, 2));
  } catch (e) {
    e.message === "HTTP request failed"
      ? console.error(JSON.stringify(e.response, null, 2))
      : console.error(e);
  }
}
