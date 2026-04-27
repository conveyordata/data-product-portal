WITH base AS (
    SELECT * FROM {{ source('marketing_customer_360', 'customer_360') }}
),

email_segment AS (
    SELECT
        MD5(customer_id::text || 'email')  AS segment_id,
        customer_id,
        'Lifecycle Email'   AS segment_name,
        'email'             AS channel,
        rfm_segment         AS rfm_tier,
        CURRENT_DATE        AS activation_date,
        'CAMP-EMAIL-001'    AS campaign_id
    FROM base
    WHERE rfm_segment IN ('Champions', 'Loyal Customers', 'At Risk')
),

paid_media_segment AS (
    SELECT
        MD5(customer_id::text || 'paid_media') AS segment_id,
        customer_id,
        'Lookalike Audience' AS segment_name,
        'paid_media'         AS channel,
        rfm_segment          AS rfm_tier,
        CURRENT_DATE         AS activation_date,
        'CAMP-PAID-001'      AS campaign_id
    FROM base
    WHERE rfm_segment = 'Churned'
)

SELECT * FROM email_segment
UNION ALL
SELECT * FROM paid_media_segment
