import { defineStore } from "pinia";
import api from "~/services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: null,
    user: null,
  }),

  actions: {
    async login(username, password) {
      const tokenCookie = useCookie("auth_token");
      try {
        const response = await api.post("/auth/login", {
          username,
          password,
        });

        if (response.data.status === "success") {
          tokenCookie.value = response.data.token;

          this.token = response.data.token;
          this.user = response.data.user;

          alert(`เข้าสู่ระบบสำเร็จ! ยินดีต้อนรับ ${this.user.username}`);
          return true;
        }
      } catch (err) {
        const errorMessage =
          err.response?.data?.message || "เกิดข้อผิดพลาดในการเชื่อมต่อ";
        throw new Error(errorMessage);
      }
    },

    async logout() {
      const tokenCookie = useCookie("auth_token");
      tokenCookie.value = null;

      if (import.meta.client) {
        alert("ออกจากระบบเรียบร้อยแล้ว");
        await navigateTo("/");

        this.token = null;
        this.user = null;
      }
    },
  },
});