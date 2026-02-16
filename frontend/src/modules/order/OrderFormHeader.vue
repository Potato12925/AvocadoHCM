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
        ref="orderCodeRef"
        @keyup.enter="emitOrderCodeEnter"
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

const props = defineProps({
  customerName: String,
  orderCode: String,
  packageDate: String,
  showPackageDatePicker: Boolean,
  packageDateMode: String,
  autoScanOrderCode: Boolean,
  isExternalOrder: Boolean,
  isScanningOrderCode: Boolean,
  orderCodeRef: Object,
});

const emit = defineEmits([
  'update:customerName',
  'update:orderCode',
  'update:packageDate',
  'orderCodeEnter',
  'orderCodeFocus',
  'startScanner',
  'toggleAutoScan',
  'toggleExternalOrder',
  'setPackageDateNow',
  'togglePackageDatePicker',
]);

const localCustomerName = ref(props.customerName || '');
const localOrderCode = ref(props.orderCode || '');
const localPackageDate = ref(props.packageDate || '');

watch(() => props.customerName, (newVal) => {
  localCustomerName.value = newVal || '';
});

watch(() => props.orderCode, (newVal) => {
  localOrderCode.value = newVal || '';
});

watch(() => props.packageDate, (newVal) => {
  localPackageDate.value = newVal || '';
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
  emit('orderCodeEnter');
};

const emitOrderCodeFocus = () => {
  emit('orderCodeFocus');
};

const emitStartScanner = () => {
  emit('startScanner');
};

const emitToggleAutoScan = () => {
  emit('toggleAutoScan');
};

const emitToggleExternalOrder = () => {
  emit('toggleExternalOrder');
};

const emitSetPackageDateNow = () => {
  emit('setPackageDateNow');
};

const emitTogglePackageDatePicker = () => {
  emit('togglePackageDatePicker');
};
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
