-- ============================================================================
-- GLPI-LibreNMS Database Initialization
-- ============================================================================

-- GLPI Database
CREATE DATABASE IF NOT EXISTS glpi
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'glpi'@'%' IDENTIFIED BY 'glpi_secure_pass';
GRANT ALL PRIVILEGES ON glpi.* TO 'glpi'@'%';

-- LibreNMS Database
CREATE DATABASE IF NOT EXISTS librenms
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'librenms'@'%' IDENTIFIED BY 'librenms_secure_pass';
GRANT ALL PRIVILEGES ON librenms.* TO 'librenms'@'%';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verificare
SELECT CONCAT('User: ', user, ' Host: ', host) as Users FROM mysql.user WHERE user IN ('glpi', 'librenms');
SHOW DATABASES LIKE '%glpi%';
SHOW DATABASES LIKE '%librenms%';
