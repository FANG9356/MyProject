const axios = require('axios');
require('dotenv').config();

const { ADGUARD_URL, ADGUARD_USERNAME, ADGUARD_PASSWORD, TARGET_IP, SERVER_IP } = process.env;

const authHeader = 'Basic ' + Buffer.from(`${ADGUARD_USERNAME}:${ADGUARD_PASSWORD}`).toString('base64');

const getAxiosConfig = () => ({
    headers: { 'Authorization': authHeader, 'Content-Type': 'application/json' }
});

const getBlockRule = () => `||*^$client=${TARGET_IP},dnsrewrite=NOERROR;A;${SERVER_IP}`;

async function blockInternet() {
    if (!ADGUARD_URL) return console.warn('[AdGuard] AdGuard URL not configured.');
    try {
        const res = await axios.get(`${ADGUARD_URL}/control/filtering/status`, getAxiosConfig());
        let rules = res.data.user_rules || [];
        const blockRule = getBlockRule();
        
        // Remove any old/orphaned captive portal rules for this server IP
        const cleanRules = rules.filter(r => !r.includes(`dnsrewrite=NOERROR;A;${SERVER_IP}`));
        
        // Add the current target rule
        cleanRules.push(blockRule);
        
        await axios.post(`${ADGUARD_URL}/control/filtering/set_rules`, { rules: cleanRules }, getAxiosConfig());
        console.log(`[AdGuard] Block rule applied for ${TARGET_IP}`);
    } catch (err) {
        console.error('[AdGuard] Error blocking internet:', err.message);
    }
}

async function unblockInternet() {
    if (!ADGUARD_URL) return console.warn('[AdGuard] AdGuard URL not configured.');
    try {
        const res = await axios.get(`${ADGUARD_URL}/control/filtering/status`, getAxiosConfig());
        let rules = res.data.user_rules || [];
        
        const initialLength = rules.length;
        // Remove ANY rule that redirects to our captive portal
        rules = rules.filter(r => !r.includes(`dnsrewrite=NOERROR;A;${SERVER_IP}`));
        
        if (rules.length !== initialLength) {
            await axios.post(`${ADGUARD_URL}/control/filtering/set_rules`, { rules }, getAxiosConfig());
            console.log(`[AdGuard] Block rules removed for all targets`);
        }
    } catch (err) {
        console.error('[AdGuard] Error unblocking internet:', err.message);
    }
}

module.exports = { blockInternet, unblockInternet };
