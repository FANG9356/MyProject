const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTest() {
  const rootDir = __dirname;
  const backendServer = path.join(rootDir, 'backend', 'server.js');
  const nuxtConfig = path.join(rootDir, 'frontend', 'nuxt.config.ts');
  const inoSketch = path.join(rootDir, 'iot', 'Arduino IDE', 'project', 'lab_devops_bmp_millis_wifi_mqtt_json_06', 'lab_devops_bmp_millis_wifi_mqtt_json_06.ino');
  const gitlabCi = path.join(rootDir, 'backend', '..', '..', '19_DevOps-Competition-Platform', 'backend', '.gitlab-ci.yml');

  assert(fs.existsSync(backendServer), 'Backend server.js must exist');
  assert(fs.existsSync(nuxtConfig), 'Frontend nuxt.config.ts must exist');
  assert(fs.existsSync(inoSketch), 'IoT Arduino sketch must exist');

  const backendCode = fs.readFileSync(backendServer, 'utf-8');
  assert(backendCode.includes('express'), 'Backend must use express');

  const sketchCode = fs.readFileSync(inoSketch, 'utf-8');
  assert(sketchCode.includes('PubSubClient'), 'Sketch must use PubSubClient for MQTT');

  console.log('Project 19 DevOps Competition Platform validation passed');
}

runTest();
