CREATE USER stock_user WITH PASSWORD 'stock_pass';
CREATE DATABASE stock_data OWNER stock_user;
GRANT ALL PRIVILEGES ON DATABASE stock_data TO stock_user;