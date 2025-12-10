<template>
  <div class="imports-container">
    <h1 class="page-title">📦 Nhập Hàng</h1>

    <!-- Form Nhập Hàng -->
    <div class="form-section">
      <h2 class="section-title">Thêm Lô Hàng Mới</h2>
      <div class="import-form" role="form">
        <div class="form-group">
          <label for="barcode">Mã Barcode</label>
          <div class="barcode-row">
            <input
              v-model="barcodeInputValue"
              type="text"
              id="barcode"
              placeholder="Nhập hoặc quét barcode"
              class="input-field"
              ref="barcodeInput"
              @keyup.enter.prevent="handleBarcodeScan"
              :disabled="loading"
            />
            <button
              type="button"
              class="btn-add-barcode"
              @click="handleBarcodeScan"
              :disabled="loading || !barcodeInputValue.trim()"
            >
              + Thêm
            </button>
          </div>
          <p class="input-hint">
            Quét liên tiếp mã vạch, hệ thống sẽ tự lấy thông tin sản phẩm và thêm vào danh sách bên dưới.
          </p>
        </div>

        <div v-if="pendingItems.length > 0" class="pending-list">
          <table class="imports-table pending-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Barcode</th>
                <th>Tên Sản Phẩm</th>
                <th>Brand</th>
                <th>Danh Mục</th>
                <th>Nhập</th>
                <th>Giá Vốn</th>
                <th>Hòa Vốn</th>
                <th>Ngày Nhập</th>
                <th>Ghi Chú</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in pendingItems" :key="item.barcode">
                <td>{{ idx + 1 }}</td>
                <td>{{ item.barcode }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.brand }}</td>
                <td>{{ item.category }}</td>
                <td>
                  <input
                    v-model.number="item.qty_in"
                    type="number"
                    min="1"
                    class="input-field inline-input"
                    :disabled="loading"
                    @change="ensureMinimumQuantity(item)"
                  />
                </td>
                <td>
                  <input
                    v-model.number="item.unit_cost"
                    type="number"
                    min="0"
                    step="0.01"
                    class="input-field inline-input"
                    :disabled="loading"
                    @input="handleUnitCostChange(item)"
                  />
                </td>
                <td>
                  <input
                    v-model.number="item.break_even_price"
                    type="number"
                    min="0"
                    step="0.01"
                    class="input-field inline-input"
                    :disabled="loading"
                    @input="markCustomBreakEven(item)"
                  />
                </td>
                <td>
                  <input v-model="item.import_date" type="date" class="input-field inline-input" :disabled="loading" />
                </td>
                <td>
                  <input
                    v-model="item.note"
                    type="text"
                    placeholder="Ghi chú..."
                    class="input-field inline-input"
                    :disabled="loading"
                  />
                </td>
                <td>
                  <button
                    type="button"
                    class="btn-delete"
                    @click="removePendingItem(item.barcode)"
                    :disabled="loading"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="pending-empty">
          Chưa có sản phẩm trong lô nhập. Quét barcode để bắt đầu.
        </div>

        <div class="form-actions">
          <button
            type="button"
            class="btn-submit"
            :disabled="loading || pendingItems.length === 0"
            @click="submitForm"
          >
            {{ loading ? 'Đang lưu...' : '✓ Nhập ' + pendingItems.length + ' sản phẩm' }}
          </button>
          <button
            type="button"
            class="btn-reset"
            :disabled="loading || pendingItems.length === 0"
            @click="resetForm"
          >
            ↺ Reset
          </button>
        </div>
      </div>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>

    <!-- Danh Sách Lô Hàng -->
    <div class="table-section">
      <div class="table-header">
        <h2 class="section-title">Danh Sách Lô Hàng</h2>
        <button @click="loadImports" class="btn-refresh">🔄 Làm Mới</button>
      </div>

      <div class="filters-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm theo barcode, tên sản phẩm..."
          class="search-input"
        />
        <div class="month-filter">
          <label for="importMonth">Tháng</label>
          <input
            id="importMonth"
            v-model="selectedMonth"
            type="month"
            class="month-input"
          />
        </div>
      </div>

      <div v-if="loading" class="loading">Đang tải dữ liệu...</div>

      <div v-else-if="filteredImports.length === 0" class="empty-state">
        Không có dữ liệu
      </div>

      <div v-else class="table-wrapper">
        <table class="imports-table">
          <thead>
            <tr>
              <th>ProductID</th>
              <th>Barcode</th>
              <th>Tên Sản Phẩm</th>
              <th>Brand</th>
              <th>Danh Mục</th>
              <th>Nhập</th>
              <th>Đã Bán</th>
              <th>Còn</th>
              <th>Giá Vốn</th>
              <th>Hòa Vốn</th>
              <th>Ngày Nhập</th>
              <th>Ghi Chú</th>
              <th>Hành Động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in filteredImports" :key="item[0]">
              <td class="product-id">{{ item[0] }}</td>
              <td>{{ item[1] }}</td>
              <td>{{ item[3] }}</td>
              <td>{{ item[2] }}</td>
              <td>{{ item[4] }}</td>
              <td>{{ item[5] }}</td>
              <td>{{ item[10] }}</td>
              <td>{{ item[11] }}</td>
              <td>{{ formatNumber(item[6]) }}</td>
              <td>{{ formatNumber(item[7]) }}</td>
              <td>{{ item[8] }}</td>
              <td>{{ item[9] }}</td>
              <td>
                <button @click="openEditModal(item)" class="btn-refresh">✏️</button>
                <button @click="deleteImport(item)" class="btn-delete">X</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal chỉnh sửa -->
    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Chỉnh Sửa Lô Hàng</h3>
          <button class="modal-close" @click="closeEditModal">✖</button>
        </div>
        <div class="modal-body">
          <div class="modal-row">
            <div class="modal-group">
              <label>ProductID</label>
              <div class="readonly-field">{{ editingId }}</div>
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Barcode</label>
              <div class="readonly-field">{{ editForm.barcode }}</div>
            </div>
            <div class="modal-group">
              <label>Brand</label>
              <div class="readonly-field">{{ editForm.brand }}</div>
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Tên Sản Phẩm</label>
              <div class="readonly-field">{{ editForm.name }}</div>
            </div>
            <div class="modal-group">
              <label>Danh Mục</label>
              <div class="readonly-field">{{ editForm.category }}</div>
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Số Lượng Nhập</label>
              <input v-model.number="editForm.qty_in" type="number" min="0" class="input-field" />
            </div>
            <div class="modal-group">
              <label>Giá Vốn (₫)</label>
              <input v-model.number="editForm.unit_cost" type="number" step="0.01" min="0" class="input-field" />
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Đã Bán</label>
              <div class="readonly-field">{{ editForm.sold_count }}</div>
            </div>
            <div class="modal-group">
              <label>Còn Tồn</label>
              <div class="readonly-field">{{ Math.max(editForm.qty_in - editForm.sold_count, 0) }}</div>
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Giá Hòa Vốn (₫)</label>
              <input
                v-model.number="editForm.break_even_price"
                type="number"
                step="0.01"
                min="0"
                class="readonly-field"
                :readonly="true"
              />
            </div>
            <div class="modal-group">
              <label>Ngày Nhập</label>
              <input v-model="editForm.import_date" type="date" class="input-field" />
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group" style="grid-column: 1 / -1;">
              <label>Ghi Chú</label>
              <input v-model="editForm.note" class="input-field" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-refresh" @click="closeEditModal" :disabled="loading">Hủy</button>
          <button class="btn-submit" @click="saveEdit" :disabled="loading">Lưu</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { importsAPI, productsAPI } from '../services/api';

const pendingItems = ref([]);
const barcodeInputValue = ref('');
const imports = ref([]);
const loading = ref(false);
const message = ref(null);
const searchQuery = ref('');
const selectedMonth = ref('');

const editingId = ref(null);
const editForm = ref({
  barcode: '',
  brand: '',
  name: '',
  category: '',
  qty_in: 0,
  unit_cost: 0,
  break_even_price: 0,
  import_date: '',
  note: '',
  sold_count: 0,
});
const isEditModalOpen = ref(false);
const barcodeInput = ref(null);

watch(
  () => editForm.value.unit_cost,
  (val) => {
    const unitCost = Number(val) || 0;
    editForm.value.unit_cost = unitCost;
    editForm.value.break_even_price = unitCost > 0 ? +(unitCost / 0.7).toFixed(2) : 0;
  }
);

const filteredImports = computed(() => {
  const query = (searchQuery.value || '').trim().toLowerCase();
  const monthFilter = selectedMonth.value;

  return imports.value
    .filter((item) => {
      const barcode = (item[1] || '').toString().toLowerCase();
      const name = (item[3] || '').toString().toLowerCase();
      const matchesQuery = !query || barcode.includes(query) || name.includes(query);

      if (!matchesQuery) return false;
      if (!monthFilter) return true;

      const isoDate = getItemImportDateISO(item);
      return isoDate ? isoDate.startsWith(monthFilter) : false;
    })
    .sort((a, b) => getItemDateValue(b) - getItemDateValue(a));
});

const productsHeader = ref([]);
const productsData = ref([]);
const productsReady = ref(false);

function headerIndex(name) {
  if (!productsHeader.value || productsHeader.value.length === 0) return -1;
  const lower = name.toLowerCase();
  return productsHeader.value.findIndex((h) => String(h).toLowerCase() === lower);
}

function getCell(row, colName) {
  const idx = headerIndex(colName);
  if (idx < 0) return '';
  return row && row[idx] !== undefined && row[idx] !== null ? String(row[idx]) : '';
}

async function loadProducts() {
  try {
    const result = await productsAPI.getAll();
    productsHeader.value = result.header || [];
    productsData.value = result.data || [];
    productsReady.value = productsHeader.value.length > 0;
  } catch (e) {
    // ignore soft-fail
  }
}

function getDefaultImportDate() {
  try {
    return new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Ho_Chi_Minh',
    }).format(new Date());
  } catch (_) {
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
    return local.toISOString().split('T')[0];
  }
}

function getItemImportDateISO(item) {
  if (!item || !item[8]) return '';
  return toISODateFromVN(String(item[8]));
}

function getItemDateValue(item) {
  const iso = getItemImportDateISO(item);
  if (!iso) return 0;
  const ts = Date.parse(iso);
  return Number.isNaN(ts) ? 0 : ts;
}

function focusBarcodeInput() {
  nextTick(() => {
    try {
      barcodeInput.value && barcodeInput.value.focus && barcodeInput.value.focus();
    } catch (_) {}
  });
}

function createPendingItemFromRow(row) {
  return {
    barcode: getCell(row, 'barcode').trim(),
    brand: getCell(row, 'hãng').trim(),
    name: getCell(row, 'tên').trim(),
    category: getCell(row, 'phân loại').trim(),
    qty_in: 1,
    unit_cost: 0,
    break_even_price: 0,
    import_date: getDefaultImportDate(),
    note: '',
    hasCustomBreakEven: false,
  };
}

async function handleBarcodeScan() {
  const code = (barcodeInputValue.value || '').trim();
  if (!code) return;

  const existing = pendingItems.value.find((item) => item.barcode === code);
  if (existing) {
    existing.qty_in += 1;
    ensureMinimumQuantity(existing);
    barcodeInputValue.value = '';
    focusBarcodeInput();
    return;
  }

  if (!productsReady.value) {
    await loadProducts();
  }
  const row = findProductRowByBarcode(code);
  if (!row) {
    showMessage(`Không tìm thấy sản phẩm với barcode ${code}`, 'error');
    barcodeInputValue.value = '';
    focusBarcodeInput();
    return;
  }

  pendingItems.value.unshift(createPendingItemFromRow(row));
  barcodeInputValue.value = '';
  focusBarcodeInput();
}

function ensureMinimumQuantity(item) {
  const qty = Number(item.qty_in) || 0;
  item.qty_in = qty < 1 ? 1 : qty;
}

function handleUnitCostChange(item) {
  item.unit_cost = Number(item.unit_cost) || 0;
  if (!item.hasCustomBreakEven) {
    item.break_even_price = item.unit_cost > 0 ? +(item.unit_cost / 0.7).toFixed(2) : 0;
  }
}

function markCustomBreakEven(item) {
  item.hasCustomBreakEven = true;
}

function removePendingItem(barcode) {
  pendingItems.value = pendingItems.value.filter((item) => item.barcode !== barcode);
}

async function loadImports() {
  loading.value = true;
  try {
    const result = await importsAPI.getAll();
    imports.value = result.data || [];
  } catch (error) {
    showMessage('Lỗi tải dữ liệu', 'error');
  } finally {
    loading.value = false;
  }
}

async function submitForm() {
  if (pendingItems.value.length === 0) {
    showMessage('Vui lòng thêm ít nhất 1 sản phẩm trước khi lưu', 'error');
    focusBarcodeInput();
    return;
  }

  loading.value = true;
  try {
    const now = new Date();
    const createdAt = now.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });

    for (const item of pendingItems.value) {
      const payload = {
        barcode: item.barcode,
        brand: item.brand,
        name: item.name,
        category: item.category,
        qty_in: item.qty_in,
        unit_cost: item.unit_cost,
        break_even_price: item.break_even_price,
        import_date: item.import_date,
        note: item.note,
        created_at: createdAt,
      };
      await importsAPI.create(payload);
    }

    showMessage('Thêm lô hàng thành công!', 'success');
    resetForm();
    await loadImports();
  } catch (error) {
    showMessage('Lỗi: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

function findProductRowByBarcode(barcode) {
  const bcIdx = headerIndex('barcode');
  if (bcIdx < 0) return null;
  const target = String(barcode || '').trim();
  if (!target) return null;
  return productsData.value.find((r) => r && String(r[bcIdx]).trim() === target) || null;
}

function toISODateFromVN(d) {
  if (!d) return '';
  const parts = d.split('/');
  if (parts.length === 3) {
    const [dd, mm, yyyy] = parts;
    return `${yyyy}-${mm.padStart(2, '0')}-${dd.padStart(2, '0')}`;
  }
  return d;
}

function resetForm() {
  pendingItems.value = [];
  barcodeInputValue.value = '';
  focusBarcodeInput();
}

function openEditModal(item) {
  editingId.value = item[0];
  editForm.value = {
    barcode: item[1] || '',
    brand: item[2] || '',
    name: item[3] || '',
    category: item[4] || '',
    qty_in: Number(item[5] || 0),
    unit_cost: Number(item[6] || 0),
    break_even_price: Number(item[7] || 0),
    import_date: toISODateFromVN(item[8] || ''),
    note: item[9] || '',
    sold_count: Number(item[10] || 0),
  };
  isEditModalOpen.value = true;
}

function closeEditModal() {
  isEditModalOpen.value = false;
  editingId.value = null;
}

async function saveEdit() {
  if (!editingId.value) return;
  if (Number(editForm.value.qty_in) < Number(editForm.value.sold_count)) {
    showMessage('Số lượng nhập không thể nhỏ hơn số sản phẩm đã bán', 'error');
    return;
  }
  loading.value = true;
  try {
    const idxInAll = imports.value.findIndex((r) => r[0] === editingId.value);
    if (idxInAll === -1) throw new Error('Không tìm thấy dòng cần cập nhật');
    const actualRow = idxInAll + 2;
    const payload = {
      barcode: editForm.value.barcode,
      brand: editForm.value.brand,
      name: editForm.value.name,
      category: editForm.value.category,
      qty_in: editForm.value.qty_in,
      unit_cost: editForm.value.unit_cost,
      break_even_price: editForm.value.break_even_price,
      import_date: editForm.value.import_date,
      note: editForm.value.note,
    };
    await importsAPI.updateRows([{ row: actualRow, data: payload }]);
    showMessage('Đã cập nhật lô hàng', 'success');
    closeEditModal();
    await loadImports();
  } catch (error) {
    showMessage('Lỗi cập nhật: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

async function deleteImport(item) {
  if (!confirm('Bạn chắc chắn muốn xóa?')) return;
  loading.value = true;
  try {
    const idxInAll = imports.value.findIndex((r) => r[0] === item[0]);
    if (idxInAll === -1) throw new Error('Không tìm thấy dòng cần xóa');
    const actualRow = idxInAll + 2;
    await importsAPI.deleteRows([actualRow]);
    showMessage('Xóa thành công!', 'success');
    await loadImports();
  } catch (error) {
    showMessage('Lỗi xóa: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

function showMessage(text, type) {
  message.value = { text, type };
  setTimeout(() => {
    message.value = null;
  }, 3000);
}

function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString('vi-VN') : num;
}

onMounted(() => {
  loadImports();
  loadProducts();
  focusBarcodeInput();
});
</script>

<style scoped>
.imports-container {
  width: 100%;
  /* widen to use more horizontal space */
  max-width: 1600px;
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
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 16px;
}

.import-form {
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

.barcode-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-add-barcode {
  padding: 10px 18px;
  background: #e0f2fe;
  color: #0369a1;
  border: 1px solid #bae6fd;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.btn-add-barcode:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-add-barcode:not(:disabled):hover {
  background: #bae6fd;
  transform: translateY(-1px);
}

.input-hint {
  font-size: 13px;
  color: #6b7280;
  margin-top: 6px;
}

.pending-list {
  margin-top: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  overflow-x: auto;
}

.pending-table th,
.pending-table td {
  white-space: nowrap;
}

.pending-empty {
  margin: 16px 0;
  padding: 16px;
  border: 1px dashed #d1d5db;
  border-radius: 12px;
  color: #6b7280;
  background: #f9fafb;
  text-align: center;
}

.inline-input {
  min-width: 110px;
}

.btn-submit {
  padding: 12px 16px;
  background: linear-gradient(135deg, #86c06b 0%, #6db046 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(134, 192, 107, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-reset {
  padding: 12px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
}

.btn-reset:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-reset:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.suggestions {
  margin-top: 6px;
  border: 1px solid #e5e7eb;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.suggestions-title {
  font-size: 13px;
  color: #6b7280;
  padding: 6px 8px;
  border-bottom: 1px solid #f3f4f6;
  background: #f9fafb;
}

.suggestion-item {
  padding: 8px 10px;
  cursor: pointer;
}

.suggestion-item:hover {
  background: #f3f4f6;
}

.suggestion-line {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #111827;
}

.s-badge {
  font-size: 13px;
  color: #065f46;
  background: #d1fae5;
  border: 1px solid #a7f3d0;
  border-radius: 6px;
  padding: 2px 6px;
}

.s-name {
  font-size: 15px;
}

.suggestion-meta {
  font-size: 13px;
  color: #6b7280;
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

.table-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.btn-refresh {
  padding: 8px 15px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e5e7eb;
}

.filters-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: flex-end;
  margin-bottom: 16px;
}

.search-input {
  flex: 1;
  min-width: 240px;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
}

.search-input:focus,
.month-input:focus {
  outline: none;
  border-color: #86c06b;
  box-shadow: 0 0 0 3px rgba(134, 192, 107, 0.1);
}

.month-filter {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 180px;
}

.month-filter label {
  font-size: 13px;
  color: #555;
}

.month-input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
}

.loading,
.empty-state {
  padding: 32px;
  text-align: center;
  color: #999;
  font-size: 15px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #eee;
}

.imports-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.imports-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #eee;
}

.imports-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.imports-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
  word-break: break-word;
}

.product-id {
  font-weight: 500;
  color: #2d5016;
}

.btn-delete {
  padding: 8px 20px;
  margin-left: 10px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: #fecaca;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 1000;
}

.modal {
  background: #fff;
  width: 100%;
  max-width: 760px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #eee;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
}

.modal-body {
  padding: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #eee;
}

.modal-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 12px;
}

.modal-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.readonly-field {
  padding: 10px 12px;
  background: #f9fafb;
  border: 1px solid #eee;
  border-radius: 8px;
  color: #555;
  font-size: 15px;
}

@media (max-width: 640px) {
  .imports-container {
    padding: 12px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  /* stack modal fields and ensure full width on mobile */
  .modal {
    max-width: 100%;
  }
  .modal-row {
    grid-template-columns: 1fr;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .imports-table {
    font-size: 13px;
  }

  .imports-table th,
  .imports-table td {
    padding: 8px 6px;
  }
}

/* on wide screens, stretch container near full device width */
@media (min-width: 1440px) {
  .imports-container {
    max-width: 96vw;
  }
}
</style>
