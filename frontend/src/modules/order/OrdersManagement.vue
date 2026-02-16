<template>
  <div class="orders-container">
    <h1 class="page-title">🛒 Tạo Đơn Hàng</h1>

    <div class="orders-layout">
      <!-- Form Tạo Đơn Hàng -->
      <div class="form-section">
        <h2 class="section-title">Thông Tin Đơn Hàng</h2>
        <form
          @submit.prevent="submitOrder"
          @keydown.enter.prevent
          @keydown.ctrl.enter.prevent="handleCtrlEnter"
          class="order-form"
        >
          <div class="form-row">
            <OrderFormHeader
              :customer-name="orderForm.customer_name"
              :order-code="orderForm.order_code"
              :package-date="orderForm.package_date"
              :order-history="orderHistory"
              :order-code-ref="orderCodeRef"

              @update:customer-name="orderForm.customer_name = $event"
              @update:order-code="orderForm.order_code = $event"
              @update:package-date="(val) => { orderForm.package_date = val; packageDateTouched = true; }"
              @show-message="showMessage"
              @focus-product-barcode="focusProductBarcode"


              :show-package-date-picker="showPackageDatePicker"
              :package-date-mode="packageDateMode"
              :auto-scan-order-code="autoScanOrderCode"
              :is-external-order="isExternalOrder"
              :is-scanning-order-code="isScanningOrderCode"
              @order-code-enter="handleOrderCodeEnter"
              @order-code-focus="handleOrderCodeFocus"
              @start-scanner="startOrderCodeScanner"
              @toggle-auto-scan="toggleOrderCodeAutoScan"
              @toggle-external-order="toggleExternalOrder"
              @set-package-date-now="setPackageDateNow"
              @toggle-package-date-picker="togglePackageDatePicker"
            />
          </div>

          <ProductCart
            :barcode-input="barcodeInput"
            :cart-items="cartItems"
            :is-loading="loading"
            :barcode-input-ref="barcodeInputRef"
            @update:barcode-input="barcodeInput = $event"
            @add-product-by-barcode="addProductByBarcode"
            @decrease-qty="decreaseQty"
            @increase-qty="increaseQty"
            @qty-change="refreshAllocationsForIndex"
            @remove-item="removeItem"
            @clear-cart="clearCart"
            @submit="submitOrder"
          />
        </form>

        <div v-if="message" :class="['message', message.type]">
          {{ message.text }}
        </div>

        <ReturnOrderSection
          :is-active="turnOnReturn"
          :orders="orderHistory"
          :order-products-map="orderItemsMap"
          @toggle="toggleReturn"
          @return="handleReturnOrder"
        />
      </div>

      <OrdersHistorySection
        v-memo="[historyLoading, orderHistory, soldHistory, expandedOrders, returningOrders, returnedOrders]"
        :history-loading="historyLoading"
        :order-history="orderHistory"
        :expanded-orders="expandedOrders"
        :returning-orders="returningOrders"
        :returned-orders="returnedOrders"
        :order-products="orderProducts"
        @refresh="loadOrderHistory"
        @toggle-order="toggleOrderDetails"
        @return-order="handleReturnOrder"
      />

    </div>
  </div>

  <OrderCodeScanner
    :is-scanning="isScanningOrderCode"
    :scanner-status="orderCodeScannerStatus"
    :scanner-error="orderCodeScannerError"
    :video-ref="orderCodeVideoRef"
    @stop="stopOrderCodeScanner"
  />
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import jsQR from 'jsqr';
import { importsAPI, ordersAPI, soldAPI, externalOrdersAPI } from '@/services/api';
import { generateUniqueId } from '@/services/api';
import OrdersHistorySection from './OrdersHistorySection.vue';
import OrderFormHeader from './OrderFormHeader.vue';
import ProductCart from './ProductCart.vue';
import OrderCodeScanner from './OrderCodeScanner.vue';
import ReturnOrderSection from './ReturnOrderSection.vue';

function getLocalDateTimeString(date = new Date()) {
  const tzOffset = date.getTimezoneOffset() * 60000;
  const localISO = new Date(date.getTime() - tzOffset).toISOString();
  return localISO.slice(0, 16);
}

//trả hàng 

const turnOnReturn = ref(false)


function toggleReturn(){
  turnOnReturn.value = !turnOnReturn.value
}

const orderForm = ref({
  customer_name: '',
  order_code: '',
  package_date: getLocalDateTimeString(),
});

const packageDateTouched = ref(false);
const showPackageDatePicker = ref(false);
const packageDateMode = ref('now');
const barcodeInput = ref('');
const orderCodeRef = ref(null);
const barcodeInputRef = ref(null);
const cartItems = ref([]);
const imports = ref([]);
const loading = ref(false);
const message = ref(null);
const orderHistory = ref([]);
const soldHistory = ref([]);
const historyLoading = ref(false);
const expandedOrders = ref(new Set());
const returningOrders = ref(new Set());
const returnedOrders = ref(new Set());
const isScanningOrderCode = ref(false);
const autoScanOrderCode = ref(false);
const isExternalOrder = ref(false);
const orderCodeVideoRef = ref(null);
const orderCodeScannerError = ref('');
const orderCodeScannerStatus = ref('');
const ORDER_CODE_VIDEO_CONSTRAINTS = {
  video: {
    facingMode: { ideal: 'environment' },
    advanced: [
      // Gợi ý autofocus nếu webcam hỗ trợ
      { focusMode: 'continuous' },
    ],
  },
};
let orderCodeStream = null;
let orderCodeScanHandle = 0;
let jsqrCanvas = null;
let jsqrCtx = null;

function itemTotalCost(item) {
  if (!item || !Array.isArray(item.allocations)) return 0;
  return item.allocations.reduce((s, a) => s + (a.qty || 0) * (a.unit_cost || 0), 0);
}

const totalCost = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + itemTotalCost(item), 0);
});

async function loadImports() {
  try {
    const result = await importsAPI.getAll();
    imports.value = result.data || [];
  } catch (error) {
    console.error('Error loading imports:', error);
  }
}

async function loadOrderHistory() {
  historyLoading.value = true;
  try {
    const [ordersRes, soldRes] = await Promise.all([ordersAPI.getAll(), soldAPI.getAll()]);
    const ordersData = ordersRes?.data || [];
    const soldData = soldRes?.data || [];

    orderHistory.value = ordersData
      .map((row, idx) => ({
        orderID: row?.[0] || '',
        customer_name: row?.[1] || '',
        order_code: row?.[2] || row?.[0] || '',
        package_date: row?.[3] || '',
        total_cost: Number(row?.[4]) || 0,
        note: row?.[5] || '',
        rowIndex: idx + 2, // 1-based + header
      }))
      .sort((a, b) => {
        const dateA = Date.parse(a.package_date) || 0;
        const dateB = Date.parse(b.package_date) || 0;
        return dateB - dateA;
      });

    soldHistory.value = soldData.map((row, idx) => ({
      order_code: row?.[0] || '',
      productID: row?.[1] || '',
      barcode: row?.[2] || '',
      brand: row?.[3] || '',
      name: row?.[4] || '',
      category: row?.[5] || '',
      qty_sold: Number(row?.[6]) || 0,
      unit_cost: Number(row?.[7]) || 0,
      total_cost: Number(row?.[8]) || 0,
      rowIndex: idx + 2, // 1-based + header
    }));

    expandedOrders.value = new Set(
      orderHistory.value.map((order) => order.order_code).filter(Boolean),
    );
    // Ghi nhận những đơn đã được đánh dấu trả (note chứa 'returned')
    const returned = new Set();
    for (const ord of orderHistory.value) {
      if (String(ord.note || '').toLowerCase().includes('returned')) {
        returned.add(ord.order_code);
      }
    }
    returnedOrders.value = returned;
  } catch (error) {
    console.error('Error loading order history:', error);
  } finally {
    historyLoading.value = false;
  }
}

const orderItemsMap = computed(() => {
  const map = {};
  for (const item of soldHistory.value || []) {
    if (!item.order_code) continue;
    if (!map[item.order_code]) map[item.order_code] = [];
    map[item.order_code].push(item);
  }
  return map;
});

function orderProducts(orderCode) {
  return orderItemsMap.value[orderCode] || [];
}

function toggleOrderDetails(orderCode) {
  const next = new Set(expandedOrders.value);
  if (next.has(orderCode)) {
    next.delete(orderCode);
  } else {
    next.add(orderCode);
  }
  expandedOrders.value = next;
}

function isOrderExpanded(orderCode) {
  return expandedOrders.value.has(orderCode);
}

function isReturning(orderCode) {
  return returningOrders.value.has(orderCode);
}

function isReturned(orderCode) {
  return returnedOrders.value.has(orderCode);
}

function parseImportDate(value) {
  if (value === null || value === undefined) return Number.POSITIVE_INFINITY;
  const raw = String(value).trim();
  if (!raw) return Number.POSITIVE_INFINITY;

  // Prefer parsing dd/mm/yyyy (and optional time) to avoid US month/day swap.
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
  for (const row of imports.value || []) {
    const rowBarcode = normalizeBarcode(row?.[1]);
    if (!rowBarcode || rowBarcode !== target) continue;
    const available = parseInt(row?.[11]) || 0;
    const unitCost = Number(row?.[6]) || 0;
    const productID = row?.[0];
    const importDate = parseImportDate(row?.[8]);
    batches.push({ row, productID, unitCost, available, importDate });
  }
  // Sort by import date asc (oldest first). Invalid dates are pushed to the end.
  batches.sort((a, b) => {
    if (a.importDate === b.importDate) return 0;
    if (a.importDate === Number.POSITIVE_INFINITY) return 1;
    if (b.importDate === Number.POSITIVE_INFINITY) return -1;
    return a.importDate - b.importDate;
  });
  console.log(
    'Sorted batches for barcode',
    barcode,
    batches.map((b) => ({
      productID: b.productID,
      rawDate: b?.row?.[8],
      parsedDate: b.importDate,
      available: b.available,
      unitCost: b.unitCost,
    })),
  );
  return batches;
}

function computeAllocations(barcode, desiredQty) {
  const batches = getBatchesForBarcode(barcode);
  const totalAvailable = batches.reduce((s, b) => s + Math.max(0, b.available), 0);
  const target = Math.max(0, Math.min(desiredQty, totalAvailable));
  let remaining = target;
  const allocations = [];
  for (const b of batches) {
    if (remaining <= 0) break;
    const take = Math.min(b.available, remaining);
    if (take > 0) {
      allocations.push({ productID: b.productID, unit_cost: b.unitCost, qty: take });
      remaining -= take;
    }
  }
  return { allocations, totalAvailable, finalQty: target };
}

function addProductByBarcode() {
  if (!barcodeInput.value.trim()) return;

  const barcode = normalizeBarcode(barcodeInput.value);
  const batches = getBatchesForBarcode(barcode);
  console.log('batches:', batches);
  if (batches.length === 0) {
    showMessage('Không tìm thấy sản phẩm với mã barcode này', 'error');
    barcodeInput.value = '';
    return;
  }

  const totalAvailable = batches.reduce((s, b) => s + Math.max(0, b.available), 0);
  if (totalAvailable <= 0) {
    showMessage('Sản phẩm đã hết hàng', 'error');
    barcodeInput.value = '';
    return;
  }

  const existingIdx = cartItems.value.findIndex(
    (ci) => normalizeBarcode(ci.barcode) === barcode,
  );
  if (existingIdx === -1) {
    const top = batches[0];
    console.log('Selected batch for new item', {
      productID: top?.productID,
      rawDate: top?.row?.[8],
      parsedDate: top?.importDate,
    });
    const brand = top?.row?.[2] || '';
    const name = top?.row?.[3] || '';
    const category = top?.row?.[4] || '';
    // Start with qty 1
    const { allocations, totalAvailable: avail, finalQty } = computeAllocations(barcode, 1);
    console.log('Allocations for new item', allocations);
    cartItems.value.push({
      barcode,
      brand,
      name,
      category,
      qty_sold: finalQty,
      available_total: avail,
      allocations,
    });
  } else {
    const current = cartItems.value[existingIdx];
    const desired = Math.min((current.qty_sold || 0) + 1, totalAvailable);
    const { allocations, totalAvailable: avail, finalQty } = computeAllocations(barcode, desired);
    current.qty_sold = finalQty;
    current.available_total = avail;
    current.allocations = allocations;
    console.log('Updated allocations for existing item', {
      barcode,
      qty: finalQty,
      allocations,
    });
  }

  barcodeInput.value = '';
}

function focusProductBarcode() {
  if (barcodeInputRef.value) {
    barcodeInputRef.value.focus();
  }
}

function focusOrderCode() {
  if (orderCodeRef.value) {
    orderCodeRef.value.focus();
  }
}

function resetOrderCodeScanner() {
  if (orderCodeScanHandle) {
    cancelAnimationFrame(orderCodeScanHandle);
    orderCodeScanHandle = 0;
  }
  if (orderCodeStream) {
    orderCodeStream.getTracks().forEach((t) => t.stop());
    orderCodeStream = null;
  }
  if (orderCodeVideoRef.value) {
    orderCodeVideoRef.value.srcObject = null;
  }
  orderCodeScannerStatus.value = '';
  orderCodeScannerError.value = '';
}

function stopOrderCodeScanner() {
  resetOrderCodeScanner();
  isScanningOrderCode.value = false;
}

function prepareJsqrCanvas(videoEl) {
  if (!jsqrCanvas) jsqrCanvas = document.createElement('canvas');
  if (!jsqrCtx) jsqrCtx = jsqrCanvas.getContext('2d');
  if (!jsqrCtx) return { width: 0, height: 0 };

  const width = videoEl.videoWidth || videoEl.clientWidth || 0;
  const height = videoEl.videoHeight || videoEl.clientHeight || 0;
  if (width && height) {
    jsqrCanvas.width = width;
    jsqrCanvas.height = height;
  }
  return { width, height };
}

function detectWithJsqr() {
  const videoEl = orderCodeVideoRef.value;
  if (!videoEl) return '';
  const { width, height } = prepareJsqrCanvas(videoEl);
  if (!width || !height || !jsqrCtx) return '';
  jsqrCtx.drawImage(videoEl, 0, 0, width, height);
  const imageData = jsqrCtx.getImageData(0, 0, width, height);
  const result = jsQR(imageData.data, width, height);
  return result?.data || '';
}

async function tryImproveFocus() {
  if (!orderCodeStream || typeof navigator === 'undefined') return;
  const track = orderCodeStream.getVideoTracks()?.[0];
  if (!track || !track.getCapabilities || !track.applyConstraints) return;

  const caps = track.getCapabilities();
  const constraint = {};

  if (Array.isArray(caps.focusMode)) {
    if (caps.focusMode.includes('continuous')) {
      constraint.focusMode = 'continuous';
    } else if (caps.focusMode.includes('single-shot')) {
      constraint.focusMode = 'single-shot';
    }
  }

  if (caps.focusDistance && typeof caps.focusDistance.min === 'number') {
    constraint.focusDistance = caps.focusDistance.min;
  }

  if (caps.zoom && typeof caps.zoom.max === 'number') {
    const targetZoom = Math.min(caps.zoom.max, Math.max(caps.zoom.min || 1, 1.5));
    if (!Number.isNaN(targetZoom)) {
      constraint.zoom = targetZoom;
    }
  }

  if (Object.keys(constraint).length === 0) return;
  try {
    await track.applyConstraints({ advanced: [constraint] });
  } catch (err) {
    console.warn('applyConstraints focus/zoom failed:', err);
  }
}

async function scanOrderCodeFrame() {
  if (!isScanningOrderCode.value || !orderCodeVideoRef.value) return;
  try {
    const value = detectWithJsqr();
    orderCodeScannerStatus.value = 'Đang quét (jsQR)...';

    if (value) {
      orderForm.value.order_code = value;
      showMessage('Đã quét mã vận đơn', 'success');
      stopOrderCodeScanner();
      await nextTick();
      handleOrderCodeEnter();
      return;
    }
  } catch (error) {
    console.error('Barcode detect error:', error);
    orderCodeScannerError.value = error?.message || 'Không thể quét mã.';
    stopOrderCodeScanner();
    return;
  }
  orderCodeScanHandle = requestAnimationFrame(scanOrderCodeFrame);
}

async function startOrderCodeScanner() {
  if (isScanningOrderCode.value) return;
  resetOrderCodeScanner();
  orderCodeScannerError.value = '';
  orderCodeScannerStatus.value = 'Đang mở camera...';
  isScanningOrderCode.value = true;
  await nextTick();

  try {
    if (!jsQR) {
      throw new Error('Không tải được thư viện jsQR để quét QR.');
    }

    orderCodeStream = await navigator.mediaDevices.getUserMedia(ORDER_CODE_VIDEO_CONSTRAINTS);
    const videoEl = orderCodeVideoRef.value;
    if (!videoEl) throw new Error('Không tìm thấy camera.');
    videoEl.srcObject = orderCodeStream;
    await videoEl.play();

    const { width, height } = prepareJsqrCanvas(videoEl);
    if (!width || !height) {
      throw new Error('Không lấy được khung hình từ camera để quét QR.');
    }

    orderCodeScannerStatus.value = 'Đưa mã QR vào khung hình (jsQR, đang cố lấy nét)...';
    await tryImproveFocus();
    orderCodeScanHandle = requestAnimationFrame(scanOrderCodeFrame);
  } catch (error) {
    console.error('Start scanner error:', error);
    orderCodeScannerError.value = error?.message || 'Không mở được camera.';
    orderCodeScannerStatus.value = '';
  }
}

function handleOrderCodeFocus() {
  if (!autoScanOrderCode.value || isScanningOrderCode.value) return;
  startOrderCodeScanner();
}

// function toggleOrderCodeAutoScan() {
//   autoScanOrderCode.value = !autoScanOrderCode.value;
//   if (!autoScanOrderCode.value) {
//     stopOrderCodeScanner();
//     return;
//   }
//   if (orderCodeRef.value && document.activeElement === orderCodeRef.value) {
//     startOrderCodeScanner();
//   }
// }

// function toggleExternalOrder() {
//   isExternalOrder.value = !isExternalOrder.value;
//   if (isExternalOrder.value) {
//     // Tắt quét tự động khi bật chế độ đơn ngoài
//     autoScanOrderCode.value = false;
//     stopOrderCodeScanner();
//     orderForm.value.order_code = '';
//   }
// }

async function handleCtrlEnter() {
  await submitOrder();
  await nextTick();
  focusOrderCode();
}

function refreshAllocationsForIndex(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  const desired = Math.max(1, Number(item.qty_sold || 1));
  const { allocations, totalAvailable, finalQty } = computeAllocations(item.barcode, desired);
  item.available_total = totalAvailable;
  item.qty_sold = finalQty;
  item.allocations = allocations;
}

function increaseQty(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  if ((item.qty_sold || 0) < (item.available_total || 0)) {
    item.qty_sold = (item.qty_sold || 0) + 1;
    refreshAllocationsForIndex(idx);
  }
}

function decreaseQty(idx) {
  const item = cartItems.value[idx];
  if (!item) return;
  if ((item.qty_sold || 0) > 1) {
    item.qty_sold = (item.qty_sold || 0) - 1;
    refreshAllocationsForIndex(idx);
  }
}

function removeItem(idx) {
  cartItems.value.splice(idx, 1);
}

function clearCart() {
  if (confirm('Bạn chắc chắn muốn xóa hết sản phẩm?')) {
    cartItems.value = [];
  }
}

async function submitOrder() {
  if (loading.value) return;

  if (cartItems.value.length === 0) {
    showMessage('Vui lòng thêm sản phẩm vào đơn hàng', 'error');
    return;
  }

  if (!orderForm.value.package_date) {
    orderForm.value.package_date = getLocalDateTimeString();
  }

  loading.value = true;

  try {
    const orderID = generateUniqueId();
    const inputOrderCode = (orderForm.value.order_code || '').trim();
    const orderCode = inputOrderCode || `ORD-${Date.now()}`;

    const orderAPI = isExternalOrder.value
      ? externalOrdersAPI
      : ordersAPI;

    // 1️⃣ Tạo order
    await orderAPI.create({
      orderID,
      customer_name: orderForm.value.customer_name,
      order_code: orderCode,
      package_date: orderForm.value.package_date,
      total_cost: totalCost.value,
      note: '',
    });

    // 2️⃣ Tạo sold + gom update tồn kho
    const updatesMap = new Map();

    for (const item of cartItems.value) {
      for (const al of item.allocations || []) {
        if (!al || !al.qty) continue;
        await soldAPI.create({
          order_code: orderCode,
          productID: al.productID,
          barcode: item.barcode,
          brand: item.brand,
          name: item.name,
          category: item.category,
          qty_sold: al.qty,
          unit_cost: al.unit_cost,
          total_cost: al.qty * al.unit_cost,
        });

        const rowIndex = imports.value.findIndex(
          (imp) => imp[0] === al.productID
        );

        if (rowIndex === -1) continue;

        const importRowData = imports.value[rowIndex];

        const currentQtySold = parseInt(importRowData[10]) || 0;
        const currentAvailable = parseInt(importRowData[5]) || 0;

        const newQtySold = currentQtySold + al.qty;
        const newAvailableQty = currentAvailable - al.qty;

        if (newAvailableQty < 0) {
          throw new Error(
            `Sản phẩm ${item.name} không đủ tồn kho`
          );
        }

        if (updatesMap.has(rowIndex)) {
          const existing = updatesMap.get(rowIndex);

          updatesMap.set(rowIndex, {
            row: rowIndex + 2, // 1-based + header
            data: {
              qty_sold: existing.data.qty_sold + al.qty,
              available_qty: existing.data.available_qty - al.qty,
            },
          });
        } else {
          updatesMap.set(rowIndex, {
            row: rowIndex + 2,
            data: {
              qty_sold: newQtySold,
              available_qty: newAvailableQty,
            },
          });
        }
      }
    }

    const updates = Array.from(updatesMap.values());

    if (updates.length > 0) {
      await importsAPI.updateRows(updates);

      // 🔥 LOAD LẠI TỪ SERVER THAY VÌ APPLY LOCAL
      await loadImports();
    }

    showMessage(
      `Tạo đơn hàng thành công! Mã: ${orderCode}`,
      'success'
    );

    // 3️⃣ Reset form
    orderForm.value = {
      customer_name: '',
      order_code: '',
      package_date: getLocalDateTimeString(),
    };

    packageDateTouched.value = false;
    showPackageDatePicker.value = false;
    packageDateMode.value = 'now';
    barcodeInput.value = '';
    cartItems.value = [];
    isExternalOrder.value = false;

    await loadOrderHistory();
  } catch (error) {
    showMessage('Lỗi: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

function showMessage(text, type) {
  message.value = { text, type };
  setTimeout(() => {
    message.value = null;
  }, 4000);
}

function addReturning(orderCode) {
  const next = new Set(returningOrders.value);
  next.add(orderCode);
  returningOrders.value = next;
}

function removeReturning(orderCode) {
  const next = new Set(returningOrders.value);
  next.delete(orderCode);
  returningOrders.value = next;
}

function markReturned(orderCode) {
  const next = new Set(returnedOrders.value);
  next.add(orderCode);
  returnedOrders.value = next;
}

async function handleReturnOrder(orderCodes) {
  if (!orderCodes) return;

  // Chuẩn hóa về array
  const codes = Array.isArray(orderCodes)
    ? orderCodes
    : [orderCodes];

  const confirmed = confirm(
    `Xác nhận trả ${codes.length} đơn? Hệ thống sẽ cộng lại tồn kho.`
  );
  if (!confirmed) return;

  try {
    await loadImports(); // lấy tồn kho mới nhất

    const allQtyByProduct = {};
    const soldRowsToDelete = [];
    const orderRowsToDelete = [];

    for (const orderCode of codes) {
      if (
        !orderCode ||
        isReturning(orderCode) ||
        isReturned(orderCode)
      )
        continue;

      addReturning(orderCode);

      const items = orderProducts(orderCode);
      if (!items || items.length === 0) continue;

      // Gom tổng số lượng trả theo productID
      for (const item of items) {
        if (!item.productID) continue;

        const pid = String(item.productID);
        const qty = Number(item.qty_sold) || 0;

        allQtyByProduct[pid] =
          (allQtyByProduct[pid] || 0) + qty;
      }

      // Gom sold rows để xóa
      soldHistory.value
        .filter((s) => String(s.order_code) === String(orderCode))
        .forEach((s) => {
          if (Number.isInteger(s.rowIndex)) {
            soldRowsToDelete.push(s.rowIndex);
          }
        });

      // Gom order row để xóa
      const orderRowIndex = (
        orderHistory.value.find(
          (o) => o.order_code === orderCode
        ) || {}
      ).rowIndex;

      if (orderRowIndex) {
        orderRowsToDelete.push(orderRowIndex);
      }
    }

    // ===== Update tồn kho =====
    const updates = [];

    for (const [productID, qtyReturn] of Object.entries(allQtyByProduct)) {
      const importRowData = imports.value.find(
        (imp) => String(imp[0]) === productID
      );
      if (!importRowData) continue;

      const rowIndex =
        imports.value.indexOf(importRowData) + 2;

      const totalQty = parseInt(importRowData[5], 10) || 0;
      const currentQtySold =
        parseInt(importRowData[10], 10) || 0;

      const qtyToDeduct = Math.min(qtyReturn, currentQtySold);
      const newQtySold = Math.max(
        0,
        currentQtySold - qtyToDeduct
      );
      const newAvailableQty = Math.max(
        0,
        totalQty - newQtySold
      );

      const oldAvailableQty = Math.max(
        0,
        totalQty - currentQtySold
      );

      const productName = importRowData[3]; // cột tên sản phẩm (nếu khác thì đổi index)

      const increase = newAvailableQty - oldAvailableQty;

      updates.push({
        row: rowIndex,
        productID,
        productName,
        oldAvailableQty,
        newAvailableQty,
        increase,
        data: {
          qty_sold: newQtySold,
          available_qty: newAvailableQty,
        },
      });
    }

    if (updates.length === 0) {
      showMessage(
        "Không tìm thấy sản phẩm tương ứng để cộng lại tồn kho",
        "error"
      );
      return;
    }

    await importsAPI.updateRows(updates);
    await loadImports();
    const detailMessages = updates.map(u => {
      return `${u.productName} (${u.productID})
    Tăng: +${u.increase}
    ${u.oldAvailableQty} → ${u.newAvailableQty}`;
    });

    alert(
      `ĐÃ CẬP NHẬT TỒN KHO\n\n` +
      detailMessages.join("\n\n")
    );
    if (soldRowsToDelete.length > 0) {
      await soldAPI.deleteRows(soldRowsToDelete);
    }

    if (orderRowsToDelete.length > 0) {
      await ordersAPI.deleteRows(orderRowsToDelete);
    }

    showMessage(
      `Đã trả ${codes.length} đơn và cập nhật tồn kho`,
      "success"
    );

    await Promise.all([loadImports(), loadOrderHistory()]);
  } catch (error) {
    showMessage(
      "Trả hàng thất bại: " + error.message,
      "error"
    );
  } finally {
    for (const code of codes) {
      removeReturning(code);
      markReturned(code);
    }
  }
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}

onMounted(() => {
  loadImports();
  loadOrderHistory();
});

onBeforeUnmount(() => {
  stopOrderCodeScanner();
});
</script>

<style scoped>
.orders-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  background: #fafaf9;
  min-height: 100vh;
}

.orders-layout {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 16px;
  align-items: flex-start;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #2d5016;
  margin-bottom: 24px;
  text-align: center;
}

.form-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 16px;
}

.order-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
  font-size: 14px;
  font-weight: 500;
}

.message.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.message.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

@media (max-width: 768px) {
  .orders-layout {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .orders-container {
    padding: 12px;
  }
}
</style>
