import { useAuthStore } from "~/stores/auth";
import api from "~/services/api";

export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore();
  const token = useCookie("auth_token").value;

  if (token && !authStore.user) {
    try {
      const response = await api.get("/auth/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.data.status === "success") {
        authStore.user = response.data.user;
        authStore.token = token; // อัปเดต token ใน Store ให้ตรงกัน
      }
    } catch (error) {
      useCookie("auth_token").value = null;
      return navigateTo("/");
    }
  }


  if (token && to.path === "/") {
    return navigateTo("/home");
  }

  const publicRoutes = ["/"];

  if (!publicRoutes.includes(to.path) && !token) {
    return navigateTo("/"); // เตะกลับไปหน้า / ทันที
  }

  if (to.path === "/users") {
    if (
      authStore.user?.role !== "admin" &&
      authStore.user?.role !== "manager"
    ) {
      if (import.meta.client) {
        alert("ระบบจำกัดสิทธิ์: คุณไม่สามารถเข้าถึงหน้าจัดการผู้ใช้งานได้");
      }
      return navigateTo("/home"); // ถ้าสิทธิ์ไม่ถึง ให้เตะกลับไป /home
    }
  }
});