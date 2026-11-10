-- À exécuter en tant que root MySQL 8 (une seule fois), puis : alembic upgrade head  (ou database/schema.sql)
CREATE DATABASE IF NOT EXISTS darmate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'darmate_user'@'localhost' IDENTIFIED BY 'ChangeMe!2026';
GRANT ALL PRIVILEGES ON darmate.* TO 'darmate_user'@'localhost';
FLUSH PRIVILEGES;
