import pandas as pd

# Data
result = [
    ('1', '20', '130', '2', '2024-08-23 17:16:37.793118'),
    ('2', '13', '26', '2', '2024-06-09 17:16:37.793118'),
    ('3', '6', '146', '3', '2024-08-23 17:16:37.793118'),
    ('4', '30', '15', '3', '2024-08-25 17:16:37.793118'),
    ('5', '23', '59', '1', '2024-11-02 17:16:37.793118')
]

column_names = ['cart_id', 'customer_id', 'product_id', 'quantity', 'added_date']

# Create DataFrame
record = pd.DataFrame(result, columns=column_names)

# Display DataFrame
print(record)