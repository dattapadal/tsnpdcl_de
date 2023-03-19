{{ config(
    materialized='table',
    partition_by={
      "field": "year",
      "data_type": "int64",
      "range": {
          "start": 2019,
          "end": 2023,
          "interval": 1,
      },
    }
)}}

select
    year,
    Circle,
    season,
     
    Total_services,
    Billed_services,
    Units_consumed,
    Load_consumed,

from {{ ref('circle_seasonal_power_usage') }}