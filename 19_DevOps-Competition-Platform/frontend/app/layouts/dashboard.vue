<template>
  <v-layout style="min-height: 100vh">
    <v-app-bar color="blue-darken-3" elevation="2">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title class="font-weight-bold"
        >DevOps Management System</v-app-bar-title
      >
      <v-spacer></v-spacer>
      <v-btn variant="text" @click="handleLogout">
        <v-icon start>mdi-logout</v-icon> ออกจากระบบ
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer" elevation="2">
      <v-list>
        <v-list-item
          prepend-icon="mdi-account-circle"
          :title="authStore.username"
          :subtitle="'สิทธิ์: ' + authStore.user.role?.toUpperCase()"
        ></v-list-item>
      </v-list>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          prepend-icon="mdi-home"
          title="หน้าหลัก"
          to="/home"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-account"
          title="โปรไฟล์"
          to="/profile"
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-chart-bar"
          title="รายงานสถิติ"
          to="reports"
        ></v-list-item>
        <v-list-item
          v-if="
            authStore.user.role === 'admin' || authStore.user.role === 'manager'
          "
          prepend-icon="mdi-account-cog"
          title="จัดการผู้ใช้งาน"
          to="/users"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main class="bg-blue-lighten-5">
      <slot />
    </v-main>
  </v-layout>
</template>

<script setup>
import { useAuthStore } from "~/stores/auth";
const authStore = useAuthStore();

const drawer = ref(null);

const handleLogout = () => {
  authStore.logout();
};
</script>