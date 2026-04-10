<template>
  <div class="cart-item">
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
      <div class="item-cost">Tổng giá vốn: {{ formatNumber(itemTotalCost) }}₫</div>
    </div>

    <div class="item-qty">
      <button
        type="button"
        @click="emitDecreaseQty"
        class="btn-qty"
        :disabled="item.qty_sold <= 1"
      >
        −
      </button>
      <input
        v-model.number="localQtySold"
        type="number"
        min="1"
        :max="item.available_total"
        @change="emitQtyChange"
        class="qty-input"
      />
      <button
        type="button"
        @click="emitIncreaseQty"
        class="btn-qty"
        :disabled="item.qty_sold >= item.available_total"
      >
        +
      </button>
    </div>

    <div class="item-total">
      {{ formatNumber(itemTotalCost) }}₫
    </div>

    <button
      type="button"
      @click="emitRemove"
      class="btn-remove"
    >
      ✕
    </button>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  index: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits([
  'decreaseQty',
  'increaseQty',
  'qtyChange',
  'remove',
]);

const localQtySold = ref(props.item.qty_sold || 0);

watch(() => props.item.qty_sold, (newVal) => {
  localQtySold.value = newVal || 0;
});

const itemTotalCost = computed(() => {
  if (!props.item || !Array.isArray(props.item.allocations)) return 0;
  return props.item.allocations.reduce((s, a) => s + (a.qty || 0) * (a.unit_cost || 0), 0);
});

const emitDecreaseQty = () => {
  emit('decreaseQty', props.index);
};

const emitIncreaseQty = () => {
  emit('increaseQty', props.index);
};

const emitQtyChange = () => {
  emit('qtyChange', {
    index: props.index,
    qty: Number(localQtySold.value) || 0,
  });
};

const emitRemove = () => {
  emit('remove', props.index);
};

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}
</script>

<style scoped>
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

@media (max-width: 768px) {
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
</style>
