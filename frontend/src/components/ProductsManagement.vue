<template>
  <div class="products-container">
    <h1 class="page-title">📦 Sản Phẩm Trong Kho</h1>

    <div class="table-section">
      <div class="table-header">
        <h2 class="section-title">Danh Sách Sản Phẩm</h2>
        <button @click="loadProducts" class="btn-refresh">🔄 Làm Mới</button>
      </div>

      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm theo barcode, tên sản phẩm..."
          class="search-input"
        />
      </div>

      <div v-if="loading" class="loading">Đang tải dữ liệu...</div>

      <div v-else-if="filteredProducts.length === 0" class="empty-state">
        Không có sản phẩm trong kho
      </div>

      <div v-else class="table-wrapper">
        <table class="products-table">
          <thead>
            <tr>
              <th>Barcode</th>
              <th>Thương Hiệu</th>
              <th>Tên Sản Phẩm</th>
              <th>Danh Mục</th>
              <th>Tồn Kho</th>
              <th>Hành Động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in filteredProducts" :key="idx">
              <td class="barcode-cell">{{ item[1] }}</td>
              <td>{{ item[2] }}</td>
              <td>{{ item[3] }}</td>
              <td>{{ item[4] }}</td>
              <td class="qty-cell">
                <span class="qty-badge">{{ item[5] }}</span>
              </td>
              <td>
                <button @click="toggleDetail(idx)" class="btn-detail">
                  {{ expandedRows.includes(idx) ? '−' : '+' }}
                </button>
              </td>
            </tr>

            <!-- Chi tiết lô nhập cho sản phẩm này -->
            <tr v-if="expandedRows.includes(idx)" class="detail-row">
              <td colspan="6">
                <div class="detail-content">
                  <h3 class="detail-title">Lịch Sử Nhập Hàng</h3>
                  <table class="detail-table">
                    <thead>
                      <tr>
                        <th>ProductID</th>
                        <th>Nhập</th>
                        <th>Đã Bán</th>
                        <th>Còn</th>
                        <th>Giá Vốn</th>
                        <th>Hòa Vốn</th>
                        <th>Ngày Nhập</th>
                        <th>Ghi Chú</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(batch, batchIdx) in getProductBatches(item[1])"
                        :key="batchIdx"
                      >
                        <td>{{ batch[0] }}</td>
                        <td>{{ batch[5] }}</td>
                        <td>{{ batch[10] }}</td>
                        <td>{{ batch[11] }}</td>
                        <td>{{ formatNumber(batch[6]) }}</td>
                        <td>{{ formatNumber(batch[7]) }}</td>
                        <td>{{ batch[8] }}</td>
                        <td>{{ batch[9] }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { productsAPI, importsAPI } from '../services/api';

const products = ref([]);
const imports = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const expandedRows = ref([]);

const filteredProducts = computed(() => {
  return products.value.filter((item) => {
    const query = searchQuery.value.toLowerCase();
    return (
      item[1].toLowerCase().includes(query) ||
      item[3].toLowerCase().includes(query)
    );
  });
});

async function loadProducts() {
  loading.value = true;
  try {
    const [productsResult, importsResult] = await Promise.all([
      productsAPI.getAll(),
      importsAPI.getAll(),
    ]);
    products.value = productsResult.data || [];
    imports.value = importsResult.data || [];
  } catch (error) {
    console.error('Error loading products:', error);
  } finally {
    loading.value = false;
  }
}

function toggleDetail(idx) {
  const foundIdx = expandedRows.value.indexOf(idx);
  if (foundIdx > -1) {
    expandedRows.value.splice(foundIdx, 1);
  } else {
    expandedRows.value.push(idx);
  }
}

function getProductBatches(barcode) {
  return imports.value.filter((item) => item[1] === barcode);
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}

onMounted(() => {
  loadProducts();
});
</script>

<style scoped>
.products-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  background: #fafaf9;
  min-height: 100vh;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2d5016;
  margin-bottom: 24px;
  text-align: center;
}

.table-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 16px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn-refresh {
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e5e7eb;
}

.search-bar {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}

.search-input:focus {
  outline: none;
  border-color: #86c06b;
  box-shadow: 0 0 0 3px rgba(134, 192, 107, 0.1);
}

.loading,
.empty-state {
  padding: 32px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #eee;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.products-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #eee;
}

.products-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.products-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
}

.barcode-cell {
  font-weight: 600;
  color: #2d5016;
  font-family: 'Courier New', monospace;
}

.qty-cell {
  text-align: center;
}

.qty-badge {
  display: inline-block;
  padding: 4px 8px;
  background: #dcfce7;
  color: #166534;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12px;
}

.btn-detail {
  padding: 6px 10px;
  background: #86c06b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-detail:hover {
  background: #6db046;
}

.detail-row {
  background: #fafaf9;
}

.detail-content {
  padding: 16px 0;
}

.detail-title {
  font-size: 13px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 12px;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  background: white;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.detail-table thead {
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.detail-table th {
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.detail-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #eee;
}

.detail-table tbody tr:last-child td {
  border-bottom: none;
}

@media (max-width: 640px) {
  .products-container {
    padding: 12px;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .products-table {
    font-size: 12px;
  }

  .products-table th,
  .products-table td {
    padding: 8px 6px;
  }

  .detail-table {
    font-size: 11px;
  }

  .detail-table th,
  .detail-table td {
    padding: 6px 4px;
  }
}
</style>
