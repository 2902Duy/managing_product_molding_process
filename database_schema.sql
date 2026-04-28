-- ==========================================================
-- SƠ ĐỒ CƠ SỞ DỮ LIỆU (SCHEMA) QUẢN LÝ SẢN XUẤT GỖ - TINH GỌN
-- Mô hình: Header-Detail & Input-Output Loopback
-- ==========================================================

-- 1. BẢNG PHIẾU SẢN XUẤT (ProductionLots)
-- Phiếu chung cho mọi trường hợp (theo đơn, dự trữ, xẻ dọn kho)
CREATE TABLE ProductionLots (
    id VARCHAR(50) PRIMARY KEY,       -- VD: 'LSX-2026-001'
    name VARCHAR(255),                -- Tên lệnh/ghi chú nhanh
    status VARCHAR(50) NOT NULL,      -- 'Đang làm', 'Hoàn thành', 'Đã hủy'
    created_date DATE NOT NULL,
    description TEXT                  -- Ghi chú chi tiết
);

-- 2. BẢNG KHO (Inventory)
-- Lưu trữ Gỗ tròn (RAW) và Phôi thành phẩm/dư (SEMIFINISHED/SURPLUS)
CREATE TABLE Inventory (
    id VARCHAR(50) PRIMARY KEY,       -- VD: 'NL-001', 'PH-500'
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL,        -- 'RAW', 'SEMIFINISHED', 'SURPLUS'
    length INT,
    width INT,
    thickness INT,
    quantity INT NOT NULL DEFAULT 0,
    volume DECIMAL(10, 4),            -- Thể tích m3
    status VARCHAR(100),              -- 'Sẵn sàng', 'Đã dùng', 'Loại bỏ'
    source_lot_id VARCHAR(50),        -- NỐI NGƯỢC: Sản phẩm này từ lệnh nào mà ra?
    FOREIGN KEY (source_lot_id) REFERENCES ProductionLots(id) ON DELETE SET NULL
);

-- 3. ĐẦU VÀO: NGUYÊN LIỆU SỬ DỤNG (Lot_Inputs)
-- Ghi nhận lấy gỗ gì từ kho ra để làm lệnh này
CREATE TABLE Lot_Inputs (
    lot_id VARCHAR(50) NOT NULL,
    inventory_id VARCHAR(50) NOT NULL,
    quantity_used INT NOT NULL,       -- Số lượng đã xuất kho
    volume_used DECIMAL(10, 4),       -- Thể tích đã xuất (tùy chọn)
    PRIMARY KEY (lot_id, inventory_id),
    FOREIGN KEY (lot_id) REFERENCES ProductionLots(id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES Inventory(id) ON DELETE CASCADE
);

-- 4. ĐẦU RA: KẾT QUẢ SẢN XUẤT (Lot_Outputs)
-- Ghi nhận thành phẩm, phôi dư, hoặc hàng loại bỏ
CREATE TABLE Lot_Outputs (
    id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,       -- Tên quy cách phôi
    length INT NOT NULL,
    width INT NOT NULL,
    thickness INT NOT NULL,
    quantity INT NOT NULL,            -- Số lượng thực tế cắt được
    volume DECIMAL(10, 4),            -- Thể tích m3
    status VARCHAR(100),              -- 'Thành phẩm', 'Phôi dư tận dụng', 'Hàng loại bỏ'
    FOREIGN KEY (lot_id) REFERENCES ProductionLots(id) ON DELETE CASCADE
);

-- ==========================================================
-- DỮ LIỆU MẪU (Mock Data)
-- ==========================================================

-- Tạo 1 phiếu sản xuất
INSERT INTO ProductionLots (id, name, status, created_date, description) 
VALUES ('LSX-001', 'Xẻ phôi chân bàn Sồi', 'Đang làm', '2026-04-28', 'Xẻ từ lô gỗ tròn NL-001');

-- Kho đang có gỗ tròn
INSERT INTO Inventory (id, name, type, length, width, thickness, quantity, volume, status)
VALUES ('NL-001', 'Gỗ Sồi Tròn 2.5m', 'RAW', 2500, 300, 300, 5, 1.125, 'Sẵn sàng');

-- Xuất 2 khúc gỗ tròn để làm phiếu LSX-001
INSERT INTO Lot_Inputs (lot_id, inventory_id, quantity_used, volume_used)
VALUES ('LSX-001', 'NL-001', 2, 0.450);

-- Ghi nhận kết quả cắt ra 40 cái chân bàn
INSERT INTO Lot_Outputs (lot_id, name, length, width, thickness, quantity, volume, status)
VALUES ('LSX-001', 'Phôi chân bàn 750', 750, 80, 80, 40, 0.192, 'Thành phẩm');


