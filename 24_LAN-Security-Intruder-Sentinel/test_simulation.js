const assert = require('assert');
const { trustedMacs, checkInternet } = require('./server');

async function runTests() {
  assert(Array.isArray(trustedMacs), 'trustedMacs must be an array');
  assert(trustedMacs.length > 0, 'trustedMacs must contain known devices');

  const knownMac = '20:8:89:4f:33:64';
  const unknownMac = 'aa:bb:cc:dd:ee:ff';

  const isKnownTrusted = trustedMacs.some(t => knownMac.includes(t) || t.includes(knownMac));
  const isUnknownTrusted = trustedMacs.some(t => unknownMac.includes(t) || t.includes(unknownMac));

  assert.strictEqual(isKnownTrusted, true, 'Known MAC should be trusted');
  assert.strictEqual(isUnknownTrusted, false, 'Unknown MAC should be flagged as untrusted');

  const netStatus = await checkInternet();
  assert(typeof netStatus === 'object', 'checkInternet must return object');
  assert('status' in netStatus, 'checkInternet must have status property');

  console.log('Project 24 LAN Security Intruder Sentinel tests passed');
  process.exit(0);
}

runTests().catch(err => {
  console.error(err);
  process.exit(1);
});
