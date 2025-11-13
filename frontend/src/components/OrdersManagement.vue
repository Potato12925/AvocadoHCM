<template>
  <div class="orders-container">
    <h1 class="page-title">🛒 Tạo Đơn Hàng</h1>

    <!-- Form Tạo Đơn Hàng -->
    <div class="form-section">
      <h2 class="section-title">Thông Tin Đơn Hàng</h2>
      <form @submit.prevent="submitOrder" @keydown.enter.prevent class="order-form">
        <div class="form-row">
          <div class="form-group">
            <label for="customerName">Tên Khách Hàng</label>
            <input
              v-model="orderForm.customer_name"
              type="text"
              id="customerName"
              placeholder="Tên khách hàng"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label for="orderCode">Mã Đơn Hàng</label>
            <input
              v-model="orderForm.order_code"
              type="text"
              id="orderCode"
              placeholder="Để trống để tự sinh"
              class="input-field"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="packageDate">Ngày Đóng Gói</label>
          <input
            v-model="orderForm.package_date"
            type="date"
            id="packageDate"
            required
            class="input-field"
          />
        </div>

        <h3 class="subsection-title">Thêm Sản Phẩm Vào Đơn</h3>

        <div class="form-group">
          <label for="barcodeInput">Quét/Nhập Barcode</label>
          <input
            v-model="barcodeInput"
            type="text"
            id="barcodeInput"
            placeholder="Nhập hoặc quét mã barcode"
            @keyup.enter="addProductByBarcode"
            class="input-field"
          />
        </div>

        <div v-if="cartItems.length === 0" class="empty-cart">
          Chưa có sản phẩm nào trong đơn hàng
        </div>

        <div v-else class="cart-items">
          <div class="cart-item" v-for="(item, idx) in cartItems" :key="idx">
            <div class="item-info">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-details">
                {{ item.barcode }} | {{ item.brand }} | {{ item.category }}
              </div>
              <div class="item-available">Tồn: {{ item.available_total }}</div>
              <div class="item-chips">
                <span
                  v-for="al in item.allocations"
                  :key="al.productID"
                  class="chip chip-alloc"
                >
                  {{ al.qty }} × {{ formatNumber(al.unit_cost) }}₫ (ID {{ al.productID }})
                </span>
              </div>
              <div class="item-cost">Tổng giá vốn: {{ formatNumber(itemTotalCost(item)) }}₫</div>
            </div>

            <div class="item-qty">
              <button
                type="button"
                @click="decreaseQty(idx)"
                class="btn-qty"
                :disabled="item.qty_sold <= 1"
              >
                −
              </button>
              <input
                v-model.number="item.qty_sold"
                type="number"
                min="1"
                :max="item.available_total"
                @change="refreshAllocationsForIndex(idx)"
                class="qty-input"
              />
              <button
                type="button"
                @click="increaseQty(idx)"
                class="btn-qty"
                :disabled="item.qty_sold >= item.available_total"
              >
                +
              </button>
            </div>

            <div class="item-total">
              {{ formatNumber(itemTotalCost(item)) }}₫
            </div>

            <button
              type="button"
              @click="removeItem(idx)"
              class="btn-remove"
            >
              ✕
            </button>
          </div>

          <div class="order-summary">
            <div class="summary-row">
              <span class="summary-label">Tổng Chi Phí:</span>
              <span class="summary-value">{{ formatNumber(totalCost) }}₫</span>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button
            type="button"
            @click="clearCart"
            class="btn-secondary"
            :disabled="cartItems.length === 0"
          >
            🗑 Xóa Hết
          </button>
          <button
            type="submit"
            class="btn-submit"
            :disabled="loading || cartItems.length === 0"
          >
            {{ loading ? 'Đang lưu...' : '✓ Hoàn Tất Đơn Hàng' }}
          </button>
        </div>
      </form>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { importsAPI, ordersAPI, soldAPI } from '../services/api';
import { generateUniqueId } from '../services/api';

const orderForm = ref({
  customer_name: '',
  order_code: '',
  package_date: new Date().toISOString().split('T')[0],
});

const barcodeInput = ref('');
const cartItems = ref([]);
const imports = ref([]);
const loading = ref(false);
const message = ref(null);

function itemTotalCost(item) {
  if (!item || !Array.isArray(item.allocations)) return 0;
  return item.allocations.reduce((s, a) => s + (a.qty || 0) * (a.unit_cost || 0), 0);
}

const totalCost = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + itemTotalCost(item), 0);
});

async function loadImports() {
  try {
    const result = await importsAPI.getAll();
    imports.value = result.data || [];
  } catch (error) {
    console.error('Error loading imports:', error);
  }
}

function getBatchesForBarcode(barcode) {
  const batches = [];
  for (const row of imports.value || []) {
    if (String(row?.[1] || '') !== String(barcode)) continue;
    const available = parseInt(row?.[11]) || 0;
    const unitCost = Number(row?.[6]) || 0;
    const productID = row?.[0];
    batches.push({ row, productID, unitCost, available });
  }
  // Sort by unit cost desc (highest first)
  batches.sort((a, b) => b.unitCost - a.unitCost);
  return batches;
}

function computeAllocations(barcode, desiredQty) {
  const batches = getBatchesForBarcode(barcode);
  const totalAvailable = batches.reduce((s, b) => s + Math.max(0, b.available), 0);
  const target = Math.max(0, Math.min(desiredQty, totalAvailable));
  let remaining = target;
  const allocations = [];
  for (const b of batches) {
    if (remaining <= 0) break;
    const take = Math.min(b.available, remaining);
    if (take > 0) {
      allocations.push({ productID: b.productID, unit_cost: b.unitCost, qty: take });
      remaining -= take;
    }
  }
  return { allocations, totalAvailable, finalQty: target };
}

function addProductByBarcode() {
  if (!barcodeInput.value.trim()) return;

  const barcode = barcodeInput.value.trim();
  const batches = getBatchesForBarcode(barcode);
  if (batches.length === 0) {
    showMessage('Không tìm thấy sản phẩm với mã barcode này', 'error');
    barcodeInput.value = '';
    return;
  }

  const totalAvailable = batches.reduce((s, b) => s + Math.max(0, b.available), 0);
  if (totalAvailable <= 0) {
    showMessage('Sản phẩm đã hết hàng', 'error');
    barcodeInput.value = '';
    return;
  }

  const existingIdx = cartItems.value.findIndex((ci) => String(ci.barcode) === barcode);
  if (existingIdx === -1) {
    const top = batches[0];
    const brand = top?.row?.[2] || '';
    const name = top?.row?.[3] || '';
    const category = top?.row?.[4] || '';
    // Start with qty 1
    const { allocations, totalAvailable: avail, finalQty } = computeAllocations(barcode, 1);
    cartItems.value.push({
      barcode,
      brand,
      name,
      category,
      qty_sold: finalQty,
      available_total: avail,
      allocations,
    });
  } else {
    const current = cartItems.value[existingIdx];
    const desired = Math.min((current.qty_sold || 0) + 1, totalAvailable);
    const { allocations, totalAvailable: avail, finalQty } = computeAllocations(barcode, desired);
    current.qty_sold = finalQty;
    current.available_total = avail;
    current.allocations = allocations;
  }

  barcodeInput.value = '';
}

function refreshAllocationsForIndex(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  const desired = Math.max(1, Number(item.qty_sold || 1));
  const { allocations, totalAvailable, finalQty } = computeAllocations(item.barcode, desired);
  item.available_total = totalAvailable;
  item.qty_sold = finalQty;
  item.allocations = allocations;
}

function increaseQty(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  if ((item.qty_sold || 0) < (item.available_total || 0)) {
    item.qty_sold = (item.qty_sold || 0) + 1;
    refreshAllocationsForIndex(idx);
  }
}

function decreaseQty(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  if ((item.qty_sold || 0) > 1) {
    item.qty_sold = (item.qty_sold || 0) - 1;
    refreshAllocationsForIndex(idx);
  }
}

function removeItem(idx) {
  cartItems.value.splice(idx, 1);
}

function clearCart() {
  if (confirm('Bạn chắc chắn muốn xóa hết sản phẩm?')) {
    cartItems.value = [];
  }
}

async function submitOrder() {
  if (cartItems.value.length === 0) {
    showMessage('Vui lòng thêm sản phẩm vào đơn hàng', 'error');
    return;
  }

  loading.value = true;
  try {
    const orderID = generateUniqueId();
    const orderCode = orderForm.value.order_code || `ORD-${Date.now()}`;

    // Ghi đơn hàng
    await ordersAPI.create({
      orderID,
      customer_name: orderForm.value.customer_name,
      order_code: orderCode,
      package_date: orderForm.value.package_date,
      total_cost: totalCost.value,
      note: '',
    });

    // Ghi chi tiết sản phẩm đã bán theo phân bổ
    const updates = [];
    for (const item of cartItems.value) {
      for (const al of item.allocations || []) {
        if (!al || !al.qty) continue;
        await soldAPI.create({
          orderID,
          productID: al.productID,
          barcode: item.barcode,
          brand: item.brand,
          name: item.name,
          category: item.category,
          qty_sold: al.qty,
          unit_cost: al.unit_cost,
          total_cost: al.qty * al.unit_cost,
        });

        const importRowData = imports.value.find((imp) => imp[0] === al.productID);
        if (importRowData) {
          const rowIndex = imports.value.indexOf(importRowData) + 2; // 1-based, +1 for header
          const currentQtySold = parseInt(importRowData[10]) || 0;
          const newQtySold = currentQtySold + al.qty;
          const newAvailableQty = parseInt(importRowData[5]) - newQtySold;
          updates.push({
            row: rowIndex,
            data: { qty_sold: newQtySold, available_qty: newAvailableQty },
          });
        }
      }
    }

    if (updates.length > 0) {
      await importsAPI.updateRows(updates);
    }

    showMessage(`Tạo đơn hàng thành công! Mã: ${orderCode}`, 'success');
    orderForm.value = {
      customer_name: '',
      order_code: '',
      package_date: new Date().toISOString().split('T')[0],
    };
    cartItems.value = [];
  } catch (error) {
    showMessage('Lỗi: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

function showMessage(text, type) {
  message.value = { text, type };
  setTimeout(() => {
    message.value = null;
  }, 4000);
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}

onMounted(() => {
  loadImports();
});
</script>

<style scoped>
.orders-container {
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

.form-section {
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

.subsection-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d5016;
  margin: 20px 0 12px 0;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.order-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.input-field {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: #86c06b;
  box-shadow: 0 0 0 3px rgba(134, 192, 107, 0.1);
}

.empty-cart {
  padding: 24px;
  text-align: center;
  color: #999;
  font-size: 15px;
  background: #fafaf9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  background: #fafaf9;
  border-radius: 8px;
  border: 1px solid #eee;
}

.cart-item {
  display: grid;
  grid-template-columns: 1fr 120px 100px 40px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #eee;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-name {
  font-weight: 600;
  color: #2d5016;
  font-size: 16px;
}

.item-details {
  font-size: 13px;
  color: #666;
}

.item-available {
  font-size: 13px;
  color: #374151;
}

.item-cost {
  font-size: 13px;
  color: #86c06b;
  font-weight: 500;
}

/* Chips to indicate batch/product and unit cost */
.item-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 12px;
  border: 1px solid transparent;
}

.chip-id {
  background: #eef2ff;
  color: #3730a3;
  border-color: #c7d2fe;
}

.chip-cost {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

.chip-alloc {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

.item-qty {
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 4px;
}

.btn-qty {
  padding: 4px 6px;
  background: #f3f4f6;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-qty:hover:not(:disabled) {
  background: #86c06b;
  color: white;
}

.btn-qty:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.qty-input {
  flex: 1;
  border: none;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  padding: 4px;
}

.qty-input::-webkit-outer-spin-button,
.qty-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.qty-input[type='number'] {
  -moz-appearance: textfield;
}

.item-total {
  text-align: right;
  font-weight: 600;
  color: #2d5016;
  font-size: 16px;
}

.btn-remove {
  padding: 4px 8px;
  background: #fee2e2;
  color: #991b1b;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #fecaca;
}

.order-summary {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 2px solid #eee;
}

.summary-row {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #2d5016;
}

.summary-label {
  color: #666;
}

.summary-value {
  color: #86c06b;
  font-size: 17px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-submit,
.btn-secondary {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-submit {
  background: linear-gradient(135deg, #86c06b 0%, #6db046 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(134, 192, 107, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
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

.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
  font-size: 14px;
  font-weight: 500;
}

.message.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .cart-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .item-qty {
    width: 100%;
  }

  .item-total {
    text-align: left;
  }
}

@media (max-width: 640px) {
  .orders-container {
    padding: 12px;
  }

  .cart-item {
    grid-template-columns: 1fr;
  }
}
</style>
