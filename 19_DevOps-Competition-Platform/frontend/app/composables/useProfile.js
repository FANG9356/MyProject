import { ref } from "vue";
import { useAuthStore } from "~/stores/auth";
import api from "~/services/api";

export function useProfile() {
  const authStore = useAuthStore();

  const isEditing = ref(false);

  const formData = ref({
    name: "",
    username: "",
    password: "",
    confirmPassword: "",
  });

  const imageFile = ref(null);
  const defaultImage = `${import.meta.env.VITE_SERVER_URL}uploads/no-profile.jpg`;

  const getExistingImageUrl = () => {
    return authStore.user?.profile_image
      ? `${import.meta.env.VITE_SERVER_URL}${authStore.user.profile_image}`
      : defaultImage;
  };

  const imagePreview = ref(getExistingImageUrl());

  const toggleEdit = () => {
    formData.value.name = authStore.user?.name || "";
    formData.value.username = authStore.user?.username || "";
    formData.value.password = "";
    formData.value.confirmPassword = "";
    imagePreview.value = getExistingImageUrl();
    isEditing.value = true;
  };

  const cancelEdit = () => {
    isEditing.value = false;
    imageFile.value = null;
    imagePreview.value = getExistingImageUrl();
  };

  const onImageChange = (file) => {
    if (file && file.length > 0) {
      imagePreview.value = URL.createObjectURL(file[0]);
    } else {
      imagePreview.value = getExistingImageUrl();
    }
  };

  const saveProfileAPI = async () => {
    if (
      formData.value.password &&
      formData.value.password !== formData.value.confirmPassword
    ) {
      return {
        success: false,
        message: "รหัสผ่านใหม่และการยืนยันรหัสผ่านไม่ตรงกัน!",
      };
    }

    try {
      const payload = new FormData();
      payload.append("name", formData.value.name);
      if (formData.value.password)
        payload.append("password", formData.value.password);

      if (imageFile.value) {
        const actualFile = Array.isArray(imageFile.value)
          ? imageFile.value[0]
          : imageFile.value;
        if (actualFile && actualFile.name) {
          payload.append("profile_image", actualFile);
        }
      }

      const response = await api.put("/auth/profile", payload, {
        headers: {
          Authorization: `Bearer ${authStore.token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.status === "success") {
        authStore.user.name = formData.value.name;

        if (response.data.newImage) {
          const timestamp = new Date().getTime();
          const fullImageUrl = `${import.meta.env.VITE_SERVER_URL}${response.data.newImage}?t=${timestamp}`;
          imagePreview.value = fullImageUrl;
          authStore.user.profile_image = response.data.newImage;
        }

        isEditing.value = false;
        return { success: true, message: "บันทึกข้อมูลโปรไฟล์เรียบร้อยแล้ว!" };
      }
    } catch (error) {
      const errorMsg =
        error.response?._data?.message || "เกิดข้อผิดพลาดในการเชื่อมต่อ";
      return { success: false, message: errorMsg };
    }
  };

  return {
    isEditing,
    formData,
    imageFile,
    imagePreview,
    toggleEdit,
    cancelEdit,
    onImageChange,
    saveProfileAPI,
  };
}