<template>
  <div class="expenses-container">
    <h1 class="page-title">💰 Chi Tiêu</h1>

    <!-- Form Chi Tiêu -->
    <div class="form-section">
      <h2 class="section-title">Thêm Chi Tiêu Mới</h2>
      <form @submit.prevent="submitForm" class="expense-form">
        <div class="form-row">
          <div class="form-group">
            <label for="date">Ngày</label>
            <input
              v-model="form.date"
              type="date"
              id="date"
              required
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label for="description">Nội Dung Chi Tiêu</label>
            <input
              v-model="form.description"
              type="text"
              id="description"
              placeholder="Mô tả chi tiêu..."
              required
              class="input-field"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="amount">Số Tiền (₫)</label>
            <input
              v-model.number="form.amount"
              type="number"
              id="amount"
              placeholder="0"
              required
              min="0"
              step="0.01"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label for="payer">Người Trả</label>
            <input
              v-model="form.payer"
              type="text"
              id="payer"
              placeholder="Tên người trả..."
              required
              class="input-field"
              list="payerOptions"
            />
            <datalist id="payerOptions">
              <option v-for="p in uniquePayers" :key="p" :value="p" />
            </datalist>
          </div>
        </div>

        <div class="form-group">
          <label for="note">Ghi Chú</label>
          <input
            v-model="form.note"
            type="text"
            id="note"
            placeholder="Ghi chú thêm..."
            class="input-field"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-submit" :disabled="loading">
            {{ loading ? 'Đang lưu...' : '✓ Thêm Chi Tiêu' }}
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

    <!-- Danh Sách Chi Tiêu -->
    <div class="table-section">
      <div class="table-header">
        <h2 class="section-title">Danh Sách Chi Tiêu</h2>
        <button @click="loadExpenses" class="btn-refresh">🔄 Làm Mới</button>
      </div>

      <div class="filter-bar">
        <div class="filter-group">
          <label for="monthFilter">Lọc theo tháng:</label>
          <input
            v-model="selectedMonth"
            type="month"
            id="monthFilter"
            class="filter-input"
          />
          <button v-if="selectedMonth" @click="resetMonthFilter" class="btn-clear">Xóa lọc</button>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm theo nội dung, người trả..."
          class="search-input"
        />
      </div>

      <div v-if="loading" class="loading">Đang tải dữ liệu...</div>

      <div v-else-if="filteredExpenses.length === 0" class="empty-state">
        Không có dữ liệu
      </div>

      <div v-else class="table-wrapper">
        <table class="expenses-table">
          <thead>
            <tr>
              <th>Ngày</th>
              <th>Nội Dung Chi Tiêu</th>
              <th>Số Tiền</th>
              <th>Ghi Chú</th>
              <th>Người Trả</th>
              <th>Hành Động</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in filteredExpenses" :key="`${item[0]}-${idx}`">
              <td>{{ item[0] }}</td>
              <td>{{ item[1] }}</td>
              <td class="amount-cell">{{ formatNumber(item[2]) }}</td>
              <td>{{ item[3] }}</td>
              <td>{{ item[4] }}</td>
              <td>
                <button @click="openEditModal(item, idx)" class="btn-refresh">✏️</button>
                <button @click="deleteExpense(item, idx)" class="btn-delete">X</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredExpenses.length > 0" class="summary">
        <span class="summary-text">Tổng cộng: <strong>{{ formatNumber(totalAmount) }}₫</strong></span>
      </div>
    </div>

    <!-- Modal chỉnh sửa -->
    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Chỉnh Sửa Chi Tiêu</h3>
          <button class="modal-close" @click="closeEditModal">✖</button>
        </div>
        <div class="modal-body">
          <div class="modal-row">
            <div class="modal-group">
              <label>Ngày</label>
              <input v-model="editForm.date" type="date" class="input-field" />
            </div>
            <div class="modal-group">
              <label>Nội Dung Chi Tiêu</label>
              <input v-model="editForm.description" class="input-field" />
            </div>
          </div>
          <div class="modal-row">
            <div class="modal-group">
              <label>Số Tiền (₫)</label>
              <input v-model.number="editForm.amount" type="number" step="0.01" min="0" class="input-field" />
            </div>
            <div class="modal-group">
              <label>Người Trả</label>
              <input v-model="editForm.payer" class="input-field" />
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
          <button class="btn-reset" @click="closeEditModal" :disabled="loading">Hủy</button>
          <button class="btn-submit" @click="saveEdit" :disabled="loading">Lưu</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { expensesAPI } from '@/services/api';

const form = ref({
  date: new Date().toISOString().split('T')[0],
  description: '',
  amount: 0,
  note: '',
  payer: '',
});

const expenses = ref([]);
const loading = ref(false);
const message = ref(null);
const searchQuery = ref('');
const selectedMonth = ref('');

const editingIdx = ref(null);
const editForm = ref({
  date: '',
  description: '',
  amount: 0,
  note: '',
  payer: '',
});
const isEditModalOpen = ref(false);

function getMonthFromVNDate(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('/');
  if (parts.length === 3) {
    const [dd, mm, yyyy] = parts;
    return `${yyyy}-${mm.padStart(2, '0')}`;
  }
  return '';
}

const filteredExpenses = computed(() => {
  return expenses.value.filter((item) => {
    const query = searchQuery.value.toLowerCase();
    const matchesSearch =
      item[1].toLowerCase().includes(query) ||
      item[4].toLowerCase().includes(query);

    if (!selectedMonth.value) return matchesSearch;

    const itemMonth = getMonthFromVNDate(item[0]);
    const matchesMonth = itemMonth === selectedMonth.value;

    return matchesSearch && matchesMonth;
  });
});

const totalAmount = computed(() => {
  return filteredExpenses.value.reduce((sum, item) => {
    const amount = parseFloat(item[2]) || 0;
    return sum + amount;
  }, 0);
});

const uniquePayers = computed(() => {
  const set = new Set(
    expenses.value
      .map((r) => (r && typeof r[4] === 'string' ? r[4].trim() : ''))
      .filter((p) => p)
  );
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'vi', { sensitivity: 'base' }));
});

function resetMonthFilter() {
  selectedMonth.value = '';
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

async function loadExpenses() {
  loading.value = true;
  try {
    const result = await expensesAPI.getAll();
    expenses.value = result.data || [];
  } catch (error) {
    showMessage('Lỗi tải dữ liệu', 'error');
  } finally {
    loading.value = false;
  }
}

async function submitForm() {
  loading.value = true;
  try {
    await expensesAPI.create({
      date: form.value.date,
      description: form.value.description,
      amount: form.value.amount,
      note: form.value.note,
      payer: form.value.payer,
    });

    showMessage('Thêm chi tiêu thành công!', 'success');
    form.value = {
      date: new Date().toISOString().split('T')[0],
      description: '',
      amount: 0,
      note: '',
      payer: '',
    };
    await loadExpenses();
  } catch (error) {
    showMessage('Lỗi: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  form.value = {
    date: new Date().toISOString().split('T')[0],
    description: '',
    amount: 0,
    note: '',
    payer: '',
  };
}

function openEditModal(item, idx) {
  editingIdx.value = idx;
  editForm.value = {
    date: toISODateFromVN(item[0] || ''),
    description: item[1] || '',
    amount: parseFloat(item[2]) || 0,
    note: item[3] || '',
    payer: item[4] || '',
  };
  isEditModalOpen.value = true;
}

function closeEditModal() {
  isEditModalOpen.value = false;
  editingIdx.value = null;
}

async function saveEdit() {
  if (editingIdx.value === null) return;
  loading.value = true;
  try {
    const actualRow = editingIdx.value + 2;
    const payload = {
      date: editForm.value.date,
      description: editForm.value.description,
      amount: editForm.value.amount,
      note: editForm.value.note,
      payer: editForm.value.payer,
    };
    await expensesAPI.updateRows([{ row: actualRow, data: payload }]);
    showMessage('Đ�� cập nhật chi tiêu', 'success');
    closeEditModal();
    await loadExpenses();
  } catch (error) {
    showMessage('Lỗi cập nhật: ' + error.message, 'error');
  } finally {
    loading.value = false;
  }
}

async function deleteExpense(item, idx) {
  if (!confirm('Bạn chắc chắn muốn xóa?')) return;
  loading.value = true;
  try {
    const actualRow = idx + 2;
    await expensesAPI.deleteRows([actualRow]);
    showMessage('Xóa thành công!', 'success');
    await loadExpenses();
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
  loadExpenses();
});
</script>

<style scoped>
.expenses-container {
  width: 100%;
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

.expense-form {
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
}

.btn-reset:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-reset:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.filter-bar {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
  white-space: nowrap;
  margin: 0;
}

.filter-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.filter-input:focus {
  outline: none;
  border-color: #86c06b;
  box-shadow: 0 0 0 3px rgba(134, 192, 107, 0.1);
}

.btn-clear {
  padding: 6px 12px;
  background: #f3f4f6;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: #e5e7eb;
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

.expenses-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.expenses-table thead {
  background: #f9fafb;
  border-bottom: 2px solid #eee;
}

.expenses-table th {
  padding: 12px 10px;
  text-align: left;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.expenses-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eee;
  word-break: break-word;
}

.amount-cell {
  font-weight: 600;
  color: #d97706;
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

.summary {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #eee;
  text-align: right;
}

.summary-text {
  font-size: 15px;
  color: #555;
}

/* Modal */
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

.modal-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

@media (max-width: 640px) {
  .expenses-container {
    padding: 12px;
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-group {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

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

  .expenses-table {
    font-size: 13px;
  }

  .expenses-table th,
  .expenses-table td {
    padding: 8px 6px;
  }
}

@media (min-width: 1440px) {
  .expenses-container {
    max-width: 96vw;
  }
}
</style>
