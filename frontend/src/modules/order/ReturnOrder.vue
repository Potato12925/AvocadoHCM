<template>
  <div class="return-container">
    <h2>Quét mã đơn để trả hàng</h2>

    <!-- Vùng nhập + quét -->
    <div class="scan-wrapper">
      <!-- Input -->
      <div style="display: flex; flex-direction: column;">
        <input
          ref="scanInputRef"
          v-model="scanCode"
          @keyup.enter="handleScan"
          placeholder="Quét hoặc nhập mã đơn..."
          class="scan-input"
        />
        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>
      </div>
      <!-- QR Scanner -->
      <QRScanner
        v-model:text="scanCode"
        class="qr-btn"
        @scanned="handleScan"
      />
    </div>

    <!-- Danh sách đã quét -->
    <OrderCard
      v-for="order in scannedOrders"
      :key="order.order_code"
      :order="order"
    >
      <template #actions>
        <button
          class="remove-btn"
          @click="removeOrder(order.order_code)"
        >
          ✕
        </button>
      </template>
    </OrderCard>

    <!-- Nút trả toàn bộ -->
    <button
      v-if="scannedOrders.length > 0"
      class="return-all-btn"
      @click="returnFullOrder"
    >
      Trả toàn bộ {{ scannedOrders.length }} đơn
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import OrderCard from '@/modules/order/OrderCard.vue'
import QRScanner from '@/modules/shared/QRScanner.vue'
const props = defineProps({
  orders: Array,
  orderProductsMap: Object,
  onReturn: Function
})

const scanCode = ref('')
const scanInputRef = ref(null)
const scannedOrders = ref([])
const errorMessage = ref('')
let errorTimeout = null
function buildOrder(order) {
  return {
    ...order,
    products:
      props.orderProductsMap?.[order.order_code] || []
  }
}
function focusOrderCode(){
  if (scanInputRef.value){
    scanInputRef.value.focus()
  }
}
function showError(message) {
  errorMessage.value = message

  if (errorTimeout) {
    clearTimeout(errorTimeout)
  }

  errorTimeout = setTimeout(() => {
    errorMessage.value = ''
  }, 3000) // 3 giây tự tắt
}
function handleScan() {
  const code = scanCode.value.trim()
  if (!code) return

  const found = props.orders.find(
    o => o.order_code === code
  )

  if (found) {
    if (!scannedOrders.value.some(o => o.order_code === code)) {
      scannedOrders.value.push(buildOrder(found))
      focusOrderCode()
    }
  } else {
    showError('Không tìm thấy đơn hàng')
  }

  scanCode.value = ''
}

function removeOrder(orderCode) {
  scannedOrders.value = scannedOrders.value.filter(
    o => o.order_code !== orderCode
  )
}

function returnFullOrder() {
  if (!scannedOrders.value.length) return

  const orderCodes = scannedOrders.value.map(
    o => o.order_code
  )

  if (props.onReturn) {
    props.onReturn(orderCodes)
  }

  scannedOrders.value = []
}
</script>

<style scoped>
.return-container {
  max-width: 800px;
}
.return-container h2 {
  text-align: left;
  margin-bottom: 20px;
  color: #14532d;
  font-weight: 700;
  letter-spacing: 1px;
}
.scan-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}
.scan-input {
  flex: 1;
  padding: 10px;
  font-size: 15px;
  border-radius: 8px;
  border: 1px solid #86c06b;
  outline: none;

}
.scan-input:focus {
  border-color: #14532d;
  box-shadow: 0 0 0 2px rgba(134, 192, 107, 0.3);
}

.qr-btn {
  flex-shrink: 0;
}
.order-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: #fafafa;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.remove-btn {
  background: #ff4d4f;
  border: none;
  color: white;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
}

.remove-btn:hover {
  background: #d9363e;
}

.product-row {
  padding: 8px 0;
  border-top: 1px dashed #ddd;
}

.product-name {
  font-weight: 600;
}

.product-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #555;
}

.return-all-btn {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  background: #86c06b;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.return-all-btn:hover {
  background: #1677cc;
}
.error-message {
  color: #ff4d4f;
  font-size: 14px;
  margin-top: 6px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0 }
  to { opacity: 1 }
}
</style>