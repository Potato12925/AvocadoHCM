<script setup>
import { useRouter, useRoute } from 'vue-router';
import { authAPI } from '@/services/api';

const router = useRouter();
const route = useRoute();

const pages = [
  { name: 'Nhập Hàng', icon: '📦', path: '/import' },
  { name: 'Sản Phẩm', icon: '📦', path: '/product' },
  { name: 'Tạo Đơn', icon: '🛒', path: '/order' },
  { name: 'Đã Bán', icon: '📊', path: '/sold' },
  { name: 'Chi Tiêu', icon: '💰', path: '/expense' },
];

const handleLogout = async () => {
  try {
    await authAPI.logout();
    router.push('/login');
  } catch (e) {
    console.error(e);
  }
};
</script>

<template>
  <div class="flex flex-col min-h-screen bg-stone-50">

    <!-- Header -->
    <header class="bg-gradient-to-br from-[#86c06b] to-[#6db046] text-white py-5 px-4 shadow-md relative flex justify-center items-center">
      <div class="text-center">
        <h1 class="text-3xl md:text-[32px] font-bold mb-1 tracking-tight">
          AvocadoShop
        </h1>
        <p class="text-sm opacity-95">
          Quản Lý Cửa Hàng Mỹ Phẩm
        </p>
      </div>
      <button 
        v-if="route.name !== 'login'"
        @click="handleLogout" 
        class="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg text-sm font-medium transition flex items-center gap-1"
      >
        Đăng xuất
      </button>
    </header>

    <!-- Navigation -->
    <nav v-if="route.name !== 'login'" class="grid grid-cols-5 gap-2 md:gap-2 p-3 md:p-4 bg-white border-b-2 border-gray-200 shadow-sm">

      <router-link
        v-for="page in pages"
        :key="page.path"
        :to="page.path"
        class="flex flex-col items-center gap-1 md:gap-2 py-2 px-1 rounded-lg text-gray-500 transition hover:bg-gray-100"
        active-class="bg-gradient-to-br from-[#86c06b] to-[#6db046] text-white shadow-md"
      >
        <span class="text-lg md:text-xl">
          {{ page.icon }}
        </span>

        <span class="text-[10px] md:text-xs font-semibold truncate">
          {{ page.name }}
        </span>

      </router-link>

    </nav>

    <!-- Main -->
    <main class="flex-1 overflow-y-auto">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="p-4 text-center bg-white border-t text-gray-400 text-xs">
      © 2025 AvocadoShop - Quản Lý Bán Hàng Mỹ Phẩm
    </footer>

  </div>
</template>