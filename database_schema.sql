-- Supabase PostgreSQL Schema for Product Molding Process
-- Run this in Supabase SQL Editor to create all tables

-- Phiếu sản xuất
CREATE TABLE IF NOT EXISTS production_lots (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    created_date DATE NOT NULL DEFAULT CURRENT_DATE,
    slip_type VARCHAR(20) NOT NULL DEFAULT 'PHOI_GO',
    description TEXT,
    created_by VARCHAR(100),
    updated_at TIMESTAMP,
    data JSONB
);

-- Kho nguyên liệu
CREATE TABLE IF NOT EXISTS inventory (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'RAW',
    length INTEGER,
    width INTEGER,
    thickness INTEGER,
    quantity INTEGER NOT NULL DEFAULT 0,
    volume NUMERIC(10, 4),
    status VARCHAR(100) DEFAULT 'AVAILABLE',
    source_lot_id VARCHAR(50) REFERENCES production_lots(id) ON DELETE SET NULL,
    wood_type VARCHAR(50),
    batch_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Nguyên liệu đầu vào cho phiếu
CREATE TABLE IF NOT EXISTS lot_inputs (
    lot_id VARCHAR(50) REFERENCES production_lots(id) ON DELETE CASCADE,
    inventory_id VARCHAR(50) REFERENCES inventory(id) ON DELETE CASCADE,
    quantity_used INTEGER NOT NULL,
    volume_used NUMERIC(10, 4),
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (lot_id, inventory_id)
);

-- Thành phẩm đầu ra
CREATE TABLE IF NOT EXISTS lot_outputs (
    id SERIAL PRIMARY KEY,
    lot_id VARCHAR(50) REFERENCES production_lots(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    length INTEGER,
    width INTEGER,
    thickness INTEGER,
    quantity INTEGER,
    volume NUMERIC(10, 4) NOT NULL,
    status VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Đơn hàng
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50),
    created_date DATE DEFAULT CURRENT_DATE,
    customer_name VARCHAR(255),
    notes TEXT,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Mục tiêu sản xuất (link phiếu với đơn hàng)
CREATE TABLE IF NOT EXISTS lot_targets (
    lot_id VARCHAR(50) PRIMARY KEY REFERENCES production_lots(id) ON DELETE CASCADE,
    order_id VARCHAR(50) REFERENCES orders(id) ON DELETE SET NULL,
    quantity_produce INTEGER NOT NULL,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_inventory_type ON inventory(type);
CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory(status);
CREATE INDEX IF NOT EXISTS idx_production_lots_status ON production_lots(status);
CREATE INDEX IF NOT EXISTS idx_production_lots_slip_type ON production_lots(slip_type);
CREATE INDEX IF NOT EXISTS idx_lot_inputs_lot_id ON lot_inputs(lot_id);
CREATE INDEX IF NOT EXISTS idx_lot_outputs_lot_id ON lot_outputs(lot_id);
