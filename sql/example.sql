SELECT 
  customers.customer_name, 
  COUNT(orders.order_id) AS total_orders
FROM 
  customers 
  JOIN orders 
    ON customers.customer_id = orders.customer_id
GROUP BY 
  customers.customer_name
HAVING 
  COUNT(orders.order_id) >= 2
ORDER BY 
  total_orders DESC;