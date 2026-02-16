<template>
  <div class="return-container">
    <div class="return-btn-wrap">
      <div class="return-title">Chế độ quét trả hàng</div>
      <div>
        <button
          :class="['toggle-btn', { off: !isActive }]"
          @click="emitToggle"
        >
          {{ isActive ? 'Bật' : 'Tắt' }}
        </button>
      </div>
    </div>
    <ReturnOrder
      v-if="isActive"
      :orders="orders"
      :order-products-map="orderProductsMap"
      :onReturn="handleReturn"
    />
  </div>
</template>

<script setup>
import ReturnOrder from '@/modules/order/ReturnOrder.vue';

const props = defineProps({
  isActive: Boolean,
  orders: {
    type: Array,
    default: () => [],
  },
  orderProductsMap: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits([
  'toggle',
  'return',
]);

const emitToggle = () => {
  emit('toggle');
};

const handleReturn = (orderCodes) => {
  emit('return', orderCodes);
};
</script>

<style scoped>
.return-container {
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  flex-direction: column;
}

.return-btn-wrap {
  display: flex;
  align-items: center;
}

.return-btn-wrap > div {
  margin-right: 10px;
}

.return-title {
  font-size: 15px;
  font-weight: 600;
}

.toggle-btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;

  background: #86c06b;
  color: #14532d;
  box-shadow: 0 6px 15px rgba(134, 192, 107, 0.3);
}

.toggle-btn:hover {
  transform: translateY(-2px);
}

.toggle-btn.off {
  background: #e5e7eb;
  color: #4b5563;
  box-shadow: none;
  opacity: 0.7;
}

.toggle-btn.off:hover {
  background: #d1d5db;
}
</style>
