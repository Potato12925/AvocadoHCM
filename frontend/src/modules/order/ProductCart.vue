<template>
  <div>
    <h3 class="text-[16px] font-semibold text-[#2d5016] mt-[20px] mb-[12px] pt-[16px] border-t border-[#eee]">
      Thêm Sản Phẩm Vào Đơn
    </h3>

    <div class="flex flex-col gap-[6px]">
      <label for="barcodeInput" class="text-[14px] font-medium text-[#555]">
        Quét/Nhập Barcode
      </label>

      <input
        v-model="barcodeInput"
        type="text"
        id="barcodeInput"
        placeholder="Nhập hoặc quét mã barcode"
        ref="localBarcodeInputRef"
        @keyup.enter="addProductByBarcode"
        class="px-[12px] py-[10px] border border-[#ddd] rounded-[8px] text-[16px] transition
               focus:outline-none focus:border-[#86c06b] focus:ring-[3px] focus:ring-[rgba(134,192,107,0.1)]"
      />
    </div>

    <div
      v-if="cartItems.length === 0"
      class="p-[24px] text-center text-[#999] text-[15px] bg-[#fafaf9] rounded-[8px] border border-dashed border-[#ddd]"
    >
      Chưa có sản phẩm nào trong đơn hàng
    </div>

    <div
      v-else
      class="flex flex-col gap-[12px] p-[12px] bg-[#fafaf9] rounded-[8px] border border-[#eee]"
    >
      <CartItemRow
        v-for="(item, idx) in cartItems"
        :key="idx"
        :item="item"
        :index="idx"
        @decreaseQty="decreaseQty"
        @increaseQty="increaseQty"
        @qtyChange="handleQtyChange"
        @remove="removeItem"
      />

      <div class="mt-[12px] pt-[12px] border-t-[2px] border-[#eee]">
        <div class="flex justify-end gap-[16px] text-[15px] font-semibold text-[#2d5016]">
          <span class="text-[#666]">Tổng Chi Phí:</span>
          <span class="text-[#86c06b] text-[17px]">
            {{ formatNumber(totalCost) }}₫
          </span>
        </div>
      </div>
    </div>

    <div class="flex gap-[12px] mt-[16px]">
      <button
        type="button"
        @click="clearCart"
        :disabled="cartItems.length === 0"
        class="flex-1 px-[16px] py-[12px] bg-[#f3f4f6] border border-[#ddd] text-[#555]
               rounded-[8px] text-[15px] font-semibold transition
               hover:bg-[#e5e7eb] disabled:opacity-50 disabled:cursor-not-allowed"
      >
        🗑 Xóa Hết
      </button>

      <button
        type="submit"
        :disabled="isLoading || cartItems.length === 0"
        class="flex-1 px-[16px] py-[12px] rounded-[8px] text-[15px] font-semibold text-white
               bg-[linear-gradient(135deg,#86c06b_0%,#6db046_100%)]
               transition
               hover:-translate-y-[2px]
               hover:shadow-[0_4px_12px_rgba(134,192,107,0.3)]
               disabled:opacity-60 disabled:cursor-not-allowed"
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
  cartItems: {
    type: Array,
    default: () => [],
  },
  imports: {
    type: Array,
    default: () => [],
  },
  isLoading: Boolean,
});

const emit = defineEmits([
  'update:cartItems',
  'notify',
  'submit',
]);

const localBarcodeInputRef = ref(null);
const barcodeInput = ref('');

function focusBarcodeInput() {
  localBarcodeInputRef.value?.focus();
}

defineExpose({
  focusBarcodeInput,
});

const totalCost = computed(() => {
  return props.cartItems.reduce((sum, item) => sum + itemTotalCost(item), 0);
});

const cartItems = computed(() => props.cartItems || []);

function itemTotalCost(item) {
  if (!item || !Array.isArray(item.allocations)) return 0;
  return item.allocations.reduce((s, a) => s + (a.qty || 0) * (a.unit_cost || 0), 0);
}

function updateCartItems(nextCartItems) {
  emit('update:cartItems', nextCartItems);
}

function parseImportDate(value) {
  if (value === null || value === undefined) return Number.POSITIVE_INFINITY;
  const raw = String(value).trim();
  if (!raw) return Number.POSITIVE_INFINITY;

  const dmyMatch = raw.match(
    /^(\d{1,2})[\/-](\d{1,2})[\/-](\d{2,4})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?$/,
  );
  if (dmyMatch) {
    const day = parseInt(dmyMatch[1], 10);
    const month = parseInt(dmyMatch[2], 10) - 1;
    const year = parseInt(
      dmyMatch[3].length === 2 ? `20${dmyMatch[3]}` : dmyMatch[3],
      10,
    );
    const hour = dmyMatch[4] ? parseInt(dmyMatch[4], 10) : 0;
    const minute = dmyMatch[5] ? parseInt(dmyMatch[5], 10) : 0;
    const second = dmyMatch[6] ? parseInt(dmyMatch[6], 10) : 0;
    const dt = new Date(year, month, day, hour, minute, second);
    if (!Number.isNaN(dt.getTime())) return dt.getTime();
  }

  const direct = Date.parse(raw);
  if (!Number.isNaN(direct)) return direct;

  return Number.POSITIVE_INFINITY;
}

function normalizeBarcode(value) {
  if (value === null || value === undefined) return '';
  const trimmed = String(value).trim();
  if (!trimmed) return '';
  return trimmed.replace(/\.0+$/, '');
}

function getBatchesForBarcode(barcode) {
  const target = normalizeBarcode(barcode);
  if (!target) return [];

  const batches = [];
  for (const row of props.imports || []) {
    const rowBarcode = normalizeBarcode(row?.[1]);
    if (!rowBarcode || rowBarcode !== target) continue;

    batches.push({
      row,
      productID: row?.[0],
      unitCost: Number(row?.[6]) || 0,
      available: parseInt(row?.[11], 10) || 0,
      importDate: parseImportDate(row?.[8]),
    });
  }

  batches.sort((a, b) => {
    if (a.importDate === b.importDate) return 0;
    if (a.importDate === Number.POSITIVE_INFINITY) return 1;
    if (b.importDate === Number.POSITIVE_INFINITY) return -1;
    return a.importDate - b.importDate;
  });

  return batches;
}

function computeAllocations(barcode, desiredQty) {
  const batches = getBatchesForBarcode(barcode);
  const totalAvailable = batches.reduce((sum, batch) => sum + Math.max(0, batch.available), 0);
  const target = Math.max(0, Math.min(desiredQty, totalAvailable));
  let remaining = target;
  const allocations = [];

  for (const batch of batches) {
    if (remaining <= 0) break;
    const take = Math.min(batch.available, remaining);
    if (take > 0) {
      allocations.push({
        productID: batch.productID,
        unit_cost: batch.unitCost,
        qty: take,
      });
      remaining -= take;
    }
  }

  return { allocations, totalAvailable, finalQty: target };
}

function addProductByBarcode() {
  const barcode = normalizeBarcode(barcodeInput.value);
  if (!barcode) return;

  const batches = getBatchesForBarcode(barcode);
  if (batches.length === 0) {
    emit('notify', 'Không tìm thấy sản phẩm với mã barcode này', 'error');
    barcodeInput.value = '';
    return;
  }

  const totalAvailable = batches.reduce((sum, batch) => sum + Math.max(0, batch.available), 0);
  if (totalAvailable <= 0) {
    emit('notify', 'Sản phẩm đã hết hàng', 'error');
    barcodeInput.value = '';
    return;
  }

  const nextCartItems = [...cartItems.value];
  const existingIdx = nextCartItems.findIndex(
    (item) => normalizeBarcode(item.barcode) === barcode,
  );

  if (existingIdx === -1) {
    const top = batches[0];
    const { allocations, totalAvailable: availableTotal, finalQty } = computeAllocations(barcode, 1);
    nextCartItems.push({
      barcode,
      brand: top?.row?.[2] || '',
      name: top?.row?.[3] || '',
      category: top?.row?.[4] || '',
      qty_sold: finalQty,
      available_total: availableTotal,
      allocations,
    });
  } else {
    const current = nextCartItems[existingIdx];
    const desired = Math.min((current.qty_sold || 0) + 1, totalAvailable);
    const { allocations, totalAvailable: availableTotal, finalQty } = computeAllocations(barcode, desired);
    nextCartItems[existingIdx] = {
      ...current,
      qty_sold: finalQty,
      available_total: availableTotal,
      allocations,
    };
  }

  updateCartItems(nextCartItems);
  barcodeInput.value = '';
}

function refreshAllocationsForIndex(idx, desiredQty) {
  const item = cartItems.value[idx];
  if (!item) return;

  const desired = Math.max(1, Number(desiredQty ?? item.qty_sold ?? 1));
  const { allocations, totalAvailable, finalQty } = computeAllocations(item.barcode, desired);
  const nextCartItems = [...cartItems.value];
  nextCartItems[idx] = {
    ...item,
    available_total: totalAvailable,
    qty_sold: finalQty,
    allocations,
  };
  updateCartItems(nextCartItems);
}

function increaseQty(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  if ((item.qty_sold || 0) < (item.available_total || 0)) {
    refreshAllocationsForIndex(idx, (item.qty_sold || 0) + 1);
  }
}

function decreaseQty(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  if ((item.qty_sold || 0) > 1) {
    refreshAllocationsForIndex(idx, (item.qty_sold || 0) - 1);
  }
}

function handleQtyChange(payload) {
  const index = payload?.index;
  if (!Number.isInteger(index)) return;
  refreshAllocationsForIndex(index, payload?.qty);
}

function removeItem(idx) {
  updateCartItems(cartItems.value.filter((_, index) => index !== idx));
}

function clearCart() {
  if (confirm('Bạn chắc chắn muốn xóa hết sản phẩm?')) {
    updateCartItems([]);
  }
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}
</script>
