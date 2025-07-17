-- Check schema-level permissions for a user
SELECT grantee, privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'netflix_historical';


-- Check table-level permissions for a user
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE table_name = 'stock_prices';


SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'netflix_historical';

GRANT USAGE ON SCHEMA netflix_historical TO stock_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA netflix_historical TO stock_user;

GRANT USAGE, SELECT, UPDATE ON SEQUENCE netflix_historical.stock_prices_id_seq TO stock_user;

SELECT * FROM netflix_historical.stock_prices;
TRUNCATE TABLE netflix_historical.stock_prices;

DROP TABLE IF EXISTS netflix_historical.stock_prices;
CREATE TABLE IF NOT EXISTS netflix_historical.stock_prices (
    id SERIAL PRIMARY KEY,
    stock_symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price NUMERIC(10, 2) NOT NULL,
    high_price NUMERIC(10, 2) NOT NULL,
    low_price NUMERIC(10, 2) NOT NULL,
    close_price NUMERIC(10, 2) NOT NULL,
    volume BIGINT NOT NULL
);


SELECT COUNT(*) FROM netflix_historical.stock_prices;
