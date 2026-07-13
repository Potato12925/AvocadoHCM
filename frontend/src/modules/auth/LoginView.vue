<template>
  <div class="flex items-center justify-center min-h-[70vh] bg-stone-50 p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
      <div class="bg-gradient-to-br from-[#86c06b] to-[#6db046] p-6 text-center">
        <h2 class="text-2xl font-bold text-white mb-1">Đăng Nhập</h2>
        <p class="text-[#e2f0d9] text-sm">AvocadoShop - Quản Lý Bán Hàng</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="p-6 md:p-8 space-y-6">
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">Mật khẩu</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-[#86c06b] focus:ring-2 focus:ring-[#86c06b] focus:ring-opacity-50 transition-colors bg-gray-50 text-gray-900"
            placeholder="Nhập mật khẩu..."
            required
            :disabled="isLoading"
          />
        </div>

        <div v-if="errorMsg" class="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-100 flex items-center gap-2">
          <span>⚠️</span>
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full py-3 px-4 bg-[#86c06b] hover:bg-[#7ab160] text-white font-bold rounded-xl shadow-md transition-transform active:scale-95 disabled:opacity-70 disabled:active:scale-100 flex justify-center items-center gap-2"
        >
          <span v-if="isLoading" class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
          <span>{{ isLoading ? 'Đang xử lý...' : 'Đăng Nhập' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { authAPI } from '@/services/api';

const router = useRouter();
const route = useRoute();
const password = ref('');
const errorMsg = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  if (!password.value) return;
  
  try {
    isLoading.value = true;
    errorMsg.value = '';
    await authAPI.login(password.value);
    
    localStorage.setItem('isAuthenticated', 'true');
    
    // Redirect to where they wanted to go, or home
    const redirectPath = route.query.redirect || '/';
    router.push(redirectPath);
  } catch (err) {
    errorMsg.value = err.message || 'Mật khẩu không đúng hoặc lỗi hệ thống';
  } finally {
    isLoading.value = false;
  }
};
</script>
