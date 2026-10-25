const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTest() {
  const rootDir = __dirname;
  const htmlFile = path.join(rootDir, 'index.html');
  const dataFile = path.join(rootDir, 'data.json');

  assert(fs.existsSync(htmlFile), 'index.html must exist');
  assert(fs.existsSync(dataFile), 'data.json must exist');

  const content = fs.readFileSync(htmlFile, 'utf-8');
  assert(content.includes('L.map'), 'Leaflet map instance required');
  assert(content.includes('updateRobotTelemetry'), 'Telemetry update function required');

  const data = JSON.parse(fs.readFileSync(dataFile, 'utf-8'));
  assert(data.robot_1.latitude !== undefined, 'Latitude required');
  assert(data.robot_1.moisture_value !== undefined, 'Moisture value required');

  console.log('Project 21 Robot Moisture Tracker validation passed');
}

runTest();
