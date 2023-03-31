SELECT first_name, last_name, email
FROM customers1
UNION
SELECT first_name, last_name, email
FROM customers2;


SELECT customers.first_name, customers.last_name, orders.order_date
FROM customers
INNER JOIN orders
ON customers.customer_id = orders.customer_id;


SELECT first_name, last_name, email
FROM customers
WHERE customer_id IN (
  SELECT customer_id
  FROM orders
  WHERE order_date >= DATEADD(day, -30, GETDATE())
);