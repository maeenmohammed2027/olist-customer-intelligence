-- =============================================================================
-- PROJECT   : Olist Customer Experience Intelligence
-- FILE      : 03_views_advanced.sql
-- PURPOSE   : Advanced analytical views — window functions, CTEs, RFM
-- AUTHOR    : Maeen Mohammed
-- =============================================================================

-- View 1: Product Revenue Ranking by Region (Window Function)
CREATE OR REPLACE VIEW product_revenue_ranking AS
SELECT
    TRIM(cc.market_region)                                                      AS market_region,
    COALESCE(pl.product_category_name, 'Unknown / Unclassified')               AS product_category_name,
    COUNT(DISTINCT ci.order_id)                                                 AS total_orders,
    COUNT(DISTINCT cc.customer_id)                                              AS total_customer,
    SUM(ci.price + ci.freight_value)                                            AS total_revenue,
    COUNT(DISTINCT ci.product_id)                                               AS distinct_products_sold,
    SUM(ci.price + ci.freight_value) / COUNT(DISTINCT co.order_id)             AS average_order_value,
    RANK() OVER (
        PARTITION BY TRIM(cc.market_region)
        ORDER BY SUM(ci.price + ci.freight_value) DESC
    ) AS revenue_rank
FROM clean_orders co
LEFT JOIN clean_customer cc    ON co.customer_id = cc.customer_id
LEFT JOIN clean_order_items ci ON co.order_id    = ci.order_id
LEFT JOIN products_list pl     ON ci.product_id  = pl.product_id
WHERE co.order_status = 'delivered'
GROUP BY
    TRIM(cc.market_region),
    COALESCE(pl.product_category_name, 'Unknown / Unclassified');


-- View 2: Month-over-Month Revenue Growth (LAG Window Function + CTE)
CREATE OR REPLACE VIEW month_growth AS
WITH revenue_calc AS (
    SELECT
        TRIM(market_region)     AS market_region,
        order_month,
        total_revenue           AS current_month_revenue,
        LAG(total_revenue) OVER (
            PARTITION BY TRIM(market_region)
            ORDER BY order_month
        )                       AS previous_month_revenue
    FROM monthly_sales
)
SELECT
    market_region,
    order_month,
    ROUND(current_month_revenue::NUMERIC, 2)    AS current_month_revenue,
    ROUND(previous_month_revenue::NUMERIC, 2)   AS previous_month_revenue,
    ROUND(
        (current_month_revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0) * 100, 2
    )                                           AS monthly_growth_pct
FROM revenue_calc
WHERE previous_month_revenue IS NOT NULL
ORDER BY market_region, order_month;


-- View 3: Customer Retention RFM Analysis (NTILE + CTE)
CREATE OR REPLACE VIEW customer_retention AS
WITH score_raw AS (
    SELECT
        market_region,
        customer_unique_id,
        total_orders    AS frequency,
        total_spent     AS monetary,
        first_purchase,
        last_purchase
    FROM customer_analysis
),
rfm_scores AS (
    SELECT
        market_region,
        customer_unique_id,
        frequency,
        monetary,
        last_purchase,
        NTILE(5) OVER (ORDER BY last_purchase DESC)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)       AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)        AS m_score
    FROM score_raw
)
SELECT
    market_region,
    customer_unique_id,
    r_score,
    f_score,
    m_score,
    CONCAT(r_score, f_score, m_score)   AS rfm_combined,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3                   THEN 'Loyal Customers'
        WHEN r_score <= 2 AND f_score <= 2                   THEN 'At Risk / Lost'
        ELSE                                                      'Potential Loyalist'
    END AS customer_segment
FROM rfm_scores;


-- =============================================================================
-- DATA VALIDATION QUERIES
-- =============================================================================

-- Check 1: Total Revenue (delivered orders only)
SELECT ROUND(SUM(oi.price + oi.freight_value)::NUMERIC, 2) AS total_revenue
FROM olist_order_items_dataset oi
JOIN olist_orders_dataset o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered';

-- Check 2: Total Delivered Orders
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM olist_orders_dataset
WHERE order_status = 'delivered';

-- Check 3: Total Unique Customers
SELECT COUNT(DISTINCT customer_unique_id) AS total_customers
FROM customer_analysis;

-- Check 4: Repeat Rate %
SELECT
    ROUND(
        COUNT(CASE WHEN total_orders > 1 THEN 1 END) * 100.0
        / COUNT(*), 2
    ) AS repeat_rate_pct
FROM customer_analysis;

-- Check 5: Average Delivery Days
SELECT ROUND(AVG(avg_delivery_days)::NUMERIC, 2) AS avg_delivery_days
FROM delivery_performance;

-- Check 6: Late Delivery Rate by Region
SELECT
    market_region,
    ROUND(late_delivery_rate * 100, 2) AS late_delivery_pct
FROM delivery_performance
ORDER BY market_region;
