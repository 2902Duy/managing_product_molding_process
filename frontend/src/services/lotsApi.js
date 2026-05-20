import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const api = axios.create({ baseURL: `${API_BASE}/api/v1/lots` });

export const lotsApi = {
  getLots: async (slipType, status) => {
    const params = {};
    if (slipType) params.slip_type = slipType;
    if (status) params.status = status;
    const { data } = await api.get('', { params });
    return data;
  },

  getLot: async (id) => {
    const { data } = await api.get(`/${id}`);
    return data;
  },

  createLot: async (lot) => {
    const { data } = await api.post('', lot);
    return data;
  },

  updateLot: async (id, updates) => {
    const { data } = await api.put(`/${id}`, updates);
    return data;
  },

  deleteLot: async (id) => {
    const { data } = await api.delete(`/${id}`);
    return data;
  },

  getLotInputs: async (lotId) => {
    const { data } = await api.get(`/${lotId}/inputs`);
    return data;
  },

  getLotOutputs: async (lotId) => {
    const { data } = await api.get(`/${lotId}/outputs`);
    return data;
  },

  saveLotOutputs: async (lotId, outputs) => {
    const { data } = await api.post(`/${lotId}/outputs`, outputs);
    return data;
  },

  consumeMaterialsForLot: async (lotId, materials) => {
    const { data } = await api.post(`/${lotId}/consume-materials`, materials);
    return data;
  },

  releaseMaterialsFromLot: async (lotId, materials) => {
    const { data } = await api.post(`/${lotId}/release-materials`, materials);
    return data;
  },

  getLotMaterialUsage: async (lotId) => {
    const { data } = await api.get(`/${lotId}/material-usage`);
    return data;
  },

  getLotTarget: async (lotId) => {
    const { data } = await api.get(`/${lotId}/target`);
    return data;
  },

  setLotTarget: async (lotId, target) => {
    const { data } = await api.post(`/${lotId}/target`, target);
    return data;
  },
};

export default lotsApi;
