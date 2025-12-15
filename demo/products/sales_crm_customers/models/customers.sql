SELECT
    id,
    first_name,
    last_name,
    email,
    signup_date
FROM
    {{ source('sources', 'crm_customers') }}
