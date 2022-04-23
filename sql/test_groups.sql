SELECT CASE
           WHEN g.name = c.test_groups THEN c.test_groups
           ELSE g.name
       END AS name,
       count(c.test_groups) AS all_test_cases,
       count(CASE
                 WHEN c.status = 'OK' THEN 1
             END) AS all_test_cases,
       sum(CASE
               WHEN c.status = 'OK' THEN g.test_value
               ELSE 0
           END) AS total_value
FROM test_groups g
LEFT JOIN test_cases c ON g.name = c.test_groups
GROUP BY CASE
             WHEN g.name = c.test_groups THEN c.test_groups
             ELSE g.name
         END
ORDER BY total_value DESC,
         CASE
             WHEN g.name = c.test_groups THEN c.test_groups
             ELSE g.name
         END