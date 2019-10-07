{% for i in range(values.iterations) %}
Iteration {{ i }}
{% endfor %}
Hello World {{ values }}

Tomelizer:
    - bool:
        - {{ True|tomelize }}
        - {{ False|tomelize }}
