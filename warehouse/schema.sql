-- ============================================================
-- Schema: bi_support_telkom_ridar
-- Dashboard BI Monitoring Work Order Telkom Ridar
-- ============================================================

CREATE DATABASE IF NOT EXISTS bi_support_telkom_ridar
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bi_support_telkom_ridar;

-- ============================================================
-- TABLE: workorders (Flat Fact Table - Staging + Warehouse)
-- ============================================================
CREATE TABLE IF NOT EXISTS workorders (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Waktu
    tanggal DATE,
    bulan TINYINT,
    nama_bulan VARCHAR(20),
    tahun SMALLINT,
    kuartal TINYINT,
    nama_hari VARCHAR(20),

    -- Identitas WO
    wo_id VARCHAR(100),
    sc_id VARCHAR(100),
    track_id VARCHAR(100),

    tanggal_order DATE,
    tanggal_komitmen DATE,

    -- STO
    sto VARCHAR(100),
    branch VARCHAR(100),
    sektor VARCHAR(100),
    hsa VARCHAR(100),
    sto_input VARCHAR(100),

    -- Teknisi
    nik_teknisi VARCHAR(50),
    nama_teknisi VARCHAR(150),
    mitra VARCHAR(150),
    korlap VARCHAR(150),
    komandan_team VARCHAR(150),
    cp VARCHAR(150),
    spv VARCHAR(150),

    -- Pelanggan
    nama_pelanggan VARCHAR(255),
    nama_contact VARCHAR(255),
    uic VARCHAR(100),
    segment VARCHAR(100),
    layanan VARCHAR(100),
    alamat_instalasi TEXT,
    koordinat_lat DECIMAL(11,8),
    koordinat_lon DECIMAL(11,8),

    -- Kendala
    kendala_pt1 TEXT,
    kategori_roc VARCHAR(150),
    kategori_solusi VARCHAR(150),
    solusi_kendala TEXT,
    keterangan TEXT,

    solusi_maintenance TEXT,
    solusi_optima TEXT,
    solusi_sdi_daman TEXT,

    -- Infrastruktur
    odp VARCHAR(255),
    odc VARCHAR(255),
    gpon VARCHAR(255),
    feeder VARCHAR(255),
    distribusi VARCHAR(255),
    core_distribusi VARCHAR(255),
    datek1 VARCHAR(255),
    datek_inputan VARCHAR(255),
    datek_real VARCHAR(255),
    base_tray_odc VARCHAR(100),
    port_base_tray_odc VARCHAR(100),
    hasil_ukur_odp VARCHAR(255),
    hasil_ukur_distribusi VARCHAR(255),
    hasil_ukur_feeder VARCHAR(255),

    -- Status
    status_wo VARCHAR(100),
    status_sc VARCHAR(100),
    status_final VARCHAR(100),

    -- Durasi
    durasi_hari DECIMAL(10,2),
    durasi_pengerjaan_menit INT,
    durasi_grup VARCHAR(100),
    durasi_grup_pengerjaan VARCHAR(100),
    durasi_manja VARCHAR(100),

    -- Monitoring
    tgl_input_hd_gdocs DATE,

    is_sla_tercapai TINYINT(1) DEFAULT 0,
    is_workfail TINYINT(1) DEFAULT 0,
    is_unsc TINYINT(1) DEFAULT 0,

    total_eskalasi INT DEFAULT 0,
    jumlah_kendala INT DEFAULT 1,

    -- ETL
    status_etl ENUM('pending','processed','failed') DEFAULT 'processed',
    source_file VARCHAR(255),
    imported_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_wo (wo_id),
    INDEX idx_track (track_id),
    INDEX idx_sto (sto),
    INDEX idx_teknisi (nik_teknisi),
    INDEX idx_status (status_wo),
    INDEX idx_tanggal (tanggal),
    INDEX idx_kendala (kendala_pt1(100)),
    INDEX idx_bulan_tahun (bulan, tahun),
    INDEX idx_sla (is_sla_tercapai),
    INDEX idx_workfail (is_workfail)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: etl_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    etl_name VARCHAR(100),
    source_file VARCHAR(255),
    status ENUM('success','failed','running') DEFAULT 'running',
    total_records INT DEFAULT 0,
    inserted_records INT DEFAULT 0,
    skipped_records INT DEFAULT 0,
    failed_records INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP NULL,
    duration_seconds DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: jobs_batches (job/batch tracking)
-- ============================================================
CREATE TABLE IF NOT EXISTS jobs_batches (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(255) NOT NULL,
    name VARCHAR(255) DEFAULT NULL,
    payload LONGTEXT,
    queue VARCHAR(255) DEFAULT NULL,
    attempts INT DEFAULT 0,
    failed_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY jobs_batches_uuid_unique (uuid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE: obs (generic key/value store placeholder)
-- ============================================================
CREATE TABLE IF NOT EXISTS obs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) DEFAULT NULL,
    `value` LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY obs_key_unique (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
