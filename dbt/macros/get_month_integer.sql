 {#
    This macro returns the month number for given month 
#}

{% macro get_month_integer(month) -%}

    case {{ month }}
		when 'JAN' then 1
        when 'FEB' then 2
        when 'MAR' then 3
        when 'APR' then 4
        when 'MAY' then 5
        when 'JUN' then 6
        when 'JUL' then 7
        when 'AUG' then 8
        when 'SEP' then 9
        when 'OCT' then 10
        when 'NOV' then 11
        when 'DEC' then 12
    end

{%- endmacro %}