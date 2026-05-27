-- =============================================================================
-- PROJECT   : Olist Customer Experience Intelligence
-- FILE      : 02_views_core.sql
-- PURPOSE   : Create core analytical views
-- AUTHOR    : Maeen Mohammed
-- =============================================================================

-- ─────────────────────────────────────────
-- View 1: Clean Orders
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW clean_orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::DATE          AS order_purchase_date,
    order_delivered_carrier_date::DATE,
    order_delivered_customer_date::DATE,
    order_estimated_delivery_date::DATE
FROM olist_orders_dataset;


-- ─────────────────────────────────────────
-- View 2: Clean Customers (with Region)
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW clean_customer AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state,
    CASE
        WHEN customer_state IN ('SP', 'RJ', 'MG') THEN 'Region A / Core Market'
        ELSE 'Region B / Expansion Market'
    END AS market_region
FROM customers_dataset;


-- ─────────────────────────────────────────
-- View 3: Clean Order Items
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW clean_order_items AS
SELECT
    order_id,
    product_id,
    seller_id,
    shipping_limit_date::DATE,
    price,
    freight_value
FROM olist_order_items_dataset;


-- ─────────────────────────────────────────
-- View 4: Products List (with English Names)
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW products_list AS
SELECT
    p.product_id,
    COALESCE(t.product_category_name_english, p.product_category_name) AS product_category_name,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
FROM olist_products_dataset p
LEFT JOIN product_category_name_translation t
    ON p.product_category_name = t.product_category_name;


-- ─────────────────────────────────────────
-- View 5: KPI Regions
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW kpi_regions AS
SELECT
    COUNT(DISTINCT co.order_id)                                         AS total_order,
    COUNT(DISTINCT cc.customer_unique_id)                               AS total_customer,
    TRIM(cc.market_region)                                              AS market_region,
    SUM(ci.price + ci.freight_value)                                    AS total_revenue,
    COUNT(DISTINCT ci.product_id)                                       AS distinct_products_sold,
    SUM(ci.price + ci.freight_value) / COUNT(DISTINCT co.order_id)     AS average_order_value
FROM clean_orders co
LEFT JOIN clean_customer cc    ON co.customer_id = cc.customer_id
LEFT JOIN clean_order_items ci ON co.order_id    = ci.order_id
WHERE co.order_status = 'delivered'
GROUP BY TRIM(cc.market_region);


-- ─────────────────────────────────────────
-- View 6: Product KPI
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW product_kpi AS
SELECT
    TRIM(cc.market_region)                                                      AS market_region,
    COALESCE(pl.product_category_name, 'Unknown / Unclassified')               AS product_category_name,
    COUNT(DISTINCT co.order_id)                                                 AS total_order,
    COUNT(DISTINCT cc.customer_id)                                              AS total_customer,
    SUM(ci.price + ci.freight_value)                                            AS total_revenue,
    COUNT(DISTINCT ci.product_id)                                               AS distinct_products_sold,
    SUM(ci.price + ci.freight_value) / COUNT(DISTINCT co.order_id)             AS average_order_value
FROM clean_orders co
LEFT JOIN clean_customer cc    ON co.customer_id  = cc.customer_id
LEFT JOIN clean_order_items ci ON co.order_id     = ci.order_id
LEFT JOIN products_list pl     ON ci.product_id   = pl.product_id
WHERE co.order_status = 'delivered'
GROUP BY
    TRIM(cc.market_region),
    COALESCE(pl.product_category_name, 'Unknown / Unclassified');


-- ─────────────────────────────────────────
-- View 7: Delivery Performance by Region
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW delivery_performance AS
SELECT
    TRIM(cc.market_region)                                                          AS market_region,
    COUNT(DISTINCT co.order_id)                                                     AS total_orders,
    AVG(co.order_delivered_customer_date - co.order_purchase_date)                  AS avg_delivery_days,
    AVG(co.order_delivered_customer_date - co.order_estimated_delivery_date)        AS avg_delay_days,
    SUM(
        CASE
            WHEN (co.order_delivered_customer_date - co.order_estimated_delivery_date) > 0
            THEN 1 ELSE 0
        END
    ) * 1.0 / COUNT(DISTINCT co.order_id)                                          AS late_delivery_rate
FROM clean_orders co
LEFT JOIN clean_customer cc ON co.customer_id = cc.customer_id
WHERE co.order_status = 'delivered'
GROUP BY TRIM(cc.market_region);


-- ─────────────────────────────────────────
-- View 8: Product Performance
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW product_performance AS
SELECT
    TRIM(cc.market_region)                                                          AS market_region,
    COALESCE(pl.product_category_name, 'Unknown / Unclassified')                   AS product_category_name,
    COUNT(DISTINCT co.order_id)                                                     AS total_orders,
    SUM(ci.price + ci.freight_value)                                                AS total_revenue,
    COUNT(DISTINCT ci.product_id)                                                   AS distinct_products_sold,
    SUM(ci.price + ci.freight_value) / COUNT(DISTINCT co.order_id)                 AS average_order_value,
    AVG(co.order_delivered_customer_date - co.order_purchase_date)                  AS avg_delivery_days,
    AVG(co.order_delivered_customer_date - co.order_estimated_delivery_date)        AS avg_delay_days,
    SUM(
        CASE
            WHEN (co.order_delivered_customer_date - co.order_estimated_delivery_date) > 0
            THEN 1 ELSE 0
        END
    ) * 1.0 / COUNT(DISTINCT co.order_id)                                          AS late_delivery_rate
FROM clean_orders co
LEFT JOIN clean_customer cc    ON co.customer_id = cc.customer_id
LEFT JOIN clean_order_items ci ON co.order_id    = ci.order_id
LEFT JOIN products_list pl     ON ci.product_id  = pl.product_id
WHERE co.order_status = 'delivered'
GROUP BY
    TRIM(cc.market_region),
    COALESCE(pl.product_category_name, 'Unknown / Unclassified');


-- ─────────────────────────────────────────
-- View 9: Monthly Sales
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW monthly_sales AS
SELECT
    TRIM(cc.market_region)                                              AS market_region,
    COUNT(DISTINCT co.order_id)                                         AS total_orders,
    SUM(ci.price + ci.freight_value)                                    AS total_revenue,
    COUNT(DISTINCT ci.product_id)                                       AS distinct_products_sold,
    SUM(ci.price + ci.freight_value) / COUNT(DISTINCT co.order_id)     AS average_order_value,
    DATE_TRUNC('month', co.order_purchase_date)::DATE                   AS order_month,
    EXTRACT(YEAR FROM co.order_purchase_date)                           AS order_year
FROM clean_orders co
LEFT JOIN clean_order_items ci ON co.order_id    = ci.order_id
LEFT JOIN clean_customer cc    ON co.customer_id = cc.customer_id
WHERE co.order_status = 'delivered'
GROUP BY
    TRIM(cc.market_region),
    DATE_TRUNC('month', co.order_purchase_date)::DATE,
    EXTRACT(YEAR FROM co.order_purchase_date)
ORDER BY market_region, order_month;


-- ─────────────────────────────────────────
-- View 10: Customer Analysis
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW customer_analysis AS
SELECT
    cc.customer_unique_id,
    TRIM(cc.market_region)                                              AS market_region,
    COUNT(DISTINCT co.order_id)                                         AS total_orders,
    SUM(ci.price + ci.freight_value)                                    AS total_spent,
    SUM(ci.price + ci.freight_value) / COUNT(DISTINCT co.order_id)     AS avg_order_value,
    MIN(co.order_purchase_date)                                         AS first_purchase,
    MAX(co.order_purchase_date)                                         AS last_purchase,
    CASE
        WHEN COUNT(DISTINCT co.order_id) = 1 THEN 'One-time'
        ELSE 'Repeat'
    END AS customer_type
FROM clean_orders co
LEFT JOIN clean_customer cc    ON co.customer_id = cc.customer_id
LEFT JOIN clean_order_items ci ON co.order_id    = ci.order_id
WHERE co.order_status = 'delivered'
GROUP BY
    cc.customer_unique_id,
    TRIM(cc.market_region);


-- ─────────────────────────────────────────
-- View 11: Customer Summary
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW customer_summary AS
SELECT
    market_region,
    COUNT(*)                                                            AS total_customers,
    SUM(CASE WHEN customer_type = 'One-time' THEN 1 ELSE 0 END)        AS one_time_customers,
    SUM(CASE WHEN customer_type = 'Repeat'   THEN 1 ELSE 0 END)        AS repeat_customers,
    AVG(total_spent)                                                    AS avg_customer_spend
FROM customer_analysis
GROUP BY market_region;


-- ─────────────────────────────────────────
-- View 12: Product Customer Behavior
-- ─────────────────────────────────────────
CREATE OR REPLACE VIEW product_customer_behavior AS
SELECT
    pl.product_category_name,
    COUNT(DISTINCT c.customer_unique_id)                                AS total_customers,
    COUNT(DISTINCT CASE WHEN customer_orders.total_orders > 1
        THEN c.customer_unique_id END)                                  AS repeat_customers,
    COUNT(DISTINCT CASE WHEN customer_orders.total_orders = 1
        THEN c.customer_unique_id END)                                  AS one_time_customers,
    COUNT(DISTINCT CASE WHEN customer_orders.total_orders > 1
        THEN c.customer_unique_id END) * 1.0
        / NULLIF(COUNT(DISTINCT c.customer_unique_id), 0)              AS repeat_rate
FROM clean_orders co
LEFT JOIN clean_order_items ci     ON co.order_id         = ci.order_id
LEFT JOIN products_list pl         ON ci.product_id       = pl.product_id
LEFT JOIN clean_customer c         ON co.customer_id      = c.customer_id
LEFT JOIN (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT co.order_id) AS total_orders
    FROM clean_orders co
    JOIN clean_customer c ON co.customer_id = c.customer_id
    WHERE co.order_status = 'delivered'
    GROUP BY c.customer_unique_id
) customer_orders ON c.customer_unique_id = customer_orders.customer_unique_id
WHERE co.order_status = 'delivered'
GROUP BY pl.product_category_name;
