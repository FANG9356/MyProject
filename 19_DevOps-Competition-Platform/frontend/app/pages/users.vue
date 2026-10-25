<template>
  <v-container class="pa-6" fluid>
    <v-card elevation="4" rounded="xl">
      <v-card-title
        class="d-flex align-center pa-6 text-h5 text-blue-darken-4 font-weight-black"
      >
        <div class="d-flex align-center">
          <v-icon start color="blue-darken-3">mdi-account-group</v-icon>
          <span>รายชื่อผู้ใช้งานในระบบ</span>
        </div>

        <v-spacer></v-spacer>

        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="ค้นหาชื่อ หรือ Username..."
          variant="outlined"
          density="compact"
          hide-details
          class="mr-4"
          style="max-width: 300px"
        ></v-text-field>

        <v-btn
          color="blue-darken-3"
          prepend-icon="mdi-plus"
          @click="openAddDialog"
          class="rounded-lg"
        >
          เพิ่มผู้ใช้ใหม่
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-table hover class="rounded-0">
        <thead class="bg-blue-lighten-5">
          <tr>
            <th class="text-left font-weight-bold" style="width: 30%">
              ชื่อ-นามสกุล
            </th>
            <th class="text-left font-weight-bold" style="width: 25%">
              ชื่อผู้ใช้งาน (Username)
            </th>
            <th class="text-center font-weight-bold" style="width: 15%">
              ระดับสิทธิ์ (Role)
            </th>
            <th class="text-center font-weight-bold" style="width: 15%">
              สถานะ
            </th>
            <th class="pl-8 font-weight-bold" style="width: 15%">
              จัดการ (Actions)
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id">
            <td>{{ user.name }}</td>
            <td>{{ user.username }}</td>
            <td class="text-center">
              <v-chip
                :color="getRoleColor(user.role)"
                size="small"
                class="font-weight-bold text-uppercase"
              >
                {{ user.role }}
              </v-chip>
            </td>
            <td class="text-center">
              <v-chip
                :color="user.status === 'Active' ? 'success' : 'error'"
                size="small"
                variant="tonal"
              >
                {{ user.status }}
              </v-chip>
            </td>
            <td class="pl-8">
              <v-btn
                v-if="
                  (authStore.user.role === 'admin' &&
                    (user.role === 'manager' || user.role === 'user')) ||
                  (authStore.user.role === 'manager' && user.role === 'user')
                "
                icon="mdi-pencil"
                variant="text"
                color="amber-darken-3"
                size="small"
                @click="openEditDialog(user)"
              ></v-btn>
              <v-btn
                v-if="
                  (authStore.user.role === 'admin' &&
                    (user.role === 'manager' || user.role === 'user')) ||
                  (authStore.user.role === 'manager' && user.role === 'user')
                "
                icon="mdi-delete"
                variant="text"
                color="red-darken-3"
                size="small"
                @click="openDeleteDialog(user)"
              ></v-btn>
            </td>
          </tr>
          <tr v-if="paginatedUsers.length === 0">
            <td colspan="5" class="text-center pa-4 text-grey">
              ไม่พบข้อมูลผู้ใช้งานที่ค้นหา
            </td>
          </tr>
        </tbody>
      </v-table>

      <v-divider></v-divider>

      <div class="text-center pa-4">
        <v-pagination
          v-model="page"
          :length="pageCount"
          color="blue-darken-3"
          rounded="circle"
        ></v-pagination>
      </div>
    </v-card>

    <UserFormDialog
      v-model="dialogForm"
      :item-data="selectedUser"
      :is-edit="isEditMode"
      @save="handleSaveUser"
    />

    <UserDeleteDialog
      v-model="dialogDelete"
      :user-id="selectedUser.id"
      :user-name="selectedUser.name"
      @confirm="handleDeleteUser"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "~/stores/auth";
import { useUsers } from "~/composables/useUsers";


definePageMeta({ layout: "dashboard" });

const authStore = useAuthStore();

const {
  search,
  page,
  pageCount,
  paginatedUsers,
  fetchUsers,
  saveUserAPI,
  deleteUserAPI,
} = useUsers();

const dialogForm = ref(false);
const dialogDelete = ref(false);
const isEditMode = ref(false);

const selectedUser = ref({});
const defaultItem = {
  id: null,
  name: "",
  username: "",
  role: authStore.user.role === "manager" ? "user" : "manager",
  status: "Active",
};

const openAddDialog = () => {
  selectedUser.value = { ...defaultItem };
  isEditMode.value = false;
  dialogForm.value = true;
};

const openEditDialog = (user) => {
  selectedUser.value = { ...user };
  isEditMode.value = true;
  dialogForm.value = true;
};

const openDeleteDialog = (user) => {
  selectedUser.value = { ...user };
  dialogDelete.value = true;
};

const handleSaveUser = async (userData, isEdit) => {
  const result = await saveUserAPI(userData, isEdit);
  if (result.success) {
    alert(isEdit ? "แก้ไขข้อมูลเรียบร้อย!" : "เพิ่มผู้ใช้งานเรียบร้อย!");
    dialogForm.value = false;
  } else {
    alert(`ผิดพลาด: ${result.message}`);
  }
};

const handleDeleteUser = async (userId) => {
  const result = await deleteUserAPI(userId);
  if (result.success) {
    alert("ลบข้อมูลสำเร็จ");
    dialogDelete.value = false;
  } else {
    alert(`ลบล้มเหลว: ${result.message}`);
  }
};

const getRoleColor = (role) => {
  if (role === "admin") return "purple-darken-2";
  if (role === "manager") return "blue-darken-2";
  return "grey-darken-2";
};

onMounted(() => {
  fetchUsers();
});

</script>
