{{ config(materialized='table') }}

select
    generate_series(
        '2000-01-01'::date,
        '2030-12-31'::date,
        '1 day'::interval
    )::date as date_day
