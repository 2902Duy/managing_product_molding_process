import React, { useState, useEffect } from 'react';
import { ArrowLeft, Save, Check, CheckCircle, X, ClipboardList } from 'lucide-react';
import { db } from '../services/db';
import { removeVietnameseTones } from '../utils/stringUtils';

import InputTable from '../components/ProductionLot/InputTable';
import TargetProductTable from '../components/ProductionLot/TargetProductTable';
import OrderSelectionModal from '../components/ProductionLot/OrderSelectionModal';
import OutputTable from '../components/ProductionLot/OutputTable';
import InventoryModal from '../components/ProductionLot/InventoryModal';

export default function ProductionLotDetail({ onNavigate, lotId }) {
  const [lotName, setLotName] = useState(lotId ? `Lệnh SX ${lotId}` : '');
  const [status, setStatus] = useState('Đang sản xuất');
  const [description, setDescription] = useState('');
  
  // Target Products (Order -> Product -> Parts)
  const [selectedTargetProducts, setSelectedTargetProducts] = useState([]);
  const [orderModalOpen, setOrderModalOpen] = useState(false);

  // ─── Data from mock DB ────────────────────────────
  const [availableInventory, setAvailableInventory] = useState([]);
  const [orders, setOrders] = useState([]);

  // ─── State ────────────────────────────────────────
  // 1. Nguyên liệu đầu vào
  const [selectedInputs, setSelectedInputs] = useState([]);
  const [inventoryModalOpen, setInventoryModalOpen] = useState(false);
  const [invSearch, setInvSearch] = useState('');
  const [invTab, setInvTab] = useState('ALL');

  // Modal
  const [modal, setModal] = useState({ isOpen: false, type: '', title: '', message: '', onConfirm: null });
  const closeModal = () => setModal(prev => ({ ...prev, isOpen: false }));

  // 2. Kêt quả đầu ra
  const [outputs, setOutputs] = useState([
    { id: Date.now(), name: '', thickness: '', width: '', length: '', quantity: '', volume: '', status: 'Thành phẩm' }
  ]);

  useEffect(() => {
    setAvailableInventory(db.getInventory());
    setOrders(db.getOrders() || []);

    if (lotId) {
      const lot = db.getLot(lotId);
      if (lot) {
        setLotName(lot.name || '');
        setStatus(lot.status || 'Đang sản xuất');
        setDescription(lot.description || '');
        setSelectedTargetProducts(lot.targetProducts || []);
        setSelectedInputs((lot.inputs || []).map(i => ({
          ...i,
          quantity_used: i.quantity_used || i.quantity,
          volume_used: i.volume_used || i.volume
        })));

        if (lot.outputs && lot.outputs.length > 0) {
          setOutputs(lot.outputs);
        }
      }
    } else {
      setLotName(`Lệnh SX Mới`);
    }
  }, [lotId]);

  // ─── Handlers cho Order / Target Products ──────────
  const handleOpenOrderModal = () => setOrderModalOpen(true);
  
  const handleToggleProductSelection = (product, order) => {
    const exists = selectedTargetProducts.find(p => p.id === product.id);
    if (exists) {
      setSelectedTargetProducts(selectedTargetProducts.filter(p => p.id !== product.id));
    } else {
      setSelectedTargetProducts([...selectedTargetProducts, { ...product, orderId: order.id, orderName: order.name, quantity_produce: product.quantity }]);
    }
  };

  const handleToggleOrderSelection = (order) => {
    const allSelected = order.products.every(p => selectedTargetProducts.find(sp => sp.id === p.id));
    if (allSelected) {
      const pIds = order.products.map(p => p.id);
      setSelectedTargetProducts(selectedTargetProducts.filter(p => !pIds.includes(p.id)));
    } else {
      const newProducts = order.products
        .filter(p => !selectedTargetProducts.find(sp => sp.id === p.id))
        .map(p => ({ ...p, orderId: order.id, orderName: order.name, quantity_produce: p.quantity }));
      setSelectedTargetProducts([...selectedTargetProducts, ...newProducts]);
    }
  };

  const handleChangeProductQuantity = (id, qty) => {
    setSelectedTargetProducts(selectedTargetProducts.map(p => {
      if (p.id === id) return { ...p, quantity_produce: qty };
      return p;
    }));
  };

  const handleRemoveProduct = (id) => setSelectedTargetProducts(selectedTargetProducts.filter(p => p.id !== id));

  // ─── Handlers cho Modal và Input Table ─────────────
  const handleOpenInventoryModal = () => {
    setInvSearch('');
    setInvTab('ALL');
    setInventoryModalOpen(true);
  };

  const handleToggleInputSelection = (item) => {
    const exists = selectedInputs.find(i => i.id === item.id);
    if (exists) {
      setSelectedInputs(selectedInputs.filter(i => i.id !== item.id));
    } else {
      setSelectedInputs([...selectedInputs, { ...item, quantity_used: item.quantity, volume_used: item.volume }]);
    }
  };

  const handleToggleModalBatchSelection = (batchItems) => {
    const allSelected = batchItems.every(item => selectedInputs.find(i => i.id === item.id));
    if (allSelected) {
      const batchIds = batchItems.map(i => i.id);
      setSelectedInputs(selectedInputs.filter(i => !batchIds.includes(i.id)));
    } else {
      const newItems = batchItems
        .filter(item => !selectedInputs.find(i => i.id === item.id))
        .map(item => ({ ...item, quantity_used: item.quantity, volume_used: item.volume }));
      setSelectedInputs([...selectedInputs, ...newItems]);
    }
  };

  const handleRemoveInputItem = (id) => setSelectedInputs(selectedInputs.filter(i => i.id !== id));

  const handleRemoveInputBatch = (batchId) => {
    setSelectedInputs(selectedInputs.filter(i => (i.batchId || i.id) !== batchId));
  };

  const handleChangeInputQuantity = (id, newQty) => {
    setSelectedInputs(selectedInputs.map(item => {
      if (item.id === id) {
        const qty = newQty === '' ? '' : Number(newQty);
        let vol = item.volume_used;
        if (qty !== '' && item.thickness && item.width && item.length && item.length != 0) {
          vol = ((Number(item.thickness) * Number(item.width) * Number(item.length) * qty) / 1000000000).toFixed(4);
        }
        return { ...item, quantity_used: qty, volume_used: vol };
      }
      return item;
    }));
  };

  const handleChangeInputVolume = (id, newVol) => {
    setSelectedInputs(selectedInputs.map(item => {
      if (item.id === id) {
        return { ...item, volume_used: newVol };
      }
      return item;
    }));
  };

  // ─── Handlers cho Output Table ─────────────────────
  const handleAddOutput = () => {
    setOutputs([...outputs, { id: Date.now(), name: '', thickness: '', width: '', length: '', quantity: '', volume: '', status: 'Thành phẩm' }]);
  };

  const handleRemoveOutput = (id) => setOutputs(outputs.filter(i => i.id !== id));

  const handleChangeOutput = (id, field, value) => {
    setOutputs(outputs.map(entry => {
      if (entry.id === id) {
        const updated = { ...entry, [field]: value };
        if (['length', 'width', 'thickness', 'quantity'].includes(field)) {
          const l = parseFloat(updated.length) || 0;
          const w = parseFloat(updated.width) || 0;
          const t = parseFloat(updated.thickness) || 0;
          const q = parseFloat(updated.quantity) || 0;
          if (l > 0 && w > 0 && t > 0 && q > 0) {
            updated.volume = ((l * w * t * q) / 1000000000).toFixed(4);
          }
        }
        return updated;
      }
      return entry;
    }));
  };

  // ─── Save logic ────────────────────────────────────
  const saveLotToDb = (newStatus) => {
    const finalLotId = lotId || `LSX-${Date.now().toString().slice(-5)}`;
    const lot = {
      id: finalLotId,
      name: lotName || 'Lệnh sản xuất',
      date: new Date().toISOString().split('T')[0],
      status: newStatus,
      description,
      targetProducts: selectedTargetProducts,
      inputs: selectedInputs,
      outputs: outputs
    };
    db.saveLot(lot);
    setStatus(newStatus);
    return finalLotId;
  };

  const handleSaveDraft = () => {
    saveLotToDb('Đang sản xuất');
    setModal({
      isOpen: true,
      type: 'alert',
      title: 'Thành công',
      message: 'Đã lưu nháp lệnh sản xuất!'
    });
  };

  const handleConfirmProduction = () => {
    setModal({
      isOpen: true,
      type: 'confirm',
      title: 'Xác nhận hoàn tất',
      message: 'Xác nhận hoàn thành sản xuất? Thành phẩm và phôi dư sẽ được tự động nhập kho.',
      onConfirm: () => {
        const finalLotId = saveLotToDb('Hoàn thành');
        const newInventoryItems = [];

        outputs.forEach(e => {
          const actualQty = Number(e.quantity) || 0;
          const actualVol = Number(e.volume) || 0;

          if (actualQty > 0 || actualVol > 0) {
            let itemType = 'SEMIFINISHED';
            let itemStatus = 'Sẵn sàng';

            if (e.status === 'Phôi dư') {
              itemType = 'SURPLUS';
              itemStatus = 'Tồn kho';
            } else if (e.status === 'Phế phẩm') {
              itemType = 'WASTE';
              itemStatus = 'Loại bỏ';
            }

            newInventoryItems.push({
              name: e.name || 'Phôi',
              length: Number(e.length) || 0,
              width: Number(e.width) || 0,
              thickness: Number(e.thickness) || 0,
              quantity: actualQty,
              volume: actualVol,
              type: itemType,
              status: itemStatus,
              source_lot_id: finalLotId
            });
          }
        });

        if (selectedInputs.length > 0) {
          const idsToRemove = selectedInputs.map(i => i.id);
          db.removeInventory(idsToRemove);

          const partials = selectedInputs.filter(i => {
            const originalQty = Number(i.quantity) || 0;
            const usedQty = Number(i.quantity_used) || 0;
            const originalVol = Number(i.volume) || 0;
            const usedVol = Number(i.volume_used) || 0;

            if (originalQty > 0) {
              return originalQty > usedQty;
            } else {
              return originalVol > usedVol && usedVol >= 0;
            }
          }).map(i => {
            const originalQty = Number(i.quantity) || 0;
            const usedQty = Number(i.quantity_used) || 0;
            const originalVol = Number(i.volume) || 0;
            const usedVol = Number(i.volume_used) || 0;

            let remainingQty = 0;
            let remainingVol = 0;

            if (originalQty > 0) {
              remainingQty = originalQty - usedQty;
              const l = parseFloat(i.length) || 0;
              const w = parseFloat(i.width) || 0;
              const t = parseFloat(i.thickness) || 0;
              remainingVol = ((l * w * t * remainingQty) / 1000000000).toFixed(4);
            } else {
              remainingQty = 0;
              remainingVol = (originalVol - usedVol).toFixed(4);
            }

            return {
              ...i,
              id: `INV-REM-${Date.now().toString().slice(-5)}-${Math.floor(Math.random() * 100)}`,
              quantity: remainingQty,
              volume: remainingVol
            };
          });

          if (partials.length > 0) {
            newInventoryItems.push(...partials);
          }
        }

        if (newInventoryItems.length > 0) {
          db.addInventory(newInventoryItems);
        }

        setModal({
          isOpen: true,
          type: 'alert',
          title: 'Thành công',
          message: 'Đã xác nhận hoàn thành và nhập kho thành công!',
          onConfirm: () => onNavigate('lot-list')
        });
      }
    });
  };

  // ─── Dữ liệu dùng chung cho Modal ──────────────────
  const filteredInventory = availableInventory.filter(item => {
    const matchesTab = invTab === 'ALL' || item.type === invTab;
    const term = removeVietnameseTones(invSearch);
    const matchesSearch =
      removeVietnameseTones(item.name || '').includes(term) ||
      removeVietnameseTones(item.batchId || '').includes(term);
    return matchesTab && matchesSearch;
  });

  const groupedInventory = Object.values(filteredInventory.reduce((acc, item) => {
    const batchId = item.batchId || item.id;
    if (!acc[batchId]) {
      acc[batchId] = {
        batchId,
        type: item.type,
        items: []
      };
    }
    acc[batchId].items.push(item);
    return acc;
  }, {}));

  // ─── Render ────────────────────────────────────────
  return (
    <div className="w-full min-h-screen bg-warm-white text-notion-black font-sans pb-24">
      {/* ── Top Bar ── */}
      <nav className="flex justify-between items-center h-[48px] px-3 md:px-5 border-b border-whisper bg-notion-white sticky top-0 z-40">
        <button
          onClick={() => onNavigate('lot-list')}
          className="flex items-center gap-1.5 text-[14px] font-medium text-warm-gray-500 hover:text-notion-black transition"
        >
          <ArrowLeft size={15} /> Quay lại
        </button>
      </nav>

      {/* ── Main Content ── */}
      <div className="max-w-[1060px] mx-auto px-3 md:px-5 py-6 md:py-8">
        {/* Title Row */}
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[11px] font-bold text-warm-gray-400 uppercase tracking-wider">{lotId || 'Mới'}</span>
            {status === 'Hoàn thành' && (
              <span className="inline-flex items-center gap-1 px-2.5 py-[3px] text-[11px] font-semibold tracking-[0.125px] rounded-full bg-success-green/10 text-success-green uppercase">
              <CheckCircle size={12} /> Đã hoàn thành
              </span>
            )}
          </div>
          <input
            type="text"
            value={lotName}
            onChange={(e) => setLotName(e.target.value)}
            className="w-full text-2xl md:text-[32px] font-bold tracking-[-1px] leading-[1.1] text-notion-black bg-transparent border-none focus:outline-none placeholder-warm-gray-300 mb-3 md:mb-4"
            placeholder="Tên lệnh sản xuất..."
          />
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full text-[14px] text-notion-black bg-notion-white border border-whisper rounded-[6px] px-3 py-2.5 md:py-2 focus:outline-none focus:border-notion-blue placeholder-warm-gray-300 mb-4"
            placeholder="Ghi chú chi tiết lệnh sản xuất..."
          />
        </div>

        {/* Target Products (Order) */}
        <TargetProductTable
          selectedTargetProducts={selectedTargetProducts}
          onChangeProductQuantity={handleChangeProductQuantity}
          onRemoveProduct={handleRemoveProduct}
          onOpenOrderModal={handleOpenOrderModal}
        />

        {/* Bảng Nguyên Liệu Đầu Vào */}
        <InputTable 
          selectedInputs={selectedInputs}
          onOpenInventoryModal={handleOpenInventoryModal}
          onChangeInputQuantity={handleChangeInputQuantity}
          onChangeInputVolume={handleChangeInputVolume}
          onRemoveInputBatch={handleRemoveInputBatch}
          onRemoveInputItem={handleRemoveInputItem}
        />

        {/* Bảng Kết Quả Sản Xuất */}
        <OutputTable 
          outputs={outputs}
          onAddOutput={handleAddOutput}
          onRemoveOutput={handleRemoveOutput}
          onChangeOutput={handleChangeOutput}
        />
      </div>

      {/* ── Fixed Bottom Action Bar ── */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-3 md:p-4 z-50 shadow-[0_-4px_12px_rgba(0,0,0,0.05)]">
        <div className="max-w-[600px] mx-auto flex gap-2 md:gap-3">
          <button
            onClick={handleSaveDraft}
            className="flex-1 flex items-center justify-center gap-1.5 md:gap-2 px-3 py-2.5 md:py-3 rounded-lg text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 active:scale-[0.98] transition"
          >
            <Save size={16} /> <span className="hidden sm:inline">Lưu nháp</span><span className="sm:hidden">Lưu</span>
          </button>
          <button
            onClick={handleConfirmProduction}
            className="flex-[2] md:flex-1 flex items-center justify-center gap-1.5 md:gap-2 px-3 py-2.5 md:py-3 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98] transition"
          >
            <Check size={16} /> <span className="hidden sm:inline">Hoàn tất sản xuất</span><span className="sm:hidden">Hoàn tất</span>
          </button>
        </div>
      </div>

      {/* ── Confirm Modal Popup ── */}
      {modal.isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm px-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-[400px] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="px-5 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <h3 className="font-semibold text-gray-800">{modal.title}</h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600 transition"><X size={18} /></button>
            </div>
            <div className="px-5 py-6 text-gray-600 text-[14px] leading-relaxed">
              {modal.message}
            </div>
            <div className="px-5 py-4 border-t border-gray-100 flex justify-end gap-2 bg-gray-50/50">
              {modal.type === 'confirm' && (
                <button
                  onClick={closeModal}
                  className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 active:scale-[0.98] transition"
                >
                  Huỷ bỏ
                </button>
              )}
              <button
                onClick={() => {
                  if (modal.onConfirm) modal.onConfirm();
                  else closeModal();
                }}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 active:scale-[0.98] transition"
              >
                Xác nhận
              </button>
            </div>
          </div>
        </div>
      )}

      {orderModalOpen && (
        <OrderSelectionModal
          orders={orders}
          selectedTargetProducts={selectedTargetProducts}
          onClose={() => setOrderModalOpen(false)}
          onToggleProductSelection={handleToggleProductSelection}
          onToggleOrderSelection={handleToggleOrderSelection}
        />
      )}

      {/* ── Inventory Modal ── */}
      {inventoryModalOpen && (
        <InventoryModal 
          groupedInventory={groupedInventory}
          selectedInputs={selectedInputs}
          invTab={invTab}
          setInvTab={setInvTab}
          invSearch={invSearch}
          setInvSearch={setInvSearch}
          onClose={() => setInventoryModalOpen(false)}
          onToggleInputSelection={handleToggleInputSelection}
          onToggleModalBatchSelection={handleToggleModalBatchSelection}
        />
      )}
    </div>
  );
}
