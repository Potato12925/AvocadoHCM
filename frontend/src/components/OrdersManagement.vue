<template>
  <div class="orders-container">
    <h1 class="page-title">🛒 Tạo Đơn Hàng</h1>

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
          <div class="form-group">
            <label for="customerName">Tên Khách Hàng</label>
            <input
              v-model="orderForm.customer_name"
              type="text"
              id="customerName"
              placeholder="Tên khách hàng"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <div class="label-row">
              <label for="orderCode">Mã Vận Đơn</label>
              <button
                type="button"
                class="btn-scan-toggle"
                :disabled="scanLockedUntilSubmit || scannerStarting"
                @click="toggleOrderCodeScanner"
              >
                {{
                  scannerStarting
                    ? 'Đang mở camera...'
                    : isOrderCodeScannerOn
                      ? 'Tắt quét mã vận đơn'
                      : scanLockedUntilSubmit
                        ? 'Đã quét - chờ hoàn tất đơn'
                        : 'Bật quét mã vận đơn'
                }}
              </button>
            </div>
            <input
              v-model="orderForm.order_code"
              type="text"
              id="orderCode"
              placeholder="Để trống để tự sinh"
              ref="orderCodeRef"
              @keyup.enter="focusBarcode"
              class="input-field"
            />
            <div v-if="isOrderCodeScannerOn" class="scanner-preview">
              <video ref="orderCodeVideoRef" class="scanner-video" autoplay playsinline muted></video>
              <div class="scanner-hint">Đưa mã QR vận đơn vào khung camera</div>
            </div>
            <div v-else-if="scannerError" class="scanner-error">
              {{ scannerError }}
            </div>
          </div>
        </div>

        <div class="form-group">
          <label for="packageDate">Ngày Đóng Gói</label>
          <input
            v-model="orderForm.package_date"
            type="date"
            id="packageDate"
            required
            class="input-field"
          />
        </div>

        <h3 class="subsection-title">Thêm Sản Phẩm Vào Đơn</h3>

        <div class="form-group">
          <label for="barcodeInput">Quét/Nhập Barcode</label>
          <input
            v-model="barcodeInput"
            type="text"
            id="barcodeInput"
            placeholder="Nhập hoặc quét mã barcode"
            ref="barcodeInputRef"
            @keyup.enter="addProductByBarcode"
            class="input-field"
          />
        </div>

        <div v-if="cartItems.length === 0" class="empty-cart">
          Chưa có sản phẩm nào trong đơn hàng
        </div>

        <div v-else class="cart-items">
          <div class="cart-item" v-for="(item, idx) in cartItems" :key="idx">
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
              <div class="item-cost">Tổng giá vốn: {{ formatNumber(itemTotalCost(item)) }}₫</div>
            </div>

            <div class="item-qty">
              <button
                type="button"
                @click="decreaseQty(idx)"
                class="btn-qty"
                :disabled="item.qty_sold <= 1"
              >
                −
              </button>
              <input
                v-model.number="item.qty_sold"
                type="number"
                min="1"
                :max="item.available_total"
                @change="refreshAllocationsForIndex(idx)"
                class="qty-input"
              />
              <button
                type="button"
                @click="increaseQty(idx)"
                class="btn-qty"
                :disabled="item.qty_sold >= item.available_total"
              >
                +
              </button>
            </div>

            <div class="item-total">
              {{ formatNumber(itemTotalCost(item)) }}₫
            </div>

            <button
              type="button"
              @click="removeItem(idx)"
              class="btn-remove"
            >
              ✕
            </button>
          </div>

          <div class="order-summary">
            <div class="summary-row">
              <span class="summary-label">Tổng Chi Phí:</span>
              <span class="summary-value">{{ formatNumber(totalCost) }}₫</span>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button
            type="button"
            @click="clearCart"
            class="btn-secondary"
            :disabled="cartItems.length === 0"
          >
            🗑 Xóa Hết
          </button>
          <button
            type="submit"
            class="btn-submit"
            :disabled="loading || cartItems.length === 0"
          >
            {{ loading ? 'Đang lưu...' : '✓ Hoàn Tất Đơn Hàng' }}
          </button>
        </div>
      </form>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>

    <div class="history-section">
      <div class="history-header">
        <h2 class="section-title">📜 Lịch Sử Đơn Hàng</h2>
        <button
          type="button"
          class="btn-refresh"
          @click="loadOrderHistory"
          :disabled="historyLoading"
        >
          {{ historyLoading ? 'Đang tải...' : '⟳ Tải lại' }}
        </button>
      </div>
      <div class="history-filters">
        <div class="filter-group">
          <label>Mã vận đơn</label>
          <input
            v-model="filterOrderCode"
            type="text"
            class="filter-input"
            placeholder="Nhập mã đơn"
          />
        </div>
        <div class="filter-group">
          <label>Mã sản phẩm</label>
          <input
            v-model="filterBarcode"
            type="text"
            class="filter-input"
            placeholder="Barcode trong đơn"
          />
        </div>
        <div class="filter-group">
          <label>Từ ngày</label>
          <input v-model="filterDateFrom" type="date" class="filter-input" />
        </div>
        <div class="filter-group">
          <label>Đến ngày</label>
          <input v-model="filterDateTo" type="date" class="filter-input" />
        </div>
        <div class="filter-actions">
          <button type="button" class="btn-secondary small" @click="clearFilters">Xóa lọc</button>
        </div>
      </div>

      <div v-if="historyLoading" class="history-empty">Đang tải dữ liệu đơn hàng...</div>
      <div v-else-if="orderHistory.length === 0" class="history-empty">
        Chưa có đơn hàng nào được tạo.
      </div>
      <div v-else class="history-list">
        <div class="history-card" v-for="order in filteredOrders" :key="order.order_code">
          <div class="history-card-main">
            <div class="history-card-info">
              <div class="history-order-code">{{ order.order_code || '(Không mã)' }}</div>
              <div class="history-info-row">
                <span>Khách: <strong>{{ order.customer_name || 'N/A' }}</strong></span>
                <span>Ngày đóng gói: {{ order.package_date }}</span>
                <span>Tổng chi phí: {{ formatNumber(order.total_cost) }}₫</span>
              </div>
            </div>
            <div class="history-actions">
              <button
                type="button"
                class="btn-return"
                :disabled="isReturning(order.order_code) || isReturned(order.order_code) || orderProducts(order.order_code).length === 0"
                @click="handleReturnOrder(order.order_code)"
              >
                {{
                  isReturned(order.order_code)
                    ? 'Đã trả'
                    : isReturning(order.order_code)
                      ? 'Đang trả...'
                      : '↩ Trả hàng'
                }}
              </button>
              <button
                type="button"
                class="btn-toggle"
                @click="toggleOrderDetails(order.order_code)"
              >
                {{ isOrderExpanded(order.order_code) ? 'Thu gọn' : 'Xem sản phẩm' }}
              </button>
            </div>
          </div>

          <transition name="fade">
            <div v-if="isOrderExpanded(order.order_code)" class="history-details">
              <div v-if="orderProducts(order.order_code).length === 0" class="history-empty-products">
                Chưa có sản phẩm nào được ghi lại cho đơn này.
              </div>
              <div v-else class="history-products">
                <div
                  class="history-product"
                  v-for="item in orderProducts(order.order_code)"
                  :key="`${order.order_code}-${item.productID}-${item.barcode}`"
                >
                  <div class="history-product-main">
                    <div class="history-product-name">{{ item.name }}</div>
                    <div class="history-product-meta">
                      Barcode: {{ item.barcode }} | Thương hiệu: {{ item.brand }} | Danh mục:
                      {{ item.category }}
                    </div>
                  </div>
                  <div class="history-product-qty">
                    {{ item.qty_sold }} × {{ formatNumber(item.unit_cost) }}₫
                  </div>
                  <div class="history-product-total">{{ formatNumber(item.total_cost) }}₫</div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { importsAPI, ordersAPI, soldAPI } from '../services/api';
import { generateUniqueId } from '../services/api';

const orderForm = ref({
  customer_name: '',
  order_code: '',
  package_date: new Date().toISOString().split('T')[0],
});

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
const filterOrderCode = ref('');
const filterBarcode = ref('');
const filterDateFrom = ref('');
const filterDateTo = ref('');
const isOrderCodeScannerOn = ref(false);
const scannerSupportsQR = ref(false);
const scannerError = ref('');
const scannerStarting = ref(false);
const orderCodeVideoRef = ref(null);
const scannerIntervalId = ref(null);
const videoStream = ref(null);
const scanLockedUntilSubmit = ref(false);
const barcodeDetector = ref(null);
const scannerMode = ref('detector'); // 'detector' | 'zxing'
const zxingReader = ref(null);
const zxingControls = ref(null);
const zxingLib = ref(null);

/**
 * Cập nhật cache imports.value theo danh sách updates (row 1-based, có header).
 * Tránh phải reload toàn bộ khi chỉ đổi qty_sold/available_qty.
 */
function applyLocalImportUpdates(updates = []) {
  if (!Array.isArray(updates) || updates.length === 0) return;

  const map = new Map();
  for (const u of updates) {
    if (!u || !Number.isInteger(u.row) || u.row <= 1 || !u.data) continue;
    map.set(u.row, u.data);
  }
  if (map.size === 0) return;

  const next = imports.value.map((row, idx) => {
    const sheetRow = idx + 2; // +1 header, +1 1-based
    const data = map.get(sheetRow);
    if (!data) return row;

    const clone = Array.isArray(row) ? [...row] : [];
    if (Object.prototype.hasOwnProperty.call(data, 'qty_in')) {
      clone[5] = data.qty_in;
    }
    if (Object.prototype.hasOwnProperty.call(data, 'qty_sold')) {
      clone[10] = data.qty_sold;
    }
    if (Object.prototype.hasOwnProperty.call(data, 'available_qty')) {
      clone[11] = data.available_qty;
    }
    if (Object.prototype.hasOwnProperty.call(data, 'unit_cost')) {
      clone[6] = data.unit_cost;
    }
    if (Object.prototype.hasOwnProperty.call(data, 'break_even_price')) {
      clone[7] = data.break_even_price;
    }
    if (Object.prototype.hasOwnProperty.call(data, 'import_date')) {
      clone[8] = data.import_date;
    }
    if (Object.prototype.hasOwnProperty.call(data, 'note')) {
      clone[9] = data.note;
    }
    return clone;
  });

  imports.value = next;
}

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

    expandedOrders.value = new Set();
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

const filteredOrders = computed(() => {
  const code = (filterOrderCode.value || '').toLowerCase();
  const barcode = (filterBarcode.value || '').toLowerCase();
  const from = filterDateFrom.value ? Date.parse(filterDateFrom.value) : null;
  const to = filterDateTo.value ? Date.parse(filterDateTo.value) : null;

  return orderHistory.value.filter((o) => {
    if (code && !(o.order_code || '').toLowerCase().includes(code)) return false;

    if (from || to) {
      const pkgDate = Date.parse(o.package_date);
      if (Number.isNaN(pkgDate)) return false;
      if (from && pkgDate < from) return false;
      if (to && pkgDate > to) return false;
    }

    if (barcode) {
      const items = orderProducts(o.order_code);
      const match = items.some((it) =>
        String(it.barcode || '').toLowerCase().includes(barcode),
      );
      if (!match) return false;
    }
    return true;
  });
});

function clearFilters() {
  filterOrderCode.value = '';
  filterBarcode.value = '';
  filterDateFrom.value = '';
  filterDateTo.value = '';
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

  const direct = Date.parse(raw);
  if (!Number.isNaN(direct)) return direct;

  const match = raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);
  if (match) {
    const day = parseInt(match[1], 10);
    const month = parseInt(match[2], 10) - 1;
    const year = parseInt(match[3].length === 2 ? `20${match[3]}` : match[3], 10);
    const dt = new Date(year, month, day);
    if (!Number.isNaN(dt.getTime())) return dt.getTime();
  }

  return Number.POSITIVE_INFINITY;
}

function getBatchesForBarcode(barcode) {
  const batches = [];
  for (const row of imports.value || []) {
    if (String(row?.[1] || '') !== String(barcode)) continue;
    const available = parseInt(row?.[11]) || 0;
    const unitCost = Number(row?.[6]) || 0;
    const productID = row?.[0];
    const importDate = parseImportDate(row?.[8]);
    batches.push({ row, productID, unitCost, available, importDate });
  }
  // Sort by import date asc (FIFO). Invalid dates are pushed to the end.
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

  const barcode = barcodeInput.value.trim();
  const batches = getBatchesForBarcode(barcode);
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

  const existingIdx = cartItems.value.findIndex((ci) => String(ci.barcode) === barcode);
  if (existingIdx === -1) {
    const top = batches[0];
    const brand = top?.row?.[2] || '';
    const name = top?.row?.[3] || '';
    const category = top?.row?.[4] || '';
    // Start with qty 1
    const { allocations, totalAvailable: avail, finalQty } = computeAllocations(barcode, 1);
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
  }

  barcodeInput.value = '';
}

function focusBarcode() {
  if (barcodeInputRef.value) {
    barcodeInputRef.value.focus();
  }
}

function focusOrderCode() {
  if (orderCodeRef.value) {
    orderCodeRef.value.focus();
  }
}

async function ensureScannerSupport() {
  if (barcodeDetector.value || scannerSupportsQR.value) return true;

  // Ưu tiên BarcodeDetector nếu có
  if ('BarcodeDetector' in window) {
    try {
      const formats = await window.BarcodeDetector.getSupportedFormats();
      if (formats.includes('qr_code')) {
        barcodeDetector.value = new window.BarcodeDetector({ formats: ['qr_code'] });
        scannerSupportsQR.value = true;
        scannerMode.value = 'detector';
        scannerError.value = '';
        return true;
      }
    } catch (err) {
      console.error('BarcodeDetector support error:', err);
    }
  }

  // Fallback: dùng thư viện ZXing
  try {
    if (!zxingReader.value) {
      const mod = await import('@zxing/browser');
      zxingLib.value = mod;
      zxingReader.value = new mod.BrowserMultiFormatReader();
    }
    scannerSupportsQR.value = true;
    scannerMode.value = 'zxing';
    scannerError.value = '';
    return true;
  } catch (err) {
    console.error('ZXing fallback error:', err);
    scannerError.value =
      'Trình duyệt không hỗ trợ BarcodeDetector và không thể tải thư viện quét QR dự phòng.';
    scannerSupportsQR.value = false;
    return false;
  }
}

function stopOrderCodeScanner() {
  isOrderCodeScannerOn.value = false;
  scannerStarting.value = false;
  if (scannerIntervalId.value) {
    clearInterval(scannerIntervalId.value);
    scannerIntervalId.value = null;
  }
  if (zxingControls.value) {
    try {
      zxingControls.value(); // hàm stop trả về từ ZXing
    } catch (err) {
      console.warn('Stop ZXing error:', err);
    }
    zxingControls.value = null;
  }
  if (zxingReader.value) {
    try {
      zxingReader.value.reset();
    } catch (err) {
      console.warn('Reset ZXing error:', err);
    }
  }
  if (videoStream.value) {
    for (const track of videoStream.value.getTracks()) {
      track.stop();
    }
    videoStream.value = null;
  }
}

async function startOrderCodeScanner() {
  if (scanLockedUntilSubmit.value) {
    showMessage('Đã quét mã. Hoàn tất đơn trước khi quét tiếp.', 'error');
    return;
  }
  const supported = await ensureScannerSupport();
  if (!supported) return;
  scannerStarting.value = true;
  try {
    // Yêu cầu quyền trước để hiện prompt rõ ràng
    const preStream = await requestCameraPermission();
    if (!preStream) {
      scannerStarting.value = false;
      return;
    }
    // Dừng stream vừa mở (ZXing sẽ tự mở lại nếu cần)
    for (const track of preStream.getTracks()) {
      track.stop();
    }

    // Hiển thị video preview trước khi gắn stream để ref tồn tại
    isOrderCodeScannerOn.value = true;
    await nextTick();
    if (!orderCodeVideoRef.value) {
      scannerError.value = 'Không khởi tạo được khung camera.';
      stopOrderCodeScanner();
      return;
    }

    const constraints = {
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: false,
    };

    if (scannerMode.value === 'detector') {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      videoStream.value = stream;
      orderCodeVideoRef.value.srcObject = stream;
      await orderCodeVideoRef.value.play();
      scannerError.value = '';
      scannerIntervalId.value = window.setInterval(async () => {
        if (!barcodeDetector.value || !orderCodeVideoRef.value) return;
        try {
          const codes = await barcodeDetector.value.detect(orderCodeVideoRef.value);
          if (Array.isArray(codes) && codes.length > 0) {
            const code = codes[0]?.rawValue || '';
            if (code) {
              orderForm.value.order_code = code;
              showMessage('Đã quét mã vận đơn', 'success');
              scanLockedUntilSubmit.value = true;
              stopOrderCodeScanner();
            }
          }
        } catch (err) {
          console.error('Scan error:', err);
          scannerError.value = 'Không thể đọc mã, hãy thử lại.';
        }
      }, 400);
    } else {
      if (!zxingReader.value) {
        throw new Error('Không khởi tạo được trình quét ZXing.');
      }
      isOrderCodeScannerOn.value = true;
      scannerError.value = '';
      zxingControls.value = await zxingReader.value.decodeFromVideoDevice(
        undefined,
        orderCodeVideoRef.value,
        (result, err) => {
          if (result) {
            const code = result.getText?.() || result.text || '';
            if (code) {
              orderForm.value.order_code = code;
              showMessage('Đã quét mã vận đơn', 'success');
              scanLockedUntilSubmit.value = true;
              stopOrderCodeScanner();
            }
          } else if (err) {
            const NotFound = zxingLib.value?.NotFoundException;
            if (!(NotFound && err instanceof NotFound)) {
              console.warn('ZXing scan warning:', err);
            }
          }
        },
      );
    }
  } catch (err) {
    console.error('Camera error:', err);
    scannerError.value = 'Không thể mở camera. Vui lòng kiểm tra quyền truy cập.';
  } finally {
    scannerStarting.value = false;
  }
}

function toggleOrderCodeScanner() {
  if (isOrderCodeScannerOn.value) {
    stopOrderCodeScanner();
  } else {
    showMessage('Trình duyệt sẽ yêu cầu quyền camera để quét mã vận đơn.', 'success');
    startOrderCodeScanner();
  }
}

async function requestCameraPermission() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    scannerError.value = 'Thiết bị không cho phép truy cập camera.';
    return null;
  }
  try {
    if (navigator.permissions && navigator.permissions.query) {
      try {
        const status = await navigator.permissions.query({ name: 'camera' });
        if (status.state === 'denied') {
          scannerError.value = 'Trình duyệt đã chặn camera. Hãy cấp quyền và thử lại.';
          return null;
        }
      } catch (err) {
        console.warn('Permission query error:', err);
      }
    }
    return await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
      audio: false,
    });
  } catch (err) {
    console.error('Camera error:', err);
    if (err.name === 'NotAllowedError' || err.name === 'SecurityError') {
      scannerError.value = 'Hãy cho phép quyền camera để quét mã vận đơn.';
    } else {
      scannerError.value = 'Không thể mở camera. Kiểm tra kết nối hoặc quyền truy cập.';
    }
    return null;
  }
}

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

  loading.value = true;
  try {
    const orderID = generateUniqueId();
    const inputOrderCode = (orderForm.value.order_code || '').trim();
    const orderCode = inputOrderCode || `ORD-${Date.now()}`;

    // Ghi đơn hàng
    await ordersAPI.create({
      orderID,
      customer_name: orderForm.value.customer_name,
      order_code: orderCode,
      package_date: orderForm.value.package_date,
      total_cost: totalCost.value,
      note: '',
    });

    // Ghi chi tiết sản phẩm đã bán theo phân bổ
    const updates = [];
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

        const importRowData = imports.value.find((imp) => imp[0] === al.productID);
        if (importRowData) {
          const rowIndex = imports.value.indexOf(importRowData) + 2; // 1-based, +1 for header
          const currentQtySold = parseInt(importRowData[10]) || 0;
          const newQtySold = currentQtySold + al.qty;
          const newAvailableQty = parseInt(importRowData[5]) - newQtySold;
          updates.push({
            row: rowIndex,
            data: { qty_sold: newQtySold, available_qty: newAvailableQty },
          });
        }
      }
    }

    if (updates.length > 0) {
      await importsAPI.updateRows(updates);
      applyLocalImportUpdates(updates);
    }

    showMessage(`Tạo đơn hàng thành công! Mã: ${orderCode}`, 'success');
    orderForm.value = {
      customer_name: '',
      order_code: '',
      package_date: new Date().toISOString().split('T')[0],
    };
    scanLockedUntilSubmit.value = false;
    cartItems.value = [];
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

async function handleReturnOrder(orderCode) {
  if (!orderCode || isReturning(orderCode) || isReturned(orderCode)) return;

  const items = orderProducts(orderCode);
  if (!items || items.length === 0) {
    showMessage('Đơn này không có sản phẩm để trả hàng', 'error');
    return;
  }

  const confirmed = confirm('Xác nhận trả hàng/hoàn đơn? Hệ thống sẽ cộng lại tồn kho.');
  if (!confirmed) return;

  addReturning(orderCode);
  try {
    await loadImports(); // lấy dữ liệu tồn kho mới nhất

    const qtyByProduct = {};
    for (const item of items) {
      if (!item.productID) continue;
      const pid = String(item.productID);
      qtyByProduct[pid] = (qtyByProduct[pid] || 0) + (Number(item.qty_sold) || 0);
    }

    const updates = [];
    for (const [productID, qtyReturn] of Object.entries(qtyByProduct)) {
      const importRowData = imports.value.find((imp) => String(imp[0]) === productID);
      if (!importRowData) continue;

      const rowIndex = imports.value.indexOf(importRowData) + 2; // 1-based + header
      const totalQty = parseInt(importRowData[5], 10) || 0;
      const currentQtySold = parseInt(importRowData[10], 10) || 0;
      const qtyToDeduct = Math.min(qtyReturn, currentQtySold);
      const newQtySold = Math.max(0, currentQtySold - qtyToDeduct);
      const newAvailableQty = Math.max(0, totalQty - newQtySold);

      updates.push({
        row: rowIndex,
        data: { qty_sold: newQtySold, available_qty: newAvailableQty },
      });
    }

    if (updates.length === 0) {
      showMessage('Không tìm thấy sản phẩm tương ứng để cộng lại tồn kho', 'error');
      return;
    }

    await importsAPI.updateRows(updates);
    applyLocalImportUpdates(updates);
    // Xóa các dòng sold đã ghi cho đơn
    const soldRowsToDelete = (soldHistory.value || [])
      .filter((s) => String(s.order_code) === String(orderCode))
      .map((s) => s.rowIndex)
      .filter((r) => Number.isInteger(r));
    if (soldRowsToDelete.length > 0) {
      await soldAPI.deleteRows(soldRowsToDelete);
    }
    // Xóa luôn dòng order để không thể nhập lại
    const orderRowIndex = (orderHistory.value.find((o) => o.order_code === orderCode) || {}).rowIndex;
    if (orderRowIndex) {
      await ordersAPI.deleteRows([orderRowIndex]);
    }
    showMessage('Đã trả hàng, cộng lại tồn kho và xoá đơn', 'success');
    markReturned(orderCode);
    await Promise.all([loadImports(), loadOrderHistory()]);
  } catch (error) {
    showMessage('Trả hàng thất bại: ' + error.message, 'error');
  } finally {
    removeReturning(orderCode);
  }
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}

onMounted(() => {
  loadImports();
  loadOrderHistory();
});

onUnmounted(() => {
  stopOrderCodeScanner();
});
</script>

<style scoped>
.orders-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  background: #fafaf9;
  min-height: 100vh;
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

.subsection-title {
  font-size: 16px;
  font-weight: 600;
  color: #2d5016;
  margin: 20px 0 12px 0;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.order-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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

.empty-cart {
  padding: 24px;
  text-align: center;
  color: #999;
  font-size: 15px;
  background: #fafaf9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  background: #fafaf9;
  border-radius: 8px;
  border: 1px solid #eee;
}

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

/* Chips to indicate batch/product and unit cost */
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

.chip-id {
  background: #eef2ff;
  color: #3730a3;
  border-color: #c7d2fe;
}

.chip-cost {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
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

.order-summary {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 2px solid #eee;
}

.summary-row {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #2d5016;
}

.summary-label {
  color: #666;
}

.summary-value {
  color: #86c06b;
  font-size: 17px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-submit,
.btn-secondary {
  flex: 1;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-submit {
  background: linear-gradient(135deg, #86c06b 0%, #6db046 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(134, 192, 107, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  border: 1px solid #ddd;
  color: #555;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.btn-scan-toggle {
  padding: 8px 12px;
  background: #e0f2fe;
  color: #0f172a;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-scan-toggle:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-scan-toggle:not(:disabled):hover {
  background: #bae6fd;
}

.scanner-preview {
  margin-top: 10px;
  border: 1px dashed #bfdbfe;
  border-radius: 10px;
  overflow: hidden;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
}

.scanner-video {
  width: 100%;
  max-height: 240px;
  object-fit: cover;
  background: #000;
}

.scanner-hint {
  padding: 6px 10px;
  font-size: 13px;
  color: #0f172a;
  background: #e0f2fe;
  text-align: center;
}

.scanner-error {
  margin-top: 6px;
  color: #b91c1c;
  font-size: 13px;
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

.history-section {
  margin-top: 24px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 13px;
  color: #4b5563;
}

.filter-input {
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-secondary.small {
  padding: 8px 10px;
  font-size: 13px;
}

.btn-refresh {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #cbd5f5;
  background: #eef2ff;
  color: #3730a3;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-refresh:not(:disabled):hover {
  background: #dbe4ff;
}

.history-empty {
  padding: 24px;
  text-align: center;
  color: #6b7280;
  border: 1px dashed #d1d5db;
  border-radius: 10px;
  background: #f9fafb;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
  background: #fdfdfc;
}

.history-card-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.history-card-info {
  flex: 1;
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-order-code {
  font-size: 18px;
  font-weight: 700;
  color: #14532d;
}

.history-info-row {
  margin-top: 6px;
  font-size: 13px;
  color: #4b5563;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn-return {
  border: 1px solid #fcd34d;
  background: #fef3c7;
  color: #92400e;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-return:hover:not(:disabled) {
  background: #fde68a;
}

.btn-return:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-toggle {
  border: none;
  background: #86c06b;
  color: white;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-toggle:hover {
  background: #6db046;
}

.history-details {
  margin-top: 12px;
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.history-products {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-product {
  display: grid;
  grid-template-columns: 2fr 1fr 100px;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.history-product-name {
  font-weight: 600;
  color: #1f2937;
}

.history-product-meta {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.history-product-qty,
.history-product-total {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.history-empty-products {
  padding: 12px;
  background: #fef3c7;
  border: 1px dashed #fcd34d;
  color: #92400e;
  border-radius: 8px;
  font-size: 13px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

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

  .history-card-main {
    flex-direction: column;
    align-items: flex-start;
  }

  .history-product {
    grid-template-columns: 1fr;
  }

  .history-info-row {
    flex-direction: column;
    gap: 6px;
  }
}

@media (max-width: 640px) {
  .orders-container {
    padding: 12px;
  }

  .cart-item {
    grid-template-columns: 1fr;
  }
}
</style>
