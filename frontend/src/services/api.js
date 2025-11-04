const API_BASE_URL = 'http://localhost:8001';

// ============= IMPORTS API =============
export const importsAPI = {
  async getAll() {
    const response = await fetch(`${API_BASE_URL}/imports/`);
    if (!response.ok) throw new Error('Failed to fetch imports');
    return response.json();
  },

  async create(data) {
    const response = await fetch(`${API_BASE_URL}/imports/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create import');
    return response.json();
  },

  async updateRows(updates) {
    const response = await fetch(`${API_BASE_URL}/imports/rows/update`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates }),
    });
    if (!response.ok) throw new Error('Failed to update imports');
    return response.json();
  },

  async deleteRows(rows) {
    const response = await fetch(`${API_BASE_URL}/imports/rows/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rows }),
    });
    if (!response.ok) throw new Error('Failed to delete imports');
    return response.json();
  },
};

// ============= PRODUCTS API =============
export const productsAPI = {
  async getAll() {
    const response = await fetch(`${API_BASE_URL}/products/get`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch products');
    return response.json();
  },
};

// ============= ORDERS API =============
export const ordersAPI = {
  async getAll() {
    const response = await fetch(`${API_BASE_URL}/orders/get`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch orders');
    return response.json();
  },

  async create(data) {
    const response = await fetch(`${API_BASE_URL}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create order');
    return response.json();
  },
};

// ============= SOLD API =============
export const soldAPI = {
  async getAll() {
    const response = await fetch(`${API_BASE_URL}/sold/get`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch sold items');
    return response.json();
  },

  async create(data) {
    const response = await fetch(`${API_BASE_URL}/sold/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create sold item');
    return response.json();
  },
};

// ============= UTILITY FUNCTIONS =============
export function generateUniqueId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export function formatDate(dateString) {
  if (!dateString) return new Date().toISOString().split('T')[0];
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
}

export function getCurrentDateVN() {
  const now = new Date();
  now.setHours(now.getHours() + 7);
  return now.toISOString().split('T')[0];
}
