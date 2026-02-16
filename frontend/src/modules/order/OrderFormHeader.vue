<template>
  <div class="form-group">
    <label for="customerName">Tên Khách Hàng</label>
    <input
      v-model="CustomerName"
      type="text"
      id="customerName"
      placeholder="Tên khách hàng"
      class="input-field"
      @input="emitCustomerNameChange"
    />
  </div>

  <div class="form-group">
    <label for="orderCode">Mã Vận Đơn</label>
    <div class="input-with-action input-with-action--double">
      <input
        v-model="OrderCode"
        type="text"
        id="orderCode"
        placeholder="Để trống để tự sinh"
        ref="orderCodeRef"
        @keyup.enter="handleOrderCodeEnter"
        @focus="emitOrderCodeFocus"
        :disabled="isExternalOrder"
        class="input-field"
      />
      <button
        type="button"
        class="btn-scan"
        @click="emitStartScanner"
        :disabled="isScanningOrderCode || isExternalOrder"
      >
        📷
      </button>
      <button
        type="button"
        class="btn-secondary btn-auto-scan"
        @click="toggleOrderCodeAutoScan"
        :disabled="isExternalOrder"
        :class="{ 'btn-active': autoScanOrderCode }"
      >
        {{ autoScanOrderCode ? 'ON' : 'OFF' }}
      </button>
      <button
        type="button"
        class="btn-secondary"
        @click="toggleExternalOrder"
        :class="{ 'btn-active': isExternalOrder }"
        title="Bật để tạo đơn ngoài (auto-generate mã vận đơn)"
      >
        {{ isExternalOrder ? 'ĐƠN NGOÀI' : 'SHOPEE' }}
      </button>
    </div>
  </div>

  <div class="form-group">
    <label for="packageDate">Ngày giờ</label>
    <div class="input-with-action">
      <button
        type="button"
        class="btn-secondary"
        :class="{ 'btn-active': packageDateMode === 'now' }"
        @click="setPackageDateNow"
      >
        Hiện tại
      </button>
      <button
        type="button"
        class="btn-secondary"
        :class="{ 'btn-active': packageDateMode === 'custom' }"
        @click="togglePackageDatePicker"
      >
        {{ showPackageDatePicker ? 'Ẩn chọn ngày' : 'Chọn ngày' }}
      </button>
    </div>
    <input
      v-if="showPackageDatePicker"
      v-model="PackageDate"
      type="datetime-local"
      id="packageDate"
      required
      @input="emitPackageDateChange"
      class="input-field"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { PropType } from 'vue'
const props = defineProps({
  customerName: String,
  orderCode: String,
  packageDate: String,
  autoScanOrderCode: Boolean,
  isExternalOrder: Boolean,
  isScanningOrderCode: Boolean,

  orderHistory: {
    type: Array as PropType<{
      orderID: string
      customer_name: string
      order_code: string
      package_date: string
      total_cost: number
      note: string
      rowIndex: number
    }[]>,
    default: () => []
  }
});

const emit = defineEmits([
  'update:customerName',
  'update:orderCode',
  'update:packageDate',
  'update:isExternalOrder',
  'showMessage',
  'focusProductBarcode',
  'stopOrderCodeScanner',
  'startOrderCodeScanner',  
  'orderCodeFocus',
  'startScanner',

]);

const CustomerName = ref(props.customerName || '');
const OrderCode = ref(props.orderCode || '');

const PackageDate = ref(props.packageDate || '');
const showPackageDatePicker = ref(false)
const packageDateMode = ref('now');

const autoScanOrderCode = ref(props.autoScanOrderCode || false)

const isExternalOrder = ref(props.isExternalOrder || false)

const orderCodeRef = ref(null)
watch(() => props.customerName, (newVal) => {
  CustomerName.value = newVal || '';
});

watch(() => props.orderCode, (newVal) => {
  OrderCode.value = newVal || '';
});

watch(() => props.packageDate, (newVal) => {
  PackageDate.value = newVal || '';
});

const emitCustomerNameChange = () => {
  emit('update:customerName', CustomerName.value);
};

const emitOrderCodeChange = () => {
  emit('update:orderCode', OrderCode.value);
};

const emitPackageDateChange = () => {
  emit('update:packageDate', PackageDate.value);
};

const emitIsExternalOrderChange = () => {
  emit('update:isExternalOrder');
}

const emitShowMessage = (text : String,type : String) => {
  emit("showMessage",text,type)
}

const emitFocusProductBarcode = () => {
  emit('focusProductBarcode');
}

const handleOrderCodeEnter = () => {
  emitOrderCodeChange();
  const code = (OrderCode.value || '').trim();
  if (!code) return;

  const exists = (props.orderHistory || []).some(
    (o) => String(o.order_code || '').toLowerCase() === code.toLowerCase(),
  );
  if (exists) {
    emitShowMessage('Mã vận đơn đã tồn tại', 'error');
    OrderCode.value = "";
    return;
  }
  emitFocusProductBarcode();
};

const emitOrderCodeFocus = () => {
  emit('orderCodeFocus');
};

const emitStartScanner = () => {
  emit('startScanner');
};

const emitStopOrderCodeScanner = () => {
  emit('stopOrderCodeScanner');
}

const emitStartOrderCodeScanner = () => {
  emit('startOrderCodeScanner');
}

function toggleOrderCodeAutoScan() {
  autoScanOrderCode.value = !autoScanOrderCode.value;
  if (!autoScanOrderCode.value) {
    emitStopOrderCodeScanner();
    return;
  }
  if (orderCodeRef.value && document.activeElement === orderCodeRef.value) {
    emitStartOrderCodeScanner();
  }
}

function toggleExternalOrder() {
  isExternalOrder.value = !isExternalOrder.value;
  emitIsExternalOrderChange();
  if (isExternalOrder.value) {
    // Tắt quét tự động khi bật chế độ đơn ngoài
    autoScanOrderCode.value = false;
    emitStopOrderCodeScanner();
    OrderCode.value = "";
    emitOrderCodeChange();
  }
}

function getLocalDateTimeString(date = new Date()) {
  const tzOffset = date.getTimezoneOffset() * 60000;
  const localISO = new Date(date.getTime() - tzOffset).toISOString();
  return localISO.slice(0, 16);
}

function setPackageDateNow() {
  PackageDate.value = getLocalDateTimeString();
  packageDateMode.value = 'now';
  showPackageDatePicker.value = false;
  emitPackageDateChange();
}

function togglePackageDatePicker() {
  showPackageDatePicker.value = !showPackageDatePicker.value;
  if (showPackageDatePicker.value) {
    packageDateMode.value = 'custom';
  }
}
</script>

<style scoped>
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

.input-with-action {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
}

.input-with-action--double {
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 6px;
}

.btn-scan {
  padding: 10px 8px;
  border: 1px solid #86c06b;
  background: #ecfdf3;
  color: #166534;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-scan:hover:not(:disabled) {
  background: #d1f7df;
}

.btn-scan:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 12px 16px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  color: #555;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.input-with-action--double .btn-secondary {
  padding: 10px 8px;
  font-size: 14px;
}

.btn-secondary.btn-active {
  background: #d1f7df;
  border-color: #86c06b;
  color: #166534;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
