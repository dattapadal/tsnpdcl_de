 {#
    This macro returns the season of given month in Telangana State of India 
#}

{% macro get_season(month) -%}

    case {{ month }}
		when 'JAN' then 'Winter'
        when 'FEB' then 'Spring'
        when 'MAR' then 'Spring'
        when 'APR' then 'Summer'
        when 'MAY' then 'Summer'
        when 'JUN' then 'Monsoon'
        when 'JUL' then 'Monsoon'
        when 'AUG' then 'Early Autumn'
        when 'SEP' then 'Early Autumn'
        when 'OCT' then 'Late Autumn'
        when 'NOV' then 'Late Autumn'
        when 'DEC' then 'Winter'
    end

{%- endmacro %}