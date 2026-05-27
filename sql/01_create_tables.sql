-- =============================================================================
-- PROJECT   : Olist Customer Experience Intelligence
-- FILE      : 01_create_tables.sql
-- PURPOSE   : Create all database tables
-- AUTHOR    : Maeen Mohammed
-- =============================================================================

-- Customers
CREATE TABLE customers_dataset (
    customer_id               TEXT,
    customer_unique_id        TEXT,
    customer_zip_code_prefix  VARCHAR(100),
    customer_city             TEXT,
    customer_state            TEXT
);

-- Geolocation
CREATE TABLE olist_geolocation_dataset (
    geolocation_zip_code_prefix  TEXT,
    geolocation_lat              TEXT,
    geolocation_lng              TEXT,
    geolocation_city             TEXT,
    geolocation_state            TEXT
);

-- Order Items
CREATE TABLE olist_order_items_dataset (
    order_id             TEXT,
    order_item_id        TEXT,
    product_id           TEXT,
    seller_id            TEXT,
    shipping_limit_date  TEXT,
    price                NUMERIC,
    freight_value        NUMERIC
);

-- Order Payments
CREATE TABLE olist_order_payments_dataset (
    order_id              TEXT,
    payment_sequential    NUMERIC,
    payment_type          TEXT,
    payment_installments  NUMERIC,
    payment_value         NUMERIC
);

-- Order Reviews
CREATE TABLE olist_order_reviews_dataset (
    review_id               TEXT,
    order_id                TEXT,
    review_score            NUMERIC,
    review_comment_title    TEXT,
    review_comment_message  TEXT,
    review_creation_date    TEXT,
    review_answer_timestamp TEXT
);

-- Orders
CREATE TABLE olist_orders_dataset (
    order_id                       TEXT,
    customer_id                    TEXT,
    order_status                   TEXT,
    order_purchase_timestamp       TEXT,
    order_approved_at              TEXT,
    order_delivered_carrier_date   TEXT,
    order_delivered_customer_date  TEXT,
    order_estimated_delivery_date  TEXT
);

-- Products
CREATE TABLE olist_products_dataset (
    product_id                   TEXT,
    product_category_name        TEXT,
    product_name_lenght          TEXT,
    product_description_lenght   NUMERIC,
    product_photos_qty           NUMERIC,
    product_weight_g             NUMERIC,
    product_length_cm            NUMERIC,
    product_height_cm            NUMERIC,
    product_width_cm             NUMERIC
);

-- Sellers
CREATE TABLE olist_sellers_dataset (
    seller_id                TEXT,
    seller_zip_code_prefix   TEXT,
    seller_city              TEXT,
    seller_state             TEXT
);

-- Product Category Translation
CREATE TABLE product_category_name_translation (
    product_category_name          TEXT,
    product_category_name_english  TEXT
);
