<script setup>
const pages = [
  { name: 'Nhập Hàng', icon: '📦', path: '/import' },
  { name: 'Sản Phẩm', icon: '📦', path: '/product' },
  { name: 'Tạo Đơn', icon: '🛒', path: '/order' },
  { name: 'Đã Bán', icon: '📊', path: '/sold' },
  { name: 'Chi Tiêu', icon: '💰', path: '/expense' },
];
</script>

<template>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="header-content">
        <h1 class="app-title">AvocadoShop</h1>
        <p class="app-subtitle">Quản Lý Cửa Hàng Mỹ Phẩm</p>
      </div>
    </header>

    <!-- Navigation -->
    <nav class="app-nav">
      <router-link
        v-for="page in pages"
        :key="page.path"
        :to="page.path"
        class="nav-btn"
        active-class="active"
      >
        <span class="nav-icon">{{ page.icon }}</span>
        <span class="nav-label">{{ page.name }}</span>
      </router-link>
    </nav>

    <!-- Main Content -->
    <main class="app-main">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>© 2025 AvocadoShop - Quản Lý Bán Hàng Mỹ Phẩm</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    sans-serif;
  background: #fafaf9;
}

.app-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 100vh;
  background: #fafaf9;
}

.app-header {
  background: linear-gradient(135deg, #86c06b 0%, #6db046 100%);
  color: white;
  padding: 20px 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.app-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.app-subtitle {
  font-size: 14px;
  font-weight: 400;
  opacity: 0.95;
}

.app-nav {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border-bottom: 2px solid #eee;
  max-width: 100%;
  margin: 0 auto;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-family: inherit;
  color: #666;
  text-decoration: none;
}

.nav-btn:hover {
  background: #f3f4f6;
}

.nav-btn.active {
  background: linear-gradient(135deg, #86c06b 0%, #6db046 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(134, 192, 107, 0.3);
}

.nav-icon {
  font-size: 20px;
}

.nav-label {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.app-main {
  flex: 1;
  padding: 0;
  overflow-y: auto;
}

.app-footer {
  padding: 16px;
  text-align: center;
  background: white;
  border-top: 1px solid #eee;
  color: #999;
  font-size: 12px;
  margin-top: auto;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .app-header {
    padding: 16px 12px;
  }

  .app-title {
    font-size: 28px;
  }

  .app-subtitle {
    font-size: 12px;
  }

  .app-nav {
    gap: 4px;
    padding: 8px 8px;
  }

  .nav-btn {
    padding: 8px 4px;
    gap: 4px;
  }

  .nav-icon {
    font-size: 18px;
  }

  .nav-label {
    font-size: 11px;
  }
}

@media (max-width: 640px) {
  .app-title {
    font-size: 24px;
  }

  .nav-btn {
    padding: 6px 2px;
  }

  .nav-icon {
    font-size: 16px;
  }

  .nav-label {
    font-size: 10px;
  }
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #86c06b;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #6db046;
}
</style>
