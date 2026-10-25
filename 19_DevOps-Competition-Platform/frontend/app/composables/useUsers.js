import { ref, computed, watch } from "vue";
import { useAuthStore } from "~/stores/auth";
import api from "~/services/api";

export function useUsers() {
  const authStore = useAuthStore();

  const users = ref([]);
  const search = ref("");
  const page = ref(1);
  const itemsPerPage = ref(2); // ปรับเป็น 5 หรือตามที่ต้องการ

  const fetchUsers = async () => {
    try {
      const response = await api.get("users", {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      if (response.data.status === "success") {
        users.value = response.data.users;
      }
    } catch (error) {
      console.error("ดึงข้อมูลล้มเหลว:", error);
    }
  };

  const filteredUsers = computed(() => {
    if (!search.value) return users.value;
    const searchLower = search.value.toLowerCase();
    return users.value.filter(
      (u) =>
        u.name.toLowerCase().includes(searchLower) ||
        u.username.toLowerCase().includes(searchLower),
    );
  });

  const pageCount = computed(() =>
    Math.ceil(filteredUsers.value.length / itemsPerPage.value),
  );
  const paginatedUsers = computed(() => {
    const start = (page.value - 1) * itemsPerPage.value;
    const end = start + itemsPerPage.value;
    return filteredUsers.value.slice(start, end);
  });

  watch(search, () => {
    page.value = 1;
  });

  const saveUserAPI = async (userData, isEdit) => {
    try {
      if (isEdit) {
        await api.put(`/users/${userData.id}`, userData, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        });
      } else {
        await api.post(`/users`, userData, {
          headers: { Authorization: `Bearer ${authStore.token}` },
        });
      }
      await fetchUsers(); // โหลดข้อมูลใหม่
      return { success: true };
    } catch (error) {
      const errorMsg =
        error.response?._data?.message || "เกิดข้อผิดพลาดในการบันทึก";
      return { success: false, message: errorMsg };
    }
  };

  const deleteUserAPI = async (userId) => {
    try {
      await api.delete(`/users/${userId}`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      });
      await fetchUsers(); // โหลดข้อมูลใหม่
      return { success: true };
    } catch (error) {
      const errorMsg = error.message || "เกิดข้อผิดพลาดในการลบข้อมูล";
      return { success: false, message: errorMsg };
    }
  };

  return {
    users,
    search,
    page,
    pageCount,
    paginatedUsers,
    fetchUsers,
    saveUserAPI,
    deleteUserAPI,
  };
}