{{ config(materialized='table') }}

with power_data as (
    select * from {{ ref('stg_tsnpdcl') }}
)
    select 
    -- Grouping 
    Circle,
    year,

    -- Calculation 
    round(sum(TotServices),0) as Total_services,
    round(sum(BilledServices),0) as Billed_services,
    round(sum(Units),0) as Units_consumed,
    round(sum(Load),0) as Load_consumed,
    
    from power_data
    group by 1,2