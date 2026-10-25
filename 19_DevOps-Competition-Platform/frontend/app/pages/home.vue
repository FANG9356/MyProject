<template>
  <v-container class="pa-6" fluid>
    <v-card elevation="4" rounded="xl">
      <v-card-title
        class="d-flex align-center pa-6 text-h5 text-blue-darken-4 font-weight-black"
      >
        <div class="d-flex align-center">
          <v-icon start color="blue-darken-3">mdi-view-dashboard</v-icon>
          <span>ยินดีต้อนรับสู่ระบบแดชบอร์ด</span>
        </div>
        <v-spacer></v-spacer>
      </v-card-title>

      <v-card-text>
        <div class="text-body-1 mb-4">
          สวัสดี <strong>{{ authStore.user?.username }}</strong
          >! คุณเข้าสู่ระบบสำเร็จด้วยสิทธิ์การใช้งานระดับ:
          <v-chip
            color="blue-darken-3"
            class="ml-2 font-weight-bold"
            size="small"
          >
            {{ authStore.user.role?.toUpperCase() }}
          </v-chip>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { useAuthStore } from "~/stores/auth";

definePageMeta({
  layout: "dashboard",
});

const authStore = useAuthStore();
</script>