<template>
  <div class="flex flex-col gap-1.5">
    <label for="customerName" class="text-sm font-medium text-gray-600">
      Tên Khách Hàng
    </label>
    <input
      v-model="localCustomerName"
      type="text"
      id="customerName"
      placeholder="Tên khách hàng"
      class="px-3 py-2.5 border border-gray-300 rounded-lg text-base transition focus:outline-none focus:border-green-400 focus:ring-4 focus:ring-green-200/40"
      @input="emitCustomerNameChange"
    />
  </div>

  <div class="flex flex-col gap-1.5">
    <label for="orderCode" class="text-sm font-medium text-gray-600">
      Mã Vận Đơn
    </label>

    <div class="grid grid-cols-[2fr_1fr_1fr_1fr] gap-1.5 items-center">
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
        class="px-3 py-2.5 border border-gray-300 rounded-lg text-base transition focus:outline-none focus:border-green-400 focus:ring-4 focus:ring-green-200/40 disabled:opacity-50 disabled:cursor-not-allowed"
      />

      <QRScanner
        ref="qrScannerRef"
        v-model:text="localOrderCode"
        class="flex"
        :disabled="isExternalOrder"
        @scanned="handleScannerScanned"
      />

      <button
        type="button"
        class="px-2 py-2.5 bg-gray-100 border border-gray-300 text-gray-600 rounded-lg text-sm font-semibold transition hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        :class="autoScanOrderCode ? 'bg-green-100 border-green-400 text-green-800' : ''"
        @click="emitToggleAutoScan"
        :disabled="isExternalOrder"
      >
        {{ autoScanOrderCode ? 'ON' : 'OFF' }}
      </button>

      <button
        type="button"
        class="px-2 py-2.5 bg-gray-100 border border-gray-300 text-gray-600 rounded-lg text-sm font-semibold transition hover:bg-gray-200"
        :class="isExternalOrder ? 'bg-green-100 border-green-400 text-green-800' : ''"
        @click="emitToggleExternalOrder"
        title="Bật để tạo đơn ngoài (auto-generate mã vận đơn)"
      >
        {{ isExternalOrder ? 'ĐƠN NGOÀI' : 'SHOPEE' }}
      </button>
    </div>
  </div>

  <div class="flex flex-col gap-1.5">
    <label for="packageDate" class="text-sm font-medium text-gray-600">
      Ngày giờ
    </label>

    <div class="grid grid-cols-[1fr_1fr] gap-2 items-center">
      <button
        type="button"
        class="px-4 py-2.5 bg-gray-100 border border-gray-300 text-gray-600 rounded-lg text-sm font-semibold transition hover:bg-gray-200"
        :class="packageDateMode === 'now' ? 'bg-green-100 border-green-400 text-green-800' : ''"
        @click="emitSetPackageDateNow"
      >
        Hiện tại
      </button>

      <button
        type="button"
        class="px-4 py-2.5 bg-gray-100 border border-gray-300 text-gray-600 rounded-lg text-sm font-semibold transition hover:bg-gray-200"
        :class="packageDateMode === 'custom' ? 'bg-green-100 border-green-400 text-green-800' : ''"
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
      class="px-3 py-2.5 border border-gray-300 rounded-lg text-base transition focus:outline-none focus:border-green-400 focus:ring-4 focus:ring-green-200/40"
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
  if ( autoScanOrderCode.value === true){
    QRScanner.value?.startScanner?.();
  }
}

function resetHeaderDate() {
  showPackageDatePicker.value = false;
  packageDateMode.value = 'now';
}

function getLocalDateTimeString(date = new Date()) {
  const tzOffset = date.getTimezoneOffset() * 60000;
  const localISO = new Date(date.getTime() - tzOffset).toISOString();
  return localISO.slice(0, 16);
}

defineExpose({
  focusOrderCode,
  resetHeaderDate,
});
</script>

