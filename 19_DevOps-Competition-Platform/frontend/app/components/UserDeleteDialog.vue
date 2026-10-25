<template>
  <v-dialog v-model="isOpen" max-width="400px">
    <v-card rounded="xl" class="text-center pa-6">
      <v-icon color="red" size="60" class="mb-4"
        >mdi-alert-circle-outline</v-icon
      >
      <div class="text-h6 font-weight-bold mb-4">ยืนยันการลบข้อมูล?</div>
      <div class="text-body-2 text-grey-darken-1 mb-6">
        คุณแน่ใจหรือไม่ที่จะลบผู้ใช้งาน
        <strong>{{ userName }}</strong> ? <br />การกระทำนี้ไม่สามารถกู้คืนได้
      </div>

      <v-card-actions class="justify-center">
        <v-btn color="grey-darken-1" variant="text" @click="close"
          >ยกเลิก</v-btn
        >
        <v-btn
          color="red-darken-2"
          variant="elevated"
          class="px-6"
          :loading="loading"
          @click="handleDelete"
          >ลบข้อมูล</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  modelValue: Boolean,
  userId: [Number, String],
  userName: String,
});

const emit = defineEmits(["update:modelValue", "confirm"]);
const loading = ref(false);

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const close = () => {
  isOpen.value = false;
};

const handleDelete = () => {
  loading.value = true;
  emit("confirm", props.userId);
  loading.value = false;
};
</script>