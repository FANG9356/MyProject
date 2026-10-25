<template>
  <v-container
    fluid
    class="fill-height bg-blue-lighten-5 d-flex align-start justify-center pt-16"
  >
    <v-card
      class="w-100 pa-8 rounded-lg"
      max-width="450"
      style="border-top: 5px solid #1565c0"
    >
      <div class="text-center mb-6">
        <h2 class="text-h4 font-weight-black text-blue-darken-4 mb-2">
          เข้าสู่ระบบ
        </h2>
        <div class="text-subtitle-1 text-grey-darken-1">
          จัดการระบบด้วยกระบวนการ DevOps
        </div>
      </div>

      <v-alert
        v-if="errorMessage"
        type="error"
        variant="tonal"
        color="error"
        border="start"
        border-color="error"
        density="compact"
        class="text-body-2 pa-3 rounded-lg mb-4"
        closable
        icon="mdi-alert-circle-outline"
        @click:close="errorMessage = ''"
      >
        {{ errorMessage }}
      </v-alert>

      <v-form @submit.prevent="handleLogin">
        <v-text-field
          v-model="username"
          label="ชื่อผู้ใช้งาน (Username)"
          prepend-inner-icon="mdi-account"
          variant="outlined"
          color="blue-darken-3"
          class="mb-3"
          required
        ></v-text-field>

        <v-text-field
          v-model="password"
          label="รหัสผ่าน (Password)"
          type="password"
          prepend-inner-icon="mdi-lock"
          variant="outlined"
          color="blue-darken-3"
          class="mb-6"
          required
        ></v-text-field>

        <v-btn
          color="blue-darken-3"
          size="x-large"
          block
          type="submit"
          class="rounded-lg text-body-1 font-weight-bold"
          elevation="4"
          :loading="isLoading"
        >
          เข้าสู่ระบบ
        </v-btn>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "~/stores/auth";

definePageMeta({ layout: "blank" });

const router = useRouter();
const authStore = useAuthStore();

const username = ref("");
const password = ref("");
const isLoading = ref(false); // ทำปุ่มหมุนติ้วๆ ตอนรอ API
const errorMessage = ref(""); // ไว้แสดงข้อความเตือนถ้ากรอกผิด

const handleLogin = async () => {
  if (!username.value.trim() || !password.value.trim()) {
    errorMessage.value = "กรอก: ชื่อผู้ใช้งาน, รหัสผ่าน ให้เรียบร้อย";
    return; // สั่ง return เพื่อ "เบรก" ไม่ให้โค้ดทำงานต่อ (ไม่ส่งไปหลังบ้าน)
  }
  errorMessage.value = "";
  isLoading.value = true;

  try {
    const success = await authStore.login(username.value, password.value);

    if (success) {
      router.push("/home");
    }
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    isLoading.value = false; // ปิดสถานะโหลด
  }
};
</script>