import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const api = axios.create({ baseURL: `${API_BASE}/api/v1/inventory` });

export const inventoryApi = {
  getInventory: async (type, status) => {
    const params = {};
    if (type) params.type = type;
    if (status) params.status = status;
    const { data } = await api.get('', { params });
    return data;
  },

  getAvailableInventory: async (type) => {
    const params = { status: 'AVAILABLE' };
    if (type) params.type = type;
    const { data } = await api.get('', { params });
    return data;
  },

  getInventoryItem: async (id) => {
    const { data } = await api.get(`/${id}`);
    return data;
  },

  createInventoryItem: async (item) => {
    const { data } = await api.post('', item);
    return data;
  },

  updateInventoryItem: async (id, updates) => {
    const { data } = await api.put(`/${id}`, updates);
    return data;
  },

  deleteInventoryItem: async (id) => {
    const { data } = await api.delete(`/${id}`);
    return data;
  },

  deleteInventoryItems: async (ids) => {
    const promises = ids.map(id => api.delete(`/${id}`));
    await Promise.all(promises);
  },

  searchInventory: async (query) => {
    const { data } = await api.get('/search', { params: { q: query } });
    return data;
  },

  getStats: async () => {
    const { data } = await api.get('/stats');
    return data;
  },

  updateStatus: async (id, status) => {
    const { data } = await api.patch(`/${id}/status`, null, { params: { status } });
    return data;
  },

  updateQuantity: async (id, quantity) => {
    const { data } = await api.patch(`/${id}/quantity`, null, { params: { quantity } });
    return data;
  },

  bulkUpdateStatus: async (ids, status) => {
    const { data } = await api.post('/bulk-update-status', null, {
      params: { ids, status }
    });
    return data;
  },
};

export default inventoryApi;
