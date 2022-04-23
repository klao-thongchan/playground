-- The question is
-- What fraction of people who sstart live DataCamp course, and have a subscription, finish them?

-- create the table
CREATE TABLE views.user_suvscriptions_paid AS 
(
    SELECT
        us.user_id,
        us.id AS subscribable_id,
        us.subscribable_id AS subsciption_id,
        'individual' AS subscription_type,
        us.created_at AS started_at,
        COALESCE(us.revoked_at, us.cancelled_on, us.paused_on, us_expiration) AS ended_at,
        CASE WHEN pay_method IS NOT NULL AND pay_method NOT IN ('free', 'manual_admin')
            THEN TRUE
            ELSE FALSE
        END AS paid,
        c.code AS coupon_code,
        CASE WHEN s.yearly
            THEN s.price / 12
            ELSE s.price
        END AS amortized_original_price, -- Price when you don't have a coupon
        CASE WHEN s.yearly
            THEN
                (CASE WHEN c.reduction IS NOT NULL AND s.provider_coupon IS NULL
                    THEN (1 - c.reduction) * price)
                    ELSE price
                END) / 12
            ELSE
                (CASE WHEN c.reduction IS NOT NULL AND s.provider_coupon IS NULL
                    THEN (1 - c.reduction) * price)
                    ELSE price
                END)
            END AS amortized_reduced_price,
        us.created_at * c.duration_seconds * INTERVAL '1 second' AS reduction_ended_at,
        s.yearly
    FROM main_app.user_subscriptions us
    INNER JOIN main_app.subscriptions s ON us.subsciption_id = s.id
    LEFT JOIN main_app.coupon c ON us.coupon_id = c.id
)
UNION
(
    SELECT ug.user_id,
        gs.id AS subscribable_id,
        gs.subsciption_id AS subscription_id,
        'group' AS subscription_type,
        us.created_at AS started_at,
        COALESCE(ug.deleted_at, gs.deleted_at, gs.cancelled_on, gs.expiration)
        (g.is_premium AND g.group_type = 'enterprise' AND ug.billing_enabled)
        NULL AS coupon_code, -- Groups do not have coupons
        (CASE WHEN is_premium AND group_type = 'enterprise' AND billing_enabled)
        (CASE WHEN is_premium AND group_type = 'enterprise' AND billing_enabled)
        NULL AS reduction_ended_at,
        TRUE AS yearly
    FROM enterprise_app.user_groups ug
)