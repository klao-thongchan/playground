ALTER TABLE ad_campaign_content
      ADD COLUMN ad_content_bid_currency VARCHAR NOT NULL DEFAULT 'USD',
      ALTER COLUMN ad_content_bid_price TYPE INTEGER USING ad_content_bid_price::money::numeric::float8 * 1000;


CREATE TABLE IF NOT EXISTS v3_test_table_ad_campaign_content (
  ad_campaign_id INTEGER NOT NULL,
  ad_content_id INTEGER NOT NULL,
  ad_content_bid_price INTEGER,
  ad_content_bid_currency VARCHAR NOT NULL DEFAULT 'USD',
  UNIQUE (ad_campaign_id, ad_content_id)
     
) USING ad_content_bid_price::money::numeric::float8 * 1000;


CREATE TABLE IF NOT EXISTS v3_test_table_ad_campaign_content (
  ad_campaign_id INTEGER NOT NULL,
  ad_content_id INTEGER NOT NULL,
  ad_content_bid_price INTEGER,
  ad_content_bid_currency VARCHAR NOT NULL DEFAULT 'USD',
  UNIQUE (ad_campaign_id, ad_content_id)
     
);

ALTER TABLE v3_test_table_ad_campaign_content
ALTER COLUMN ad_content_bid_price TYPE INTEGER USING ad_content_bid_price::money::numeric::float8 * 1000;