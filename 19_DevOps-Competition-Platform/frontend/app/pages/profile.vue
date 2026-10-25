<template>
  <v-container class="pa-6" fluid>
    <v-card elevation="4" rounded="xl">
      <v-card-title
        class="d-flex align-center pa-6 text-h5 text-blue-darken-4 font-weight-black"
      >
        <div class="d-flex align-center">
          <v-icon start color="blue-darken-3">mdi-account</v-icon>
          <span>ข้อมูลส่วนตัว</span>
        </div>
        <v-spacer></v-spacer>
        <div class="d-flex align-center">
          <v-btn
            v-if="!isEditing"
            color="blue-darken-3"
            variant="outlined"
            prepend-icon="mdi-pencil"
            @click="toggleEdit"
            class="rounded-lg"
          >
            แก้ไขโปรไฟล์
          </v-btn>
        </div>
      </v-card-title>

      <v-card-text class="pa-6">
        <v-form @submit.prevent="saveProfile">
          <v-row>
            <v-col cols="12" md="4" class="d-flex flex-column align-center">
              <v-avatar
                size="160"
                color="grey-lighten-3"
                class="mb-4 elevation-3"
              >
                <v-img :src="imagePreview" cover></v-img>
              </v-avatar>

              <v-file-input
                v-if="isEditing"
                v-model="imageFile"
                accept="image/png, image/jpeg"
                label="อัปโหลดรูปภาพใหม่"
                variant="outlined"
                density="compact"
                prepend-icon="mdi-camera"
                @update:model-value="onImageChange"
                hide-details
                class="w-100"
              ></v-file-input>
              <div v-if="isEditing" class="text-caption text-grey mt-2">
                รองรับไฟล์ JPG, PNG ขนาดไม่เกิน 2MB
              </div>
            </v-col>

            <v-col cols="12" md="8">
              <div class="text-subtitle-1 font-weight-bold mb-2">
                ข้อมูลทั่วไป
              </div>

              <div v-if="!isEditing" class="mb-6">
                <div class="text-grey-darken-1 mb-1">ชื่อ-นามสกุล (Name)</div>
                <div class="text-body-1 mb-4">
                  {{ authStore.user?.name || "-" }}
                </div>

                <div class="text-grey-darken-1 mb-1">
                  ชื่อผู้ใช้งาน (Username)
                </div>
                <div class="text-body-1">{{ authStore.user?.username }}</div>
              </div>

              <div v-else>
                <v-text-field
                  v-model="formData.name"
                  label="ชื่อ-นามสกุล (Name)"
                  prepend-inner-icon="mdi-badge-account"
                  variant="outlined"
                  color="blue-darken-3"
                  class="mb-2"
                ></v-text-field>

                <v-text-field
                  v-model="formData.username"
                  label="ชื่อผู้ใช้งาน (Username)"
                  prepend-inner-icon="mdi-account"
                  variant="outlined"
                  color="blue-darken-3"
                  class="mb-4"
                  readonly
                ></v-text-field>

                <v-divider class="mb-4"></v-divider>

                <div
                  class="text-subtitle-1 font-weight-bold mb-2 text-red-darken-2"
                >
                  เปลี่ยนรหัสผ่าน (เว้นว่างไว้หากไม่ต้องการเปลี่ยน)
                </div>
                <v-text-field
                  v-model="formData.password"
                  label="รหัสผ่านใหม่ (New Password)"
                  type="password"
                  prepend-inner-icon="mdi-lock-reset"
                  variant="outlined"
                  color="blue-darken-3"
                  class="mb-2"
                ></v-text-field>

                <v-text-field
                  v-model="formData.confirmPassword"
                  label="ยืนยันรหัสผ่านใหม่ (Confirm Password)"
                  type="password"
                  prepend-inner-icon="mdi-lock-check"
                  variant="outlined"
                  color="blue-darken-3"
                  class="mb-6"
                ></v-text-field>
              </div>

              <div v-if="isEditing" class="d-flex justify-end mt-4">
                <v-btn
                  color="grey-darken-1"
                  variant="text"
                  size="large"
                  class="mr-4"
                  @click="cancelEdit"
                >
                  ยกเลิก
                </v-btn>
                <v-btn
                  color="blue-darken-3"
                  size="large"
                  type="submit"
                  elevation="2"
                  class="px-8 rounded-lg font-weight-bold"
                >
                  <v-icon start>mdi-content-save</v-icon> บันทึกข้อมูล
                </v-btn>
              </div>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { useAuthStore } from "~/stores/auth";
import { useProfile } from "~/composables/useProfile";

definePageMeta({ layout: "dashboard" });

const authStore = useAuthStore();

const {
  isEditing,
  formData,
  imageFile,
  imagePreview,
  toggleEdit,
  cancelEdit,
  onImageChange,
  saveProfileAPI,
} = useProfile();

const saveProfile = async () => {
  const result = await saveProfileAPI();
  if (result.success) {
    alert(result.message);
  } else {
    alert(`ผิดพลาด: ${result.message}`);
  }
};
</script>