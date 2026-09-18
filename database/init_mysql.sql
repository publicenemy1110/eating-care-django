-- Скрипт для MySQL Workbench
-- Выполните от имени root (или другого пользователя с правами CREATE USER)

CREATE DATABASE IF NOT EXISTS eating_care
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'eating_care_user'@'localhost' IDENTIFIED BY 'eating_care_pass';
CREATE USER IF NOT EXISTS 'eating_care_user'@'127.0.0.1' IDENTIFIED BY 'eating_care_pass';

GRANT ALL PRIVILEGES ON eating_care.* TO 'eating_care_user'@'localhost';
GRANT ALL PRIVILEGES ON eating_care.* TO 'eating_care_user'@'127.0.0.1';

FLUSH PRIVILEGES;

USE eating_care;

-- Таблицы создаёт Django через migrate.
-- После выполнения этого скрипта в терминале проекта запустите:
--   python manage.py migrate
--   python manage.py createsuperuser
