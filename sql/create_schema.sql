CREATE SCHEMA IF NOT EXISTS netflix_historical;

GRANT USAGE ON SCHEMA netflix_historical TO stock_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA netflix_historical TO stock_user;

GRANT USAGE, SELECT, UPDATE ON SEQUENCE stock_prices_id_seq TO stock_user;