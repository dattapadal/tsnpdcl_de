{{ config(materialized='view') }}

select 
    Circle		,	
    Division	,	
    SubDivision	,	
    Section		,	
    Area		,	
    CatCode     ,
    replace(CatDesc, 'GENERAL', 'DOMESTIC') as CatDesc,	
    TotServices	,	
    BilledServices,	
    Units			,
    Load			,
    year			,
    {{ get_month_integer('month') }} as month_int,
    {{ get_season('month') }} as season,

from {{ source('staging', 'tsnpdcl')}}
where
    Circle is not null and 
    Division is not null and 
    SubDivision is not null and 
    Section is not null


{% if var('is_test_run', default=true) %}

limit 100

{% endif %}