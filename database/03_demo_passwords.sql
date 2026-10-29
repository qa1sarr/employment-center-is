-- Жұмыспен қамту орталығының ақпараттық жүйесі
-- 3-файл. Демо құпиясөз: барлық пайдаланушыға 123456 (SHA-256 хэшімен сақталады).
-- Бұл хэш src/business/auth_service.py ішіндегі hash_password() нәтижесімен бірдей.

USE EmploymentCenter;
GO

UPDATE users
SET password_hash = LOWER(CONVERT(VARCHAR(64), HASHBYTES('SHA2_256', '123456'), 2));
GO

SELECT user_id, full_name, email, role, LEFT(password_hash, 12) AS hash_start FROM users;
GO
