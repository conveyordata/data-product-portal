WITH base AS (
    SELECT * FROM {{ source('marketing_customer_360', 'customer_360') }}
),

scored AS (
    SELECT
        customer_id,

        -- Deterministic proxy score: lower recency + fewer orders + lower revenue = higher churn risk
        ROUND(
            LEAST(1.0,
                GREATEST(0.0,
                    (
                        -- Recency component (days since last order, capped at 180)
                        LEAST(COALESCE(CURRENT_DATE - last_order_date::date, 180), 180) / 180.0 * 0.5
                        -- Frequency component (inverse of order count, capped at 20)
                        + (1 - LEAST(total_orders, 20) / 20.0) * 0.3
                        -- Monetary component (inverse of revenue, capped at 5000)
                        + (1 - LEAST(total_revenue, 5000) / 5000.0) * 0.2
                    )
                )
            )::numeric, 4
        )                           AS churn_score,

        CASE rfm_segment
            WHEN 'Churned'          THEN 'high'
            WHEN 'At Risk'          THEN 'medium'
            WHEN 'Recent'           THEN 'low'
            WHEN 'Loyal Customers'  THEN 'low'
            WHEN 'Champions'        THEN 'very_low'
            ELSE                         'unknown'
        END                         AS churn_risk_tier,

        CURRENT_TIMESTAMP           AS scored_at,
        '1.0.0'                     AS model_version

    FROM base
)

SELECT * FROM scored
