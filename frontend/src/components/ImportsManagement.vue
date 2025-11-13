<template>
  <div class="imports-container">
    <h1 class="page-title">📦 Nhập Hàng</h1>

    <!-- Form Nhập Hàng -->
    <div class="form-section">
      <h2 class="section-title">Thêm Lô Hàng Mới</h2>
      <form @submit.prevent="submitForm" class="import-form">
        <div class="form-group">
          <label for="barcode">Mã Barcode</label>
          <input
            v-model="form.barcode"
            type="text"
            id="barcode"
            placeholder="Nhập hoặc quét barcode"
            required
            class="input-field"
            ref="barcodeInput"
          />
          <!-- Gợi ý sản phẩm theo barcode -->
          <div v-if="barcodeSuggestions.length > 0" class="suggestions">
            <div class="suggestions-title">Gợi ý sản phẩm trùng barcode:</div>
            <div
              v-for="(row, i) in barcodeSuggestions"
              :key="i"
              class="suggestion-item"
              @click="selectSuggestedProduct(row)"
            >
              <div class="suggestion-line">
                <span class="s-badge">{{ getCell(row, 'barcode') }}</span>
                <span class="s-name">{{ getCell(row, 'tên') }}</span>
              </div>
              <div class="suggestion-meta">
                <span>{{ getCell(row, 'hãng') }}</span> ·
                <span>{{ getCell(row, 'phân loại') }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="brand">Thương Hiệu</label>
            <input
              v-model="form.brand"
              type="text"
              id="brand"
              placeholder="Brand"
              required
              class="input-field"
              list="brandOptions"
            />
            <datalist id="brandOptions">
              <option v-for="b in uniqueBrands" :key="b" :value="b" />
            </datalist>
          </div>
          <div class="form-group">
            <label for="name">Tên Sản Phẩm</label>
            <input
              v-model="form.name"
              type="text"
              id="name"
              placeholder="Tên sản phẩm"
              required
              class="input-field"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="category">Danh Mục</label>
            <input
              v-model="form.category"
              type="text"
              id="category"
              placeholder="Danh mục"
              required
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label for="qty">Số Lượng Nhập</label>
            <input
              v-model.number="form.qty_in"
              type="number"
              id="qty"
              placeholder="0"
              required
              min="1"
              class="input-field"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="unitCost">Giá Vốn (₫)</label>
            <input
              v-model.number="form.unit_cost"
              type="number"
              id="unitCost"
              placeholder="0"
              required
              min="0"
              step="0.01"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label for="breakEven">Giá Hòa Vốn (₫)</label>
            <input
              v-model.number="form.break_even_price"
              type="number"
              id="breakEven"
              placeholder="0"
              min="0"
              step="0.01"
              class="input-field"
              @input="hasCustomBreakEven = true"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="importDate">Ngày Nhập</label>
            <input
              v-model="form.import_date"
              type="date"
              id="importDate"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label for="note">Ghi Chú</label>
            <input
              v-model="form.note"
              type="text"
              id="note"
              placeholder="Ghi chú..."
              class="input-field"
            />
          </div>
        </div>

        <div class="form- ">
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? 'Đang lưu...' : '✓ Thêm Lô Hàng' }}
          </button>
          <button type="button" class="btn-reset" :disabled="loading" @click="resetForm">
            ↺ Reset
          </button>
        </div>
      </form>

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

      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm theo barcode, tên sản phẩm..."
          class="search-input"
        />
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
              <input v-model="editForm.barcode" class="input-field" />
            </div>
            <div class="modal-group">
              <label>Brand</label>
              <input v-model="editForm.brand" class="input-field" />
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Tên Sản Phẩm</label>
              <input v-model="editForm.name" class="input-field" />
            </div>
            <div class="modal-group">
              <label>Danh Mục</label>
              <input v-model="editForm.category" class="input-field" />
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
              <label>Giá Hòa Vốn (₫)</label>
              <input v-model.number="editForm.break_even_price" type="number" step="0.01" min="0" class="input-field" />
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { importsAPI, productsAPI } from '../services/api';

const form = ref({
  barcode: '',
  brand: '',
  name: '',
  category: '',
  qty_in: 1,
  unit_cost: 0,
  break_even_price: 0,
  import_date: new Date().toISOString().split('T')[0],
  note: '',
});

const imports = ref([]);
const loading = ref(false);
const message = ref(null);
const searchQuery = ref('');
const hasCustomBreakEven = ref(false);

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
});
const isEditModalOpen = ref(false);
const barcodeInput = ref(null);

const filteredImports = computed(() => {
  return imports.value.filter((item) => {
    const query = searchQuery.value.toLowerCase();
    return (
      item[1].toLowerCase().includes(query) ||
      item[3].toLowerCase().includes(query)
    );
  });
});

// Danh sách brand đã từng nhập (từ bảng imports)
const uniqueBrands = computed(() => {
  const set = new Set(
    imports.value
      .map((r) => (r && typeof r[2] === 'string' ? r[2].trim() : ''))
      .filter((b) => b)
  );
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'vi', { sensitivity: 'base' }));
});

// Products for auto-fill by barcode
const productsHeader = ref([]);
const productsData = ref([]);
const productsReady = ref(false);
const barcodeSuggestions = ref([]);

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
    console.log(result)
    productsHeader.value = result.header || [];
    productsData.value = result.data || [];
    productsReady.value = (productsHeader.value.length > 0);
    if ((form.value.barcode || '').trim()) {
      updateBarcodeSuggestions();
    }
  } catch (e) {
    // ignore soft-fail
  }
}

function updateBarcodeSuggestions() {
  barcodeSuggestions.value = [];
  const bcIdx = headerIndex('barcode');
  if (bcIdx < 0) return;
  const target = (form.value.barcode || '').trim();
  if (!target) return;
  const matches = productsData.value.filter((r) => r && String(r[bcIdx]).trim() === target);
  barcodeSuggestions.value = matches;
}

function fillMissingFromRow(row) {
  const brand = getCell(row, 'hãng');
  const name = getCell(row, 'tên');
  const category = getCell(row, 'phân loại');
  if (!form.value.brand && brand) form.value.brand = brand;
  if (!form.value.name && name) form.value.name = name;
  if (!form.value.category && category) form.value.category = category;
}

function selectSuggestedProduct(row) {
  fillMissingFromRow(row);
  barcodeSuggestions.value = [];
}

// Default break-even = unit_cost / 0.7 unless user edits
watch(
  () => form.value.unit_cost,
  (val) => {
    if (!hasCustomBreakEven.value) {
      const num = Number(val || 0);
      form.value.break_even_price = num > 0 ? +(num / 0.7).toFixed(2) : 0;
    }
  }
);

// Auto-fill when barcode changes and products are ready
watch(
  [() => form.value.barcode, () => productsReady.value],
  ([barcode, ready]) => {
    if (ready) {
      updateBarcodeSuggestions();
    }
  }
);

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
  loading.value = true;
  try {
    const now = new Date();
    const createdAt = now.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });

    // Nếu barcode chưa có trong products, thêm sản phẩm mới trước (không chặn luồng nếu lỗi)
    await ensureProductExists();

    await importsAPI.create({
      ...form.value,
      created_at: createdAt,
    });

    showMessage('Thêm lô hàng thành công!', 'success');
    form.value = {
      barcode: '',
      brand: '',
      name: '',
      category: '',
      qty_in: 1,
      unit_cost: 0,
      break_even_price: 0,
      import_date: new Date().toISOString().split('T')[0],
      note: '',
    };
    hasCustomBreakEven.value = false;
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

async function ensureProductExists() {
  try {
    if (!productsReady.value) {
      try {
        const result = await productsAPI.getAll();
        productsHeader.value = result.header || [];
        productsData.value = result.data || [];
        productsReady.value = (productsHeader.value.length > 0);
      } catch (_) {
        // ignore
      }
    }
    const bc = (form.value.barcode || '').trim();
    if (!bc) return;
    const found = findProductRowByBarcode(bc);
    if (found) return;

    // Dựng payload theo header của sheet sản phẩm
    const payload = {
      barcode: bc,
      'hãng': form.value.brand || '',
      'tên': form.value.name || '',
      'phân loại': form.value.category || '',
    };
    await productsAPI.create(payload);
    // Cập nhật lại cache products để các gợi ý dùng ngay dữ liệu mới
    await loadProducts();
  } catch (e) {
    // Không chặn thêm lô hàng; chỉ log mềm
    console.warn('Create product failed:', e);
  }
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
  form.value = {
    barcode: '',
    brand: '',
    name: '',
    category: '',
    qty_in: 1,
    unit_cost: 0,
    break_even_price: 0,
    import_date: new Date().toISOString().split('T')[0],
    note: '',
  };
  hasCustomBreakEven.value = false;
  barcodeSuggestions.value = [];
  nextTick(() => {
    try { barcodeInput.value && barcodeInput.value.focus && barcodeInput.value.focus(); } catch (_) {}
  });
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
  };
  isEditModalOpen.value = true;
}

function closeEditModal() {
  isEditModalOpen.value = false;
  editingId.value = null;
}

async function saveEdit() {
  if (!editingId.value) return;
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

.search-bar {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
}

.search-input:focus {
  outline: none;
  border-color: #86c06b;
  box-shadow: 0 0 0 3px rgba(134, 192, 107, 0.1);
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
