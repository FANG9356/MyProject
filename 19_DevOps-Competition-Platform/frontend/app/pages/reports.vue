<template>
  <v-container class="pa-6" fluid>
    <v-card elevation="4" rounded="xl">
      <v-card-title
        class="d-flex align-center pa-6 text-h5 text-blue-darken-4 font-weight-black"
      >
        <div class="d-flex align-center">
          <v-icon start color="blue-darken-3">mdi-chart-line</v-icon>
          <span>รายงานสถิติระบบ</span>
        </div>
        <v-spacer></v-spacer>
      </v-card-title>

      <v-card-text
        class="d-flex flex-column flex-grow-1 pa-4 pa-md-6"
        style="overflow: hidden"
      >
        <v-row class="flex-grow-1" style="margin: 0">
          <v-col cols="12" md="4" class="d-flex flex-column pa-2">
            <div
              class="text-subtitle-1 text-md-h6 font-weight-bold text-grey-darken-4 mb-2 d-flex align-center"
            >
              <v-icon color="blue-darken-2" class="mr-2">mdi-gauge</v-icon>
              อุณหภูมิปัจจุบัน (Temperature)
            </div>
            <div class="iframe-container flex-grow-1">
              <iframe :src="getGrafanaUrl('panel-2')" frameborder="0"></iframe>
            </div>
          </v-col>

          <v-col cols="12" md="8" class="d-flex flex-column pa-2">
            <div
              class="d-flex flex-column flex-sm-row justify-space-between align-start align-sm-center mb-2"
            >
              <div
                class="text-subtitle-1 text-md-h6 font-weight-bold text-grey-darken-4 d-flex align-center"
              >
                <v-icon color="blue-darken-2" class="mr-2">mdi-history</v-icon>
                อุณหภูมิย้อนหลัง 1 ชั่วโมง
              </div>
            </div>
            <div class="iframe-container flex-grow-1">
              <iframe :src="getGrafanaUrl('panel-1')" frameborder="0"></iframe>
            </div>
          </v-col>
        </v-row>

        <v-divider
          class="my-4 border-opacity-50"
          color="blue-lighten-4"
        ></v-divider>

        <v-row class="flex-grow-1" style="margin: 0">
          <v-col cols="12" md="4" class="d-flex flex-column pa-2">
            <div
              class="text-subtitle-1 text-md-h6 font-weight-bold text-grey-darken-4 mb-2 d-flex align-center"
            >
              <v-icon color="blue-darken-2" class="mr-2">mdi-gauge</v-icon>
              ความกดอากาศปัจจุบัน (Pressure)
            </div>
            <div class="iframe-container flex-grow-1">
              <iframe :src="getGrafanaUrl('panel-3')" frameborder="0"></iframe>
            </div>
          </v-col>

          <v-col cols="12" md="8" class="d-flex flex-column pa-2">
            <div
              class="d-flex flex-column flex-sm-row justify-space-between align-start align-sm-center mb-2"
            >
              <div
                class="text-subtitle-1 text-md-h6 font-weight-bold text-grey-darken-4 d-flex align-center"
              >
                <v-icon color="blue-darken-2" class="mr-2">mdi-history</v-icon>
                ความกดอากาศย้อนหลัง 1 ชั่วโมง
              </div>
            </div>
            <div class="iframe-container flex-grow-1">
              <iframe :src="getGrafanaUrl('panel-4')" frameborder="0"></iframe>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
definePageMeta({ layout: "dashboard" });

const getGrafanaUrl = (panelId) => {
  const baseUrl = import.meta.env.VITE_GRAFANA_URL;

  const params = new URLSearchParams({
    orgId: "1",
    from: "now-1h",
    to: "now",
    timezone: "browser",
    refresh: "10s",
    panelId: panelId,
    theme: "light",
  });
  console.log(`${baseUrl}?${params.toString()}`);
  return `${baseUrl}?${params.toString()}`;
};
</script>

<style scoped>
/* การตั้งค่า Iframe เพื่อให้ฟิตพอดีกับช่องว่างที่เหลืออยู่ 100% โดยไม่เกิด Scrollbar */
.iframe-container {
  position: relative; /* ล็อกกรอบเอาไว้ */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
  background-color: #f9f9f9;
  width: 100%;
  min-height: 200px; /* กันกราฟพังในจอมือถือเล็กๆ */
}

/* บังคับ iframe ให้กางเต็มกรอบที่ครอบมันอยู่เสมอ */
.iframe-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}
</style>