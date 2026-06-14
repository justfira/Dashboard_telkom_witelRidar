import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.db import execute_ddl, run_query

sql = '''
-- Create jobs_batches (simple batch/job tracking)
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

-- Create obs placeholder table (generic key/value store)
CREATE TABLE IF NOT EXISTS obs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) DEFAULT NULL,
    `value` LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY obs_key_unique (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
'''

print("Applying DDL to create missing tables...")
execute_ddl(sql)
print("Done. Verifying tables:")
for t in ['jobs_batches', 'obs', 'failed_jobs', 'workorders', 'etl_logs']:
    try:
        rows = run_query(f"SELECT COUNT(*) AS c FROM {t}")
        c = rows[0]['c'] if rows else 0
        print(f"{t}: {c}")
    except Exception as e:
        print(f"{t}: ERROR: {e}")
