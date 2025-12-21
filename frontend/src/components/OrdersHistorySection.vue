<template>
  <div class="history-section">
    <div class="history-header">
      <h2 class="section-title">Lịch sử đơn hàng</h2>
      <button
        type="button"
        class="btn-refresh"
        @click="emit('refresh')"
        :disabled="historyLoading"
      >
        {{ historyLoading ? 'Đang tải...' : 'Tải lại' }}
      </button>
    </div>
    <div class="history-filters">
      <div class="filter-group">
        <label>Sắp xếp</label>
        <select v-model="sortOption" class="filter-input">
          <option value="datetime">Thời gian (mới nhất)</option>
          <option value="code">Mã vận đơn (A-Z)</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Mã vận đơn</label>
        <input
          v-model="filterOrderCode"
          type="text"
          class="filter-input"
          placeholder="Nhập mã đơn"
        />
      </div>
      <div class="filter-group">
        <label>Mã sản phẩm</label>
        <input
          v-model="filterBarcode"
          type="text"
          class="filter-input"
          placeholder="Barcode trong đơn"
        />
      </div>
      <div class="filter-group">
        <label>Từ ngày</label>
        <input v-model="filterDateFrom" type="date" class="filter-input" />
      </div>
      <div class="filter-group">
        <label>Đến ngày</label>
        <input v-model="filterDateTo" type="date" class="filter-input" />
      </div>
      <div class="filter-actions">
        <button type="button" class="btn-secondary small" @click="clearFilters">Xóa lọc</button>
      </div>
    </div>

    <div v-if="historyLoading" class="history-empty">Đang tải dữ liệu đơn hàng...</div>
    <div v-else-if="sortedOrders.length === 0" class="history-empty">
      Chưa có đơn hàng nào được tạo.
    </div>
    <div v-else class="history-list">
      <div
        class="history-card"
        v-for="order in sortedOrders"
        :key="order.order_code"
        v-memo="[
          order.order_code,
          order.customer_name,
          order.package_date,
          order.total_cost,
          isOrderExpanded(order.order_code),
          isReturning(order.order_code),
          isReturned(order.order_code),
          orderProducts(order.order_code).length,
        ]"
      >
        <div class="history-card-main">
          <div class="history-card-info">
            <div class="history-order-code">{{ order.order_code || '(Không mã)' }}</div>
            <div class="history-info-row">
              <span>Khách: <strong>{{ order.customer_name || 'N/A' }}</strong></span>
              <span>Ngày đóng gói: {{ formatDateTimeDisplay(order.package_date) }}</span>
              <span>Tổng chi phí: {{ formatNumber(order.total_cost) }} VND</span>
            </div>
          </div>
          <div class="history-actions">
            <button
              type="button"
              class="btn-return"
              :disabled="isReturning(order.order_code) || isReturned(order.order_code) || orderProducts(order.order_code).length === 0"
              @click="emit('return-order', order.order_code)"
            >
              {{
                isReturned(order.order_code)
                  ? 'Đã trả'
                  : isReturning(order.order_code)
                    ? 'Đang trả...'
                    : 'Trả hàng'
              }}
            </button>
            <button
              type="button"
              class="btn-toggle"
              @click="emit('toggle-order', order.order_code)"
            >
              {{ isOrderExpanded(order.order_code) ? 'Thu gọn' : 'Xem sản phẩm' }}
            </button>
          </div>
        </div>

        <transition name="fade">
          <div v-if="isOrderExpanded(order.order_code)" class="history-details">
            <div v-if="orderProducts(order.order_code).length === 0" class="history-empty-products">
              Chưa có sản phẩm nào được ghi lại cho đơn này.
            </div>
            <div v-else class="history-products">
              <div
                class="history-product"
                v-for="item in orderProducts(order.order_code)"
                :key="`${order.order_code}-${item.productID}-${item.barcode}`"
              >
                <div class="history-product-main">
                  <div class="history-product-name">{{ item.name }}</div>
                  <div class="history-product-meta">
                    Barcode: {{ item.barcode }} | Thương hiệu: {{ item.brand }} | Danh mục:
                    {{ item.category }}
                  </div>
                </div>
                <div class="history-product-qty">
                  {{ item.qty_sold }} x {{ formatNumber(item.unit_cost) }} VND
                </div>
                <div class="history-product-total">{{ formatNumber(item.total_cost) }} VND</div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  historyLoading: { type: Boolean, default: false },
  orderHistory: { type: Array, default: () => [] },
  expandedOrders: { type: Object, default: () => new Set() },
  returningOrders: { type: Object, default: () => new Set() },
  returnedOrders: { type: Object, default: () => new Set() },
  orderProducts: { type: Function, required: true },
});

const emit = defineEmits(['refresh', 'toggle-order', 'return-order']);

const filterOrderCode = ref('');
const filterBarcode = ref('');
const filterDateFrom = ref('');
const filterDateTo = ref('');
const sortOption = ref('datetime');

const orderProducts = (orderCode) => props.orderProducts(orderCode);

function clearFilters() {
  filterOrderCode.value = '';
  filterBarcode.value = '';
  filterDateFrom.value = '';
  filterDateTo.value = '';
}

const filteredOrders = computed(() => {
  const code = (filterOrderCode.value || '').toLowerCase();
  const barcode = (filterBarcode.value || '').toLowerCase();
  const from = filterDateFrom.value ? Date.parse(filterDateFrom.value) : null;
  const to = filterDateTo.value ? Date.parse(filterDateTo.value) : null;

  return (props.orderHistory || []).filter((o) => {
    if (code && !(o.order_code || '').toLowerCase().includes(code)) return false;

    if (from || to) {
      const pkgDate = Date.parse(o.package_date);
      if (Number.isNaN(pkgDate)) return false;
      if (from && pkgDate < from) return false;
      if (to && pkgDate > to) return false;
    }

    if (barcode) {
      const items = orderProducts(o.order_code);
      const match = items.some((it) =>
        String(it.barcode || '').toLowerCase().includes(barcode),
      );
      if (!match) return false;
    }
    return true;
  });
});

function parseDateTimeValue(value) {
  const raw = String(value || '').trim();
  if (!raw) return { timestamp: NaN, hasTime: false, day: NaN };
  const timestamp = Date.parse(raw);
  const hasTime = /T\\d{2}:\\d{2}/.test(raw) || /\\d{1,2}:\\d{2}/.test(raw);
  if (Number.isNaN(timestamp)) {
    return { timestamp: NaN, hasTime, day: NaN };
  }
  const dt = new Date(timestamp);
  const day = new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()).getTime();
  return { timestamp, hasTime, day };
}

function compareOrdersByDateTime(a, b) {
  const pa = parseDateTimeValue(a?.package_date);
  const pb = parseDateTimeValue(b?.package_date);

  if (!Number.isNaN(pb.day) || !Number.isNaN(pa.day)) {
    if (Number.isNaN(pa.day)) return 1;
    if (Number.isNaN(pb.day)) return -1;
    if (pa.day !== pb.day) return pb.day - pa.day;
  }

  if (pa.hasTime && !pb.hasTime) return -1;
  if (!pa.hasTime && pb.hasTime) return 1;

  if (!Number.isNaN(pa.timestamp) || !Number.isNaN(pb.timestamp)) {
    if (Number.isNaN(pa.timestamp)) return 1;
    if (Number.isNaN(pb.timestamp)) return -1;
    return pb.timestamp - pa.timestamp;
  }

  return 0;
}

const sortedOrders = computed(() => {
  const list = [...filteredOrders.value];
  if (sortOption.value === 'code') {
    return list.sort((a, b) => String(a.order_code || '').localeCompare(String(b.order_code || '')));
  }
  return list.sort(compareOrdersByDateTime);
});

function isOrderExpanded(orderCode) {
  return props.expandedOrders?.has(orderCode);
}

function isReturning(orderCode) {
  return props.returningOrders?.has(orderCode);
}

function isReturned(orderCode) {
  return props.returnedOrders?.has(orderCode);
}

function formatDateTimeDisplay(value) {
  const ts = Date.parse(value);
  if (Number.isNaN(ts)) return value || 'N/A';
  return new Date(ts).toLocaleString('vi-VN', {
    hour12: false,
  });
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}
</script>

<style scoped>
.history-section {
  margin-top: 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 16px;
}

.history-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 13px;
  color: #4b5563;
}

.filter-input {
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-secondary {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  background: #f3f4f6;
  border: 1px solid #ddd;
  color: #555;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary.small {
  padding: 8px 10px;
  font-size: 13px;
}

.btn-refresh {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #cbd5f5;
  background: #eef2ff;
  color: #3730a3;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-refresh:not(:disabled):hover {
  background: #dbe4ff;
}

.history-empty {
  padding: 24px;
  text-align: center;
  color: #6b7280;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  background: #f9fafb;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
}

.history-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
  background: #fdfdfc;
}

.history-card-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.history-card-info {
  flex: 1;
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-order-code {
  font-size: 18px;
  font-weight: 700;
  color: #14532d;
}

.history-info-row {
  margin-top: 6px;
  font-size: 13px;
  color: #4b5563;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn-return {
  border: 1px solid #fcd34d;
  background: #fef3c7;
  color: #92400e;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-return:hover:not(:disabled) {
  background: #fde68a;
}

.btn-return:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-toggle {
  border: none;
  background: #86c06b;
  color: white;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-toggle:hover {
  background: #6db046;
}

.history-details {
  margin-top: 12px;
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.history-products {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-product {
  display: grid;
  grid-template-columns: 2fr 1fr 100px;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.history-product-name {
  font-weight: 600;
  color: #1f2937;
}

.history-product-meta {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.history-product-qty,
.history-product-total {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.history-empty-products {
  padding: 12px;
  background: #fef3c7;
  border: 1px dashed #fcd34d;
  color: #92400e;
  border-radius: 8px;
  font-size: 13px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .history-card-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .history-product {
    grid-template-columns: 1fr;
  }

  .history-info-row {
    flex-direction: column;
    gap: 6px;
  }
}
</style>
