<template>
  <div class="products-container">
    <h1 class="page-title">📦 Sản Phẩm Trong Kho</h1>

    <div class="table-section">
      <div class="table-header">
        <h2 class="section-title">Danh Sách Sản Phẩm</h2>
        <div class="actions-right">
          <button @click="openAddModal" class="btn-primary">➕ Thêm</button>
          <button @click="loadProducts" class="btn-refresh">🔄 Làm Mới</button>
        </div>
      </div>

      <div class="search-bar">
        <input
          id="pm-search"
          name="search"
          v-model="searchQuery"
          type="text"
          placeholder="Tìm theo barcode, tên sản phẩm..."
          class="search-input"
        />
      </div>

      <div v-if="loading" class="loading">Đang tải dữ liệu...</div>

      <div v-else-if="filteredProducts.length === 0" class="empty-state">
        Không có sản phẩm trong kho
      </div>

      <div v-else class="table-wrapper">
        <table class="products-table">
          <thead>
            <tr>
              <th>Barcode</th>
              <th>Thương Hiệu</th>
              <th>Tên Sản Phẩm</th>
              <th>Danh Mục</th>
              <th>Đã Đăng</th>
              <th>Tồn Kho</th>
              <th>Hành Động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in filteredProducts" :key="idx" :class="{ 'row-unpublished': item[4] !== '1' }">
              <td class="barcode-cell">{{ item[0] }}</td>
              <td>{{ item[1] }}</td>
              <td>{{ item[2] }}</td>
              <td>{{ item[3] }}</td>
              <td>
                <span v-if="item[4] === '1'" class="pub-badge pub-on">✓</span>
              </td>
              <td class="qty-cell">
                <span class="qty-badge">{{ item[5] }}</span>
              </td>
              <td class="action-cell">
                <button class="btn-small" @click="openEditModal(item)">Sửa</button>
                <button class="btn-small btn-danger" @click="deleteByBarcode(item[0])">Xóa</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Modal thêm/cập nhật sản phẩm -->
  <div v-if="modalOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title">{{ isEditing ? 'Cập Nhật Sản Phẩm' : 'Thêm Sản Phẩm' }}</h3>
        <button class="modal-close" @click="closeModal">×</button>
      </div>
      <div class="modal-body">
        <div v-if="errorMessage" class="alert error-alert">{{ errorMessage }}</div>
        <div v-if="!isEditing" class="modal-row modal-row-full">
          <div class="modal-group">
            <label for="pm-copy-existing">Lấy thông tin từ sản phẩm có sẵn</label>
            <select
              id="pm-copy-existing"
              class="input-field"
              v-model="selectedTemplateIdx"
            >
              <option value="">-- Chọn sản phẩm --</option>
              <option
                v-for="option in templateOptions"
                :key="`${option.barcode}-${option.idx}`"
                :value="String(option.idx)"
              >
                {{ option.barcode }} - {{ option.brand }} {{ option.name }} ({{ option.category || 'Chưa phân loại' }})
              </option>
            </select>
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-group">
            <label for="pm-barcode">Barcode</label>
            <input id="pm-barcode" name="barcode" class="input-field" v-model="form.barcode" :readonly="isEditing" />
          </div>
          <div class="modal-group">
            <label for="pm-brand">Hãng</label>
            <div class="brand-stack" @click.stop>
              <div class="brand-input-row">
                <input
                  id="pm-brand"
                  name="brand"
                  class="input-field"
                  v-model="form.brand"
                  @input="onBrandInput"
                  placeholder="Nhập hoặc chọn hãng"
                />
                <button
                  type="button"
                  class="btn-brand-dropdown"
                  @click="toggleBrandDropdown"
                  :disabled="!brandOptions.length"
                >
                  ▼
                </button>
              </div>
              <ul v-if="brandDropdownOpen && brandOptions.length" class="brand-dropdown">
                <li v-for="brand in brandOptions" :key="brand" @click="selectBrand(brand)">
                  {{ brand }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-group">
            <label for="pm-name">Tên</label>
            <input id="pm-name" name="name" class="input-field" v-model="form.name" />
          </div>
          <div class="modal-group">
            <label for="pm-category">Phân Loại</label>
            <input id="pm-category" name="category" class="input-field" v-model="form.category" />
          </div>
        </div>
        <div class="modal-row">
          <div class="modal-group">
            <label for="pm-published">Đã Đăng</label>
            <select id="pm-published" name="published" class="input-field" v-model="form.published">
              <option value="">Chưa</option>
              <option value="1">Đã đăng</option>
            </select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="closeModal">Hủy</button>
        <button class="btn-primary" @click="saveProduct" :disabled="saving">
          {{ saving ? 'Đang lưu...' : (isEditing ? 'Lưu thay đổi' : 'Thêm mới') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { productsAPI, importsAPI } from '@/services/api';

const products = ref([]); // mảng rows [barcode, hãng, tên, phân loại, đã đăng]
const imports = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const modalOpen = ref(false);
const isEditing = ref(false);
const saving = ref(false);
const editBarcodeRef = ref('');
const selectedTemplateIdx = ref('');
const brandDropdownOpen = ref(false);
const errorMessage = ref('');
const form = ref({ barcode: '', brand: '', name: '', category: '', published: '' });
const collator = new Intl.Collator('vi', { sensitivity: 'base', usage: 'sort' });

function formatBrandValue(value) {
  return String(value || '').trim().toUpperCase();
}

// Bản đồ tồn kho theo barcode, lấy từ bảng Imports (cộng dồn available_qty)
const stockByBarcode = computed(() => {
  const m = new Map();
  for (const row of imports.value || []) {
    const barcode = (row?.[1] || '').toString();
    if (!barcode) continue;
    // available_qty ở cột L (index 11) theo định nghĩa backend
    const availableRaw = row?.[11] ?? 0;
    const available = typeof availableRaw === 'number'
      ? availableRaw
      : parseInt((availableRaw || '0').toString().replace(/,/g, ''), 10) || 0;
    m.set(barcode, (m.get(barcode) || 0) + available);
  }
  return m;
});

// Gom nhóm theo barcode từ /products (5 cột: + đã đăng), rồi gán tồn kho từ stockByBarcode
const groupedProducts = computed(() => {
  const map = new Map();
  for (const row of products.value || []) {
    const barcode = (row?.[0] || '').toString();
    const brand = formatBrandValue(row?.[1]);
    const name = row?.[2] || '';
    const category = row?.[3] || '';
    const publishedRaw = row?.[4] || '';
    const published = String(publishedRaw).trim() === '1' ? '1' : '';
    if (!barcode) continue;

    if (!map.has(barcode)) {
      // Cấu trúc hiển thị: [barcode, brand, name, category, published, totalQty]
      map.set(barcode, [barcode, brand, name, category, published, 0]);
    }
    // Luôn cập nhật tồn kho theo stockByBarcode (không lấy từ products)
    const agg = map.get(barcode);
    // Published: nếu bất kỳ dòng nào có '1' thì giữ '1'
    if (published === '1') agg[4] = '1';
    // Tồn kho ở index 5
    agg[5] = stockByBarcode.value.get(barcode) || 0;
  }
  return Array.from(map.values());
});

const templateOptions = computed(() => {
  return (products.value || [])
    .map((row, idx) => ({
      idx,
      barcode: (row?.[0] || '').toString(),
      brand: formatBrandValue(row?.[1]),
      name: row?.[2] || '',
      category: row?.[3] || '',
    }))
    .filter((option) => option.barcode || option.name);
});

const brandOptions = computed(() => {
  const set = new Set();
  for (const item of groupedProducts.value || []) {
    const brand = formatBrandValue(item?.[1]);
    if (brand) set.add(brand);
  }
  return Array.from(set).sort((a, b) => collator.compare(a, b));
});

const filteredProducts = computed(() => {
  const query = (searchQuery.value || '').toLowerCase();
  const sorted = [...groupedProducts.value].sort((a, b) => {
    const brandCompare = collator.compare(a[1] || '', b[1] || '');
    if (brandCompare !== 0) return brandCompare;
    const nameCompare = collator.compare(a[2] || '', b[2] || '');
    if (nameCompare !== 0) return nameCompare;
    return collator.compare(a[3] || '', b[3] || '');
  });
  return sorted.filter((item) => {
    return (
      (item[0] || '').toLowerCase().includes(query) ||
      (item[2] || '').toLowerCase().includes(query)
    );
  });
});

async function loadProducts() {
  loading.value = true;
  try {
    const [productsResult, importsResult] = await Promise.all([
      productsAPI.getAll(),
      importsAPI.getAll(),
    ]);
    const productsRaw = Array.isArray(productsResult?.data)
      ? productsResult.data
      : (Array.isArray(productsResult) ? productsResult : []);
    const importsRaw = Array.isArray(importsResult?.data)
      ? importsResult.data
      : (Array.isArray(importsResult) ? importsResult : []);
    products.value = productsRaw;
    imports.value = importsRaw;
  } catch (error) {
    console.error('Error loading products:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadProducts();
  document.addEventListener('click', closeBrandDropdown);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', closeBrandDropdown);
});

function openAddModal() {
  console.log("Mở cửa sổ thêm")
  isEditing.value = false;
  selectedTemplateIdx.value = '';
  errorMessage.value = '';
  form.value = { barcode: '', brand: '', name: '', category: '', published: '' };
  brandDropdownOpen.value = false;
  modalOpen.value = true;
  console.log(modalOpen.value)
}

function openEditModal(item) {
  isEditing.value = true;
  selectedTemplateIdx.value = '';
  errorMessage.value = '';
  const normalizedBrand = formatBrandValue(item[1] || '');
  form.value = {
    barcode: item[0] || '',
    brand: normalizedBrand,
    name: item[2] || '',
    category: item[3] || '',
    published: item[4] === '1' ? '1' : '',
  };
  brandDropdownOpen.value = false;
  editBarcodeRef.value = form.value.barcode;
  modalOpen.value = true;
}

function closeModal() {
  modalOpen.value = false;
  saving.value = false;
  selectedTemplateIdx.value = '';
  errorMessage.value = '';
  brandDropdownOpen.value = false;
}

watch(selectedTemplateIdx, (val) => {
  if (isEditing.value) return;
  if (val === '' || val === null || val === undefined) return;
  const idx = Number(val);
  if (!Number.isInteger(idx)) return;
  const row = products.value?.[idx];
  if (!row) return;
  form.value = {
    barcode: row[0] || '',
    brand: formatBrandValue(row[1]),
    name: row[2] || '',
    category: row[3] || '',
    published: String(row[4] || '').trim() === '1' ? '1' : '',
  };
});

function onBrandInput() {
  form.value.brand = formatBrandValue(form.value.brand);
}

function toggleBrandDropdown() {
  if (!brandOptions.value.length) return;
  brandDropdownOpen.value = !brandDropdownOpen.value;
}

function selectBrand(brand) {
  form.value.brand = formatBrandValue(brand);
  brandDropdownOpen.value = false;
}

function closeBrandDropdown() {
  brandDropdownOpen.value = false;
}

async function saveProduct() {
  try {
    saving.value = true;
    errorMessage.value = '';
    const barcode = (form.value.barcode || '').toString().trim();
    if (!barcode) {
      errorMessage.value = 'Vui lòng nhập barcode';
      saving.value = false;
      return;
    }
    if (!isEditing.value) {
      const isDuplicate = (products.value || []).some(
        (row) => String(row?.[0] || '').trim() === barcode,
      );
      if (isDuplicate) {
        errorMessage.value = 'Barcode đã tồn tại, vui lòng chỉnh sửa sản phẩm cũ hoặc nhập barcode khác.';
        saving.value = false;
        return;
      }
    }

    form.value.brand = formatBrandValue(form.value.brand);
    const payload = {
      barcode,
      'hãng': form.value.brand || '',
      'tên': form.value.name || '',
      'phân loại': form.value.category || '',
      'đã đăng': form.value.published === '1' ? '1' : '',
    };

    if (!isEditing.value) {
      await productsAPI.create(payload);
    } else {
      // cập nhật tất cả dòng products có cùng barcode
      const updates = [];
      for (let i = 0; i < products.value.length; i++) {
        const row = products.value[i];
        if (!row) continue;
        if (String(row[0] || '') === String(editBarcodeRef.value)) {
          updates.push({ row: i + 2, data: payload });
        }
      }
      if (updates.length) await productsAPI.updateRows(updates);

      // đồng bộ các lô nhập có cùng barcode
      const importUpdates = [];
      for (let i = 0; i < imports.value.length; i++) {
        const r = imports.value[i];
        if (!r) continue;
        if (String(r[1] || '') === String(editBarcodeRef.value)) {
          importUpdates.push({
            row: i + 2,
            data: {
              barcode: form.value.barcode,
              brand: form.value.brand || '',
              name: form.value.name || '',
              category: form.value.category || '',
            },
          });
        }
      }
      if (importUpdates.length) await importsAPI.updateRows(importUpdates);
    }

    await loadProducts();
    closeModal();
  } catch (e) {
    console.error('Save product failed:', e);
  } finally {
    saving.value = false;
  }
}

async function deleteByBarcode(barcode) {
  if (!barcode) return;
  if (!confirm('Xóa toàn bộ sản phẩm có barcode này?')) return;
  try {
    const rows = [];
    for (let i = 0; i < products.value.length; i++) {
      const row = products.value[i];
      if (row && String(row[0] || '') === String(barcode)) rows.push(i + 2);
    }
    if (rows.length) {
      await productsAPI.deleteRows(rows);
      await loadProducts();
    }
  } catch (e) {
    console.error('Delete product failed:', e);
  }
}
</script>

<style scoped>
.products-container {
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

.table-section {
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

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

/* Header actions */
.actions-right { display: flex; gap: 8px; }
.btn-primary { padding: 8px 12px; background: #86c06b; color: #fff; border: 1px solid #6db046; border-radius: 6px; font-size: 14px; cursor: pointer; transition: all 0.2s; }
.btn-primary:hover { background: #6db046; }
.btn-secondary { padding: 8px 12px; background: #f3f4f6; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; cursor: pointer; }
.btn-small { padding: 4px 8px; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; font-size: 13px; }
.btn-danger { background: #fee2e2; border-color: #fecaca; }
.actions-right { display: flex; gap: 8px; }
.btn-primary { padding: 8px 12px; background: #86c06b; color: #fff; border: 1px solid #6db046; border-radius: 6px; font-size: 13px; cursor: pointer; transition: all 0.2s; }
.btn-primary:hover { background: #6db046; }
.btn-secondary { padding: 8px 12px; background: #f3f4f6; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; cursor: pointer; }
.btn-small { padding: 4px 8px; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; font-size: 12px; }
.btn-danger { background: #fee2e2; border-color: #fecaca; }

.btn-refresh {
  padding: 8px 12px;
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

.products-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.products-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #eee;
}

.products-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.products-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
}
.products-table td.action-cell { white-space: nowrap; }

/* Unpublished rows highlighted red */
.products-table tbody tr.row-unpublished { background: #fef2f2; }
.products-table td.action-cell { white-space: nowrap; }

/* Unpublished rows highlighted red */
.products-table tbody tr.row-unpublished { background: #fef2f2; }

.barcode-cell {
  font-weight: 600;
  color: #2d5016;
  font-family: 'Courier New', monospace;
}


.qty-badge {
  display: inline-block;
  padding: 4px 8px;
  background: #dcfce7;
  color: #166534;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

/* Published badge */
.pub-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 13px;
  border: 1px solid transparent;
}
.pub-on {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}
.pub-off {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fecaca;
}

.btn-detail {
  padding: 6px 10px;
  background: #86c06b;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-detail:hover {
  background: #6db046;
}

.detail-row {
  background: #fafaf9;
}

.detail-content {
  padding: 16px 0;
}

.detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d5016;
  margin-bottom: 12px;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  background: white;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.detail-table thead {
  background: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
}

.detail-table th {
  padding: 8px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.detail-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #eee;
}

.detail-table tbody tr:last-child td {
  border-bottom: none;
}
/* modal thêm hoặc cập nhật */

/* Modal overlay and dialog (match ImportsManagement) */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
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
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
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

.modal-row-full {
  grid-template-columns: 1fr;
}

.modal-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.helper-text {
  font-size: 12px;
  color: #6b7280;
  margin: 4px 0 0;
}

.brand-stack {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.brand-input-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px;
  align-items: center;
}

.btn-brand-dropdown {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f3f4f6;
  cursor: pointer;
  min-width: 44px;
}

.btn-brand-dropdown:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.brand-dropdown {
  margin: 0;
  padding: 4px 0;
  list-style: none;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
  z-index: 20;
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
}

.brand-dropdown li {
  padding: 8px 12px;
  cursor: pointer;
}

.brand-dropdown li:hover {
  background: #f3f4f6;
}

.alert {
  margin-bottom: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.error-alert {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Inputs inside modal (match ImportsManagement) */
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

@media (max-width: 640px) {
  .products-container {
    padding: 12px;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .products-table {
    font-size: 12px;
  }

  .products-table th,
  .products-table td {
    padding: 8px 6px;
  }

  .detail-table {
    font-size: 11px;
  }

  .detail-table th,
  .detail-table td {
    padding: 6px 4px;
  }
}
</style>
