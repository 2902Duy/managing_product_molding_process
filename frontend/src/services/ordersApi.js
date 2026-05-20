import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const api = axios.create({ baseURL: `${API_BASE}/api/v1/orders` });

export const ordersApi = {
  getOrders: async () => {
    const { data } = await api.get('');
    return data;
  },

  getOrder: async (id) => {
    const { data } = await api.get(`/${id}`);
    return data;
  },

  createOrder: async (order) => {
    const { data } = await api.post('', order);
    return data;
  },

  searchOrders: async (query) => {
    const { data } = await api.get('/search', { params: { q: query } });
    return data;
  },
};

export default ordersApi;
