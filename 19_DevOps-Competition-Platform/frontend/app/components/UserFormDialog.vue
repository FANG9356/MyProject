<template>
  <v-dialog v-model="isOpen" max-width="500px">
    <v-card rounded="xl">
      <v-card-title class="bg-blue-darken-3 text-white pa-4">
        <span class="text-h6">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text class="pa-6">
        <v-form ref="form">
          <v-text-field
            v-model="localItem.name"
            label="ชื่อ-นามสกุล"
            variant="outlined"
            class="mb-4"
            hide-details="auto"
          ></v-text-field>
          <v-text-field
            v-model="localItem.username"
            label="ชื่อผู้ใช้งาน (Username)"
            variant="outlined"
            class="mb-4"
            :readonly="isEdit"
            :bg-color="isEdit ? 'grey-lighten-4' : ''"
            hide-details="auto"
          >
            <template v-slot:append-inner v-if="isEdit">
              <v-tooltip location="top">
                <template v-slot:activator="{ props }">
                  <v-icon v-bind="props" color="orange-darken-2"
                    >mdi-lock-outline</v-icon
                  >
                </template>
                <span>ระบบไม่อนุญาตให้เปลี่ยน Username</span>
              </v-tooltip>
            </template>
          </v-text-field>
          <v-select
            v-model="localItem.role"
            :items="
              authStore.user.role === 'manager' ? ['user'] : ['manager', 'user']
            "
            label="ระดับสิทธิ์ (Role)"
            variant="outlined"
            class="mb-4"
            :readonly="authStore.user.role === 'manager'"
            :bg-color="
              authStore.user.role === 'manager' ? 'grey-lighten-4' : ''
            "
            hide-details="auto"
          ></v-select>
          <v-select
            v-model="localItem.status"
            :items="['Active', 'Inactive']"
            label="สถานะการใช้งาน"
            variant="outlined"
            class="mb-4"
            hide-details="auto"
          ></v-select>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4 pt-0">
        <v-spacer></v-spacer>
        <v-btn color="grey-darken-1" variant="text" @click="close"
          >ยกเลิก</v-btn
        >
        <v-btn
          color="blue-darken-3"
          variant="elevated"
          :loading="loading"
          @click="handleSave"
          >บันทึกข้อมูล</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from "vue";

const props = defineProps({
  modelValue: Boolean,
  itemData: Object,
  isEdit: Boolean,
});

const emit = defineEmits(["update:modelValue", "save"]);
const loading = ref(false);

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const formTitle = computed(() =>
  props.isEdit ? "แก้ไขข้อมูลผู้ใช้งาน" : "เพิ่มผู้ใช้งานใหม่",
);

const localItem = ref({ ...props.itemData });

watch(
  () => props.itemData,
  (newVal) => {
    localItem.value = { ...newVal };
  },
  { deep: true },
);

const close = () => {
  isOpen.value = false;
};

const handleSave = async () => {
  loading.value = true;
  emit("save", { ...localItem.value }, props.isEdit);
  loading.value = false;
};
</script>