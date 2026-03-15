<template>
  <div class="form-group">
    <label for="customerName">Tên Khách Hàng</label>
    <input
      v-model="localCustomerName"
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
        v-model="localOrderCode"
        type="text"
        id="orderCode"
        placeholder="Để trống để tự sinh"
        ref="orderCodeInputRef"
        @input="emitOrderCodeChange"
        @keyup.enter="emitOrderCodeEnter"
        @focus="emitOrderCodeFocus"
        :disabled="isExternalOrder"
        class="input-field"
      />
      <QRScanner
        ref="qrScannerRef"
        v-model:text="localOrderCode"
        class="btn-scan"
        :disabled="isExternalOrder"
        @scanned="handleScannerScanned"
      />
      <button
        type="button"
        class="btn-secondary btn-auto-scan"
        @click="emitToggleAutoScan"
        :disabled="isExternalOrder"
        :class="{ 'btn-active': autoScanOrderCode }"
      >
        {{ autoScanOrderCode ? 'ON' : 'OFF' }}
      </button>
      <button
        type="button"
        class="btn-secondary"
        @click="emitToggleExternalOrder"
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
        @click="emitSetPackageDateNow"
      >
        Hiện tại
      </button>
      <button
        type="button"
        class="btn-secondary"
        :class="{ 'btn-active': packageDateMode === 'custom' }"
        @click="emitTogglePackageDatePicker"
      >
        {{ showPackageDatePicker ? 'Ẩn chọn ngày' : 'Chọn ngày' }}
      </button>
    </div>
    <input
      v-if="showPackageDatePicker"
      v-model="localPackageDate"
      type="datetime-local"
      id="packageDate"
      required
      @input="emitPackageDateChange"
      class="input-field"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import QRScanner from '@/modules/shared/QRScanner.vue';

const props = defineProps({
  customerName: String,
  orderCode: String,
  packageDate: String,
  isExternalOrder: Boolean,
  orderHistory: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits([
  'update:customerName',
  'update:orderCode',
  'update:packageDate',
  'update:isExternalOrder',
  'focusBarcode',
  'orderCodeDuplicate',
]);

const localCustomerName = ref(props.customerName || '');
const localOrderCode = ref(props.orderCode || '');
const localPackageDate = ref(props.packageDate || '');
const qrScannerRef = ref(null);
const orderCodeInputRef = ref(null);
const showPackageDatePicker = ref(false);
const packageDateMode = ref('now');
const autoScanOrderCode = ref(false);

watch(() => props.customerName, (newVal) => {
  localCustomerName.value = newVal || '';
});

watch(() => props.orderCode, (newVal) => {
  localOrderCode.value = newVal || '';
});

watch(() => props.packageDate, (newVal) => {
  localPackageDate.value = newVal || '';
});

watch(() => props.isExternalOrder, (external) => {
  if (external) {
    autoScanOrderCode.value = false;
    localOrderCode.value = '';
    emit('update:orderCode', '');
    qrScannerRef.value?.stopScanner?.();
  }
});

watch(autoScanOrderCode, (enabled) => {
  const inputEl = orderCodeInputRef.value;
  if (enabled && inputEl && document.activeElement === inputEl && !props.isExternalOrder) {
    qrScannerRef.value?.startScanner?.();
  }
});

const emitCustomerNameChange = () => {
  emit('update:customerName', localCustomerName.value);
};

const emitOrderCodeChange = () => {
  emit('update:orderCode', localOrderCode.value);
};

const emitPackageDateChange = () => {
  emit('update:packageDate', localPackageDate.value);
};

const emitOrderCodeEnter = () => {
  emitOrderCodeChange();
  handleOrderCodeEnter();
};

const emitOrderCodeFocus = () => {
  if (autoScanOrderCode.value && !props.isExternalOrder) {
    qrScannerRef.value?.startScanner?.();
  }
};

const emitToggleAutoScan = () => {
  autoScanOrderCode.value = !autoScanOrderCode.value;
};

const emitToggleExternalOrder = () => {
  emit('update:isExternalOrder', !props.isExternalOrder);
};

const emitSetPackageDateNow = () => {
  localPackageDate.value = getLocalDateTimeString();
  packageDateMode.value = 'now';
  showPackageDatePicker.value = false;
  emitPackageDateChange();
};

const emitTogglePackageDatePicker = () => {
  showPackageDatePicker.value = !showPackageDatePicker.value;
  if (showPackageDatePicker.value) {
    packageDateMode.value = 'custom';
  }
};

const handleScannerScanned = () => {
  emitOrderCodeChange();
  handleOrderCodeEnter();
};

function handleOrderCodeEnter() {
  const code = String(localOrderCode.value || '').trim();
  if (!code) return;

  const exists = (props.orderHistory || []).some(
    (order) => String(order?.order_code || '').trim().toLowerCase() === code.toLowerCase(),
  );

  if (exists) {
    localOrderCode.value = '';
    emit('update:orderCode', '');
    emit('orderCodeDuplicate', 'Mã vận đơn đã tồn tại');
    return;
  }

  emit('focusBarcode');
}

function focusOrderCode() {
  orderCodeInputRef.value?.focus();
}

function resetHeaderState() {
  autoScanOrderCode.value = false;
  showPackageDatePicker.value = false;
  packageDateMode.value = 'now';
  qrScannerRef.value?.stopScanner?.();
}

function getLocalDateTimeString(date = new Date()) {
  const tzOffset = date.getTimezoneOffset() * 60000;
  const localISO = new Date(date.getTime() - tzOffset).toISOString();
  return localISO.slice(0, 16);
}

defineExpose({
  focusOrderCode,
  resetHeaderState,
});
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
  display: flex;
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
