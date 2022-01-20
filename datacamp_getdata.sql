-- create the table
CREATE TABLE views.user_suvscriptions_paid AS (
    SELECT
        us.user_id,
        us.id AS subscribable_id,
        us.subscribable_id AS subsciption_id,
        'individual' AS subscription id
)