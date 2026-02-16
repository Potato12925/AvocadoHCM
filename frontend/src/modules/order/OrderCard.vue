<template>
  <div class="order-card">
    <div class="order-header">
      <div>
        <strong>{{ order.order_code }}</strong>
        <span> - {{ order.total_cost }}</span>
      </div>

      <!-- Slot để chèn nút riêng -->
      <slot name="actions"></slot>
    </div>

    <div
      v-for="item in order.products"
      :key="item.rowIndex"
      class="product-row"
    >
      <div class="product-name">
        {{ item.name }}
      </div>

      <div class="product-meta">
        <span>{{ item.barcode }} | {{ item.brand }} | {{item.category}}</span>
        <div> {{ item.qty_sold }} x {{ item.unit_cost }} </div>
        <div> {{ item.total_cost }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  order: Object
})
</script>
<style scoped>
.order-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 18px;
  margin-bottom: 20px;
  border: 2px solid #86c06b;
  box-shadow: 0 6px 18px rgba(20, 83, 45, 0.08);
  transition: all 0.25s ease;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(20, 83, 45, 0.15);
}

/* ===== HEADER ===== */
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 2px dashed #86c06b;
  font-size: 16px;
}

.order-header strong {
  color: #14532d;
  font-size: 17px;
}

.order-header span {
  color: #4b5563;
  margin-left: 6px;
}

/* ===== PRODUCT ===== */
.product-row {
  padding: 12px 0;
  border-top: 1px solid #e5e7eb;
}

.product-row:first-of-type {
  border-top: none;
}

.product-name {
  font-weight: 600;
  margin-bottom: 6px;
  color: #14532d;
}

/* Meta dạng tag */
.product-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 14px;
  align-items: center;
}

.product-meta span {
  background: #f0fdf4;
  color: #4b5563;
  padding: 5px 10px;
  border-radius: 8px;
  border: 1px solid #86c06b;
}

/* Nếu muốn highlight tổng tiền */
.product-meta div:last-child {
  margin-left: auto;
}
</style>