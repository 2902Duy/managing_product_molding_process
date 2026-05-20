import { inventoryApi } from './inventoryApi';
import { lotsApi } from './lotsApi';
import { ordersApi } from './ordersApi';

const defaultOrders = [
  {
    id: 'DH-2026-01', name: 'Đơn hàng Nội thất Vinpearl', products: [
      {
        id: 'SP-001', name: 'Bàn ăn Sồi', quantity: 10, items: [
          { id: 'PT-01', name: 'Phôi chân bàn', length: 750, width: 80, thickness: 80, base_quantity: 4 },
          { id: 'PT-02', name: 'Phôi mặt bàn', length: 1800, width: 200, thickness: 25, base_quantity: 1 },
        ]
      },
      {
        id: 'SP-002', name: 'Ghế ăn Sồi', quantity: 40, items: [
          { id: 'PT-03', name: 'Phôi chân ghế trước', length: 450, width: 50, thickness: 50, base_quantity: 2 },
          { id: 'PT-04', name: 'Phôi chân ghế sau', length: 850, width: 50, thickness: 50, base_quantity: 2 },
          { id: 'PT-05', name: 'Phôi mặt ghế', length: 450, width: 400, thickness: 20, base_quantity: 1 },
        ]
      }
    ]
  },
  {
    id: 'DH-2026-02', name: 'Dự án Tủ áo Gõ đỏ', products: [
      {
        id: 'SP-003', name: 'Tủ quần áo 3 buồng', quantity: 5, items: [
          { id: 'PT-06', name: 'Phôi cánh tủ', length: 2000, width: 500, thickness: 20, base_quantity: 3 },
          { id: 'PT-07', name: 'Phôi hông tủ', length: 2000, width: 600, thickness: 18, base_quantity: 2 },
          { id: 'PT-08', name: 'Phôi đợt kệ', length: 800, width: 580, thickness: 18, base_quantity: 6 },
        ]
      }
    ]
  },
  {
    id: 'DH-2026-03', name: 'Lô xuất khẩu gỗ khối', products: [
      {
        id: 'SP-004', name: 'Phôi tổng hợp Dẻ gai', quantity: 1, items: [
          { id: 'PT-09', name: 'Phôi quy cách A', length: 670, width: 910, thickness: 22, base_quantity: 22 },
          { id: 'PT-10', name: 'Phôi quy cách B', length: 500, width: 400, thickness: 22, base_quantity: 104 },
        ]
      }
    ]
  }
];

export const db = {
  // ── Orders (API with fallback to default data) ──
  getOrders: async () => {
    try {
      const orders = await ordersApi.getOrders();
      if (orders && orders.length > 0) return orders;
    } catch (e) {
      console.warn('API unavailable, using default orders:', e.message);
    }
    return defaultOrders;
  },

  // ── Inventory (API calls) ──
  getInventory: async (type, status) => {
    try {
      return await inventoryApi.getInventory(type, status);
    } catch (e) {
      console.warn('API unavailable for inventory:', e.message);
      return [];
    }
  },

  getAvailableInventory: async (type) => {
    try {
      return await inventoryApi.getAvailableInventory(type);
    } catch (e) {
      console.warn('API unavailable for available inventory:', e.message);
      return [];
    }
  },

  addInventory: async (items) => {
    try {
      const results = [];
      for (const item of items) {
        const created = await inventoryApi.createInventoryItem({
          ...item,
          id: item.id || undefined,
        });
        results.push(created);
      }
      return results;
    } catch (e) {
      console.warn('API unavailable for addInventory:', e.message);
      return [];
    }
  },

  removeInventory: async (ids) => {
    try {
      await inventoryApi.deleteInventoryItems(ids);
    } catch (e) {
      console.warn('API unavailable for removeInventory:', e.message);
    }
  },

  // ── Lots (API calls) ──
  getLots: async (slipType, status) => {
    try {
      return await lotsApi.getLots(slipType, status);
    } catch (e) {
      console.warn('API unavailable for lots:', e.message);
      return [];
    }
  },

  getLot: async (id) => {
    try {
      return await lotsApi.getLot(id);
    } catch (e) {
      console.warn('API unavailable for getLot:', e.message);
      return null;
    }
  },

  saveLot: async (lot) => {
    try {
      if (lot.id) {
        const existing = await lotsApi.getLot(lot.id).catch(() => null);
        if (existing) {
          return await lotsApi.updateLot(lot.id, {
            name: lot.name,
            status: lot.status,
            description: lot.description,
            data: {
              targetProducts: lot.targetProducts,
              inputs: lot.inputs,
              outputs: lot.outputs,
            },
          });
        }
      }
      const created = await lotsApi.createLot({
        id: lot.id || undefined,
        name: lot.name,
        status: lot.status,
        description: lot.description,
        created_date: lot.date || new Date().toISOString().split('T')[0],
        data: {
          targetProducts: lot.targetProducts,
          inputs: lot.inputs,
          outputs: lot.outputs,
        },
      });
      return created;
    } catch (e) {
      console.warn('API unavailable for saveLot:', e.message);
      return null;
    }
  },

  deleteLot: async (id) => {
    try {
      await lotsApi.deleteLot(id);
    } catch (e) {
      console.warn('API unavailable for deleteLot:', e.message);
    }
  },

  // Helper for development: Reset all local storage data
  resetAllData: () => {
    localStorage.removeItem('wp_orders');
    localStorage.removeItem('wp_orders_v2');
    localStorage.removeItem('wp_inventory_v3');
    localStorage.removeItem('wp_lots_v3');
    localStorage.removeItem('wp_production_lots_v3');
    console.log("Đã xóa dữ liệu cũ. Reload lại trang để nhận dữ liệu mới từ API.");
    window.location.reload();
  }
};

// Expose to window for easy debugging
if (typeof window !== 'undefined') {
  window.resetDb = db.resetAllData;
}
