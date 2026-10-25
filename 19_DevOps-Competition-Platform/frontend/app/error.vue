<template>
  <v-app>
    <v-main class="bg-blue-lighten-5">
      <v-container fluid class="fill-height d-flex align-center justify-center">
        <v-card
          class="pa-10 text-center"
          rounded="xl"
          elevation="8"
          max-width="500"
          width="100%"
        >
          <v-icon
            :color="
              error?.statusCode === 404 ? 'orange-darken-2' : 'red-darken-2'
            "
            size="120"
            class="mb-6"
          >
            {{
              error?.statusCode === 404
                ? "mdi-file-search-outline"
                : "mdi-shield-lock-outline"
            }}
          </v-icon>

          <h1
            class="text-h1 font-weight-black mb-2 text-grey-darken-4"
            style="line-height: 1"
          >
            {{ error?.statusCode || "Error" }}
          </h1>

          <p class="text-h6 text-grey-darken-1 mb-8">
            {{
              error?.statusCode === 404
                ? "ขออภัย ไม่พบหน้าที่คุณกำลังค้นหา"
                : "คุณไม่มีสิทธิ์เข้าถึงข้อมูลในส่วนนี้"
            }}
          </p>

          <v-btn
            color="blue-darken-3"
            size="x-large"
            @click="handleError"
            class="rounded-xl font-weight-bold px-8"
            prepend-icon="mdi-home"
            elevation="4"
          >
            กลับสู่หน้าหลัก
          </v-btn>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
const props = defineProps({
  error: Object,
});

const handleError = () => {
  clearError({ redirect: "/home" });
};
</script>