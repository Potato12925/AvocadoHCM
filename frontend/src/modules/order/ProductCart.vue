<template>
  <div>
    <h3 class="subsection-title">Thêm Sản Phẩm Vào Đơn</h3>

    <div class="form-group">
      <label for="barcodeInput">Quét/Nhập Barcode</label>
      <input
        v-model="barcodeModel"
        type="text"
        id="barcodeInput"
        placeholder="Nhập hoặc quét mã barcode"
        ref="localBarcodeInputRef"
        @keyup.enter="emitAddProductByBarcode"
        class="input-field"
      />
    </div>

    <div v-if="cartItems.length === 0" class="empty-cart">
      Chưa có sản phẩm nào trong đơn hàng
    </div>

    <div v-else class="cart-items">
      <CartItemRow
        v-for="(item, idx) in cartItems"
        :key="idx"
        :item="item"
        :index="idx"
        @decreaseQty="emitDecreaseQty"
        @increaseQty="emitIncreaseQty"
        @qtyChange="emitQtyChange"
        @remove="emitRemove"
      />

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
        @click="emitClearCart"
        class="btn-secondary"
        :disabled="cartItems.length === 0"
      >
        🗑 Xóa Hết
      </button>
      <button
        type="submit"
        class="btn-submit"
        :disabled="isLoading || cartItems.length === 0"
      >
        {{ isLoading ? 'Đang lưu...' : '✓ Hoàn Tất Đơn Hàng' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import CartItemRow from './CartItemRow.vue';

const props = defineProps({
  barcodeInput: String,
  cartItems: {
    type: Array,
    default: () => [],
  },
  isLoading: Boolean,
});

const emit = defineEmits([
  'update:barcodeInput',
  'addProductByBarcode',
  'decreaseQty',
  'increaseQty',
  'qtyChange',
  'removeItem',
  'clearCart',
  'submit',
]);

const localBarcodeInputRef = ref(null);

const barcodeModel = computed({
  get: () => props.barcodeInput || '',
  set: (value) => emit('update:barcodeInput', value),
});

function focusBarcodeInput() {
  localBarcodeInputRef.value?.focus();
}

defineExpose({
  focusBarcodeInput,
});

const totalCost = computed(() => {
  return props.cartItems.reduce((sum, item) => sum + itemTotalCost(item), 0);
});

function itemTotalCost(item) {
  if (!item || !Array.isArray(item.allocations)) return 0;
  return item.allocations.reduce((s, a) => s + (a.qty || 0) * (a.unit_cost || 0), 0);
}

const emitAddProductByBarcode = () => {
  emit('addProductByBarcode');
  barcodeModel.value = '';
};

const emitDecreaseQty = (idx) => {
  emit('decreaseQty', idx);
};

const emitIncreaseQty = (idx) => {
  emit('increaseQty', idx);
};

const emitQtyChange = (idx) => {
  emit('qtyChange', idx);
};

const emitRemove = (idx) => {
  emit('removeItem', idx);
};

const emitClearCart = () => {
  emit('clearCart');
};

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}
</script>

<style scoped>
.subsection-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d5016;
  margin: 20px 0 12px 0;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
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
</style>
