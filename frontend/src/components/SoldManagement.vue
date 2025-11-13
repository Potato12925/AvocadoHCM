<template>
  <div class="sold-container">
    <h1 class="page-title">📊 Lịch Sử Bán Hàng</h1>

    <div class="table-section">
      <div class="table-header">
        <h2 class="section-title">Danh Sách Sản Phẩm Đã Bán</h2>
        <button @click="loadSoldItems" class="btn-refresh">🔄 Làm Mới</button>
      </div>

      <div class="filter-section">
        <div class="filter-group">
          <label for="filterOrderID">Mã Đơn Hàng</label>
          <input
            v-model="filterOrderID"
            type="text"
            id="filterOrderID"
            placeholder="Tìm mã đơn..."
            class="filter-input"
          />
        </div>

        <div class="filter-group">
          <label for="filterBarcode">Barcode</label>
          <input
            v-model="filterBarcode"
            type="text"
            id="filterBarcode"
            placeholder="Tìm barcode..."
            class="filter-input"
          />
        </div>

        <div class="filter-group">
          <label for="filterStartDate">Từ Ngày</label>
          <input
            v-model="filterStartDate"
            type="date"
            id="filterStartDate"
            class="filter-input"
          />
        </div>

        <div class="filter-group">
          <label for="filterEndDate">Đến Ngày</label>
          <input
            v-model="filterEndDate"
            type="date"
            id="filterEndDate"
            class="filter-input"
          />
        </div>

        <button @click="resetFilters" class="btn-reset">Xóa Bộ Lọc</button>
      </div>

      <div v-if="loading" class="loading">Đang tải dữ liệu...</div>

      <div v-else-if="filteredSoldItems.length === 0" class="empty-state">
        Không có dữ liệu bán hàng
      </div>

      <div v-else class="table-wrapper">
        <table class="sold-table">
          <thead>
            <tr>
              <th>Mã Đơn</th>
              <th>Barcode</th>
              <th>Tên Sản Phẩm</th>
              <th>Brand</th>
              <th>Danh Mục</th>
              <th>Số Lượng</th>
              <th>Giá Vốn (₫)</th>
              <th>Thành Tiền (₫)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in filteredSoldItems" :key="idx">
              <td class="order-id">{{ item[0] }}</td>
              <td>{{ item[2] }}</td>
              <td>{{ item[4] }}</td>
              <td>{{ item[3] }}</td>
              <td>{{ item[5] }}</td>
              <td class="qty-cell">{{ item[6] }}</td>
              <td class="price-cell">{{ formatNumber(item[7]) }}</td>
              <td class="total-cell">{{ formatNumber(item[8]) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredSoldItems.length > 0" class="summary-section">
        <div class="summary-row">
          <span class="summary-label">Tổng Sản Phẩm Bán:</span>
          <span class="summary-value">{{ totalQtySold }}</span>
        </div>
        <div class="summary-row">
          <span class="summary-label">Tổng Giá Vốn:</span>
          <span class="summary-value">{{ formatNumber(totalCostSold) }}₫</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { soldAPI } from '../services/api';

const soldItems = ref([]);
const loading = ref(false);
const filterOrderID = ref('');
const filterBarcode = ref('');
const filterStartDate = ref('');
const filterEndDate = ref('');

const filteredSoldItems = computed(() => {
  return soldItems.value.filter((item) => {
    // Filter by order ID
    if (filterOrderID.value && !item[0].toLowerCase().includes(filterOrderID.value.toLowerCase())) {
      return false;
    }

    // Filter by barcode
    if (filterBarcode.value && !item[2].toLowerCase().includes(filterBarcode.value.toLowerCase())) {
      return false;
    }

    // Filter by date range if needed (would require parsing dates from order data)
    // For now, this is a placeholder as sold items don't directly include date

    return true;
  });
});

const totalQtySold = computed(() => {
  return filteredSoldItems.value.reduce((sum, item) => sum + parseInt(item[6] || 0), 0);
});

const totalCostSold = computed(() => {
  return filteredSoldItems.value.reduce((sum, item) => sum + parseFloat(item[8] || 0), 0);
});

async function loadSoldItems() {
  loading.value = true;
  try {
    const result = await soldAPI.getAll();
    soldItems.value = result.data || [];
  } catch (error) {
    console.error('Error loading sold items:', error);
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filterOrderID.value = '';
  filterBarcode.value = '';
  filterStartDate.value = '';
  filterEndDate.value = '';
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}

onMounted(() => {
  loadSoldItems();
});
</script>

<style scoped>
.sold-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  background: #fafaf9;
  min-height: 100vh;
}

.page-title {
  font-size: 32px;
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
  font-size: 18px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 16px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-refresh {
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e5e7eb;
}

.filter-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  padding: 16px;
  background: #fafaf9;
  border-radius: 8px;
  margin-bottom: 16px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 13px;
  font-weight: 500;
  color: #555;
}

.filter-input {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.filter-input:focus {
  outline: none;
  border-color: #86c06b;
  box-shadow: 0 0 0 3px rgba(134, 192, 107, 0.1);
}

.btn-reset {
  align-self: flex-end;
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reset:hover {
  background: #e5e7eb;
}

.loading,
.empty-state {
  padding: 32px;
  text-align: center;
  color: #999;
  font-size: 15px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #eee;
  margin-bottom: 16px;
}

.sold-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.sold-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #eee;
}

.sold-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.sold-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
}

.order-id {
  font-weight: 600;
  color: #2d5016;
  font-family: 'Courier New', monospace;
}

.qty-cell,
.price-cell,
.total-cell {
  text-align: right;
  font-weight: 500;
}

.price-cell {
  color: #666;
}

.total-cell {
  color: #86c06b;
  font-weight: 600;
}

.summary-section {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #eee;
}

.summary-row {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 8px;
}

.summary-row:last-child {
  margin-bottom: 0;
}

.summary-label {
  color: #666;
}

.summary-value {
  color: #86c06b;
}

@media (max-width: 768px) {
  .filter-section {
    grid-template-columns: 1fr;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .sold-table {
    font-size: 12px;
  }

  .sold-table th,
  .sold-table td {
    padding: 8px 6px;
  }
}

@media (max-width: 640px) {
  .sold-container {
    padding: 12px;
  }

  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .btn-refresh {
    width: 100%;
  }
}
</style>
