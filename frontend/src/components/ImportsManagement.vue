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
          />
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
            />
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

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Đang lưu...' : '✓ Thêm Lô Hàng' }}
        </button>
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
            <tr v-for="(item, idx) in filteredImports" :key="idx">
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
                <button @click="openEditModal(idx)" class="btn-edit">✏️</button>
                <button @click="deleteImport(idx)" class="btn-delete">🗑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Chỉnh Sửa Lô Hàng</h2>
          <button @click="closeEditModal" class="btn-close">✕</button>
        </div>

        <form @submit.prevent="submitEdit" class="edit-form">
          <div class="form-group">
            <label for="edit-barcode">Mã Barcode</label>
            <input
              v-model="editForm.barcode"
              type="text"
              id="edit-barcode"
              placeholder="Nhập hoặc quét barcode"
              class="input-field"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="edit-brand">Thương Hiệu</label>
              <input
                v-model="editForm.brand"
                type="text"
                id="edit-brand"
                placeholder="Brand"
                class="input-field"
              />
            </div>
            <div class="form-group">
              <label for="edit-name">Tên Sản Phẩm</label>
              <input
                v-model="editForm.name"
                type="text"
                id="edit-name"
                placeholder="Tên sản phẩm"
                class="input-field"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="edit-category">Danh Mục</label>
              <input
                v-model="editForm.category"
                type="text"
                id="edit-category"
                placeholder="Danh mục"
                class="input-field"
              />
            </div>
            <div class="form-group">
              <label for="edit-qty">Số Lượng Nhập</label>
              <input
                v-model.number="editForm.qty_in"
                type="number"
                id="edit-qty"
                placeholder="0"
                min="1"
                class="input-field"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="edit-unitCost">Giá Vốn (₫)</label>
              <input
                v-model.number="editForm.unit_cost"
                type="number"
                id="edit-unitCost"
                placeholder="0"
                min="0"
                step="0.01"
                class="input-field"
              />
            </div>
            <div class="form-group">
              <label for="edit-breakEven">Giá Hòa Vốn (₫)</label>
              <input
                v-model.number="editForm.break_even_price"
                type="number"
                id="edit-breakEven"
                placeholder="0"
                min="0"
                step="0.01"
                class="input-field"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="edit-importDate">Ngày Nhập</label>
              <input
                v-model="editForm.import_date"
                type="date"
                id="edit-importDate"
                class="input-field"
              />
            </div>
            <div class="form-group">
              <label for="edit-note">Ghi Chú</label>
              <input
                v-model="editForm.note"
                type="text"
                id="edit-note"
                placeholder="Ghi chú..."
                class="input-field"
              />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeEditModal" class="btn-cancel">Hủy</button>
            <button type="submit" class="btn-submit" :disabled="loading">
              {{ loading ? 'Đang lưu...' : '✓ Cập Nhật' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { importsAPI } from '../services/api';

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
const showEditModal = ref(false);
const editingRowIndex = ref(null);
const editForm = ref({
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

const filteredImports = computed(() => {
  return imports.value.filter((item) => {
    const query = searchQuery.value.toLowerCase();
    return (
      item[1].toLowerCase().includes(query) ||
      item[3].toLowerCase().includes(query)
    );
  });
});

function generateSampleData() {
  const sampleProducts = [
    {
      productID: 'PROD001',
      barcode: '8936026800001',
      brand: 'SK-II',
      name: 'Facial Treatment Essence',
      category: 'Essence',
      qty_in: 20,
      unit_cost: 450000,
      break_even_price: 520000,
      import_date: '15/01/2025',
      note: 'Hàng mẫu - dùng để test',
      qty_sold: 5,
      available_qty: 15,
      created_at: '2025-01-15 10:00:00',
    },
    {
      productID: 'PROD002',
      barcode: '8936026800002',
      brand: 'Laneige',
      name: 'Water Sleeping Mask',
      category: 'Mặt Nạ',
      qty_in: 15,
      unit_cost: 320000,
      break_even_price: 380000,
      import_date: '14/01/2025',
      note: 'Hàng mẫu - dùng để test',
      qty_sold: 3,
      available_qty: 12,
      created_at: '2025-01-14 14:30:00',
    },
    {
      productID: 'PROD003',
      barcode: '8936026800003',
      brand: 'Etude House',
      name: 'Soon Jung Toner',
      category: 'Nước Hoa Hồng',
      qty_in: 30,
      unit_cost: 180000,
      break_even_price: 220000,
      import_date: '13/01/2025',
      note: 'Hàng mẫu - dùng để test',
      qty_sold: 8,
      available_qty: 22,
      created_at: '2025-01-13 09:15:00',
    },
    {
      productID: 'PROD004',
      barcode: '8936026800004',
      brand: 'Innisfree',
      name: 'Green Tea Seed Serum',
      category: 'Serum',
      qty_in: 25,
      unit_cost: 220000,
      break_even_price: 280000,
      import_date: '12/01/2025',
      note: 'Hàng mẫu - dùng để test',
      qty_sold: 0,
      available_qty: 25,
      created_at: '2025-01-12 11:45:00',
    },
    {
      productID: 'PROD005',
      barcode: '8936026800005',
      brand: 'The Ordinary',
      name: 'Hyaluronic Acid 2%',
      category: 'Serum',
      qty_in: 40,
      unit_cost: 120000,
      break_even_price: 150000,
      import_date: '11/01/2025',
      note: 'Hàng mẫu - dùng để test',
      qty_sold: 12,
      available_qty: 28,
      created_at: '2025-01-11 16:20:00',
    },
  ];

  return sampleProducts.map((p) => [
    p.productID,
    p.barcode,
    p.brand,
    p.name,
    p.category,
    String(p.qty_in),
    String(p.unit_cost),
    String(p.break_even_price),
    p.import_date,
    p.note,
    String(p.qty_sold),
    String(p.available_qty),
    p.created_at,
  ]);
}

async function loadImports() {
  loading.value = true;
  try {
    const result = await importsAPI.getAll();
    imports.value = result.data || [];
    if (imports.value.length === 0) {
      showMessage('Không có dữ liệu từ server, đang hiển thị dữ liệu mẫu', 'info');
      imports.value = generateSampleData();
    }
  } catch (error) {
    showMessage('Không thể kết nối API, đang hiển thị dữ liệu mẫu', 'info');
    imports.value = generateSampleData();
  } finally {
    loading.value = false;
  }
}

async function submitForm() {
  loading.value = true;
  try {
    const now = new Date();
    const createdAt = now.toLocaleString('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh' });

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
    await loadImports();
  } catch (error) {
    showMessage('Lỗi: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

function openEditModal(idx) {
  editingRowIndex.value = idx;
  const item = filteredImports.value[idx];
  editForm.value = {
    barcode: item[1],
    brand: item[2],
    name: item[3],
    category: item[4],
    qty_in: parseInt(item[5]) || 1,
    unit_cost: parseFloat(item[6]) || 0,
    break_even_price: parseFloat(item[7]) || 0,
    import_date: item[8] || new Date().toISOString().split('T')[0],
    note: item[9] || '',
  };
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
  editingRowIndex.value = null;
  editForm.value = {
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
}

async function submitEdit() {
  if (!editForm.value.barcode.trim()) {
    showMessage('Vui lòng nhập barcode', 'error');
    return;
  }
  if (!editForm.value.brand.trim()) {
    showMessage('Vui lòng nhập brand', 'error');
    return;
  }
  if (!editForm.value.name.trim()) {
    showMessage('Vui lòng nhập tên sản phẩm', 'error');
    return;
  }
  if (!editForm.value.category.trim()) {
    showMessage('Vui lòng nhập danh mục', 'error');
    return;
  }

  loading.value = true;
  try {
    const idx = editingRowIndex.value;
    const actualRow = idx + 2;

    const updates = [
      {
        row: actualRow,
        data: {
          barcode: editForm.value.barcode,
          brand: editForm.value.brand,
          name: editForm.value.name,
          category: editForm.value.category,
          qty_in: editForm.value.qty_in,
          unit_cost: editForm.value.unit_cost,
          break_even_price: editForm.value.break_even_price,
          import_date: editForm.value.import_date,
          note: editForm.value.note,
        },
      },
    ];

    await importsAPI.updateRows(updates);
    showMessage('Cập nhật thành công!', 'success');
    closeEditModal();
    await loadImports();
  } catch (error) {
    showMessage('Lỗi cập nhật: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

async function deleteImport(idx) {
  if (!confirm('Bạn chắc chắn muốn xóa?')) return;
  loading.value = true;
  try {
    const actualRow = idx + 2;
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
});
</script>

<style scoped>
.imports-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
  background: #fafaf9;
  min-height: 100vh;
}

.page-title {
  font-size: 28px;
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
  font-size: 16px;
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
  font-size: 13px;
  font-weight: 500;
  color: #555;
}

.input-field {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
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
  font-size: 14px;
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

.message {
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 12px;
  font-size: 13px;
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

.message.info {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #bfdbfe;
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
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
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
  font-size: 14px;
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
  font-size: 14px;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #eee;
}

.imports-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
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

.btn-edit {
  padding: 4px 8px;
  background: #dbeafe;
  border: 1px solid #bfdbfe;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  margin-right: 4px;
}

.btn-edit:hover {
  background: #bfdbfe;
}

.btn-delete {
  padding: 4px 8px;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: #fecaca;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #2d5016;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
  padding: 0;
}

.btn-close:hover {
  color: #2d5016;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn-cancel {
  flex: 1;
  padding: 12px 16px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

@media (max-width: 640px) {
  .imports-container {
    padding: 12px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .imports-table {
    font-size: 12px;
  }

  .imports-table th,
  .imports-table td {
    padding: 8px 6px;
  }
}
</style>
