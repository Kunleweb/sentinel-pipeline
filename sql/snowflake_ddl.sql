CREATE DATABASE IF NOT EXISTS SENTINEL;

CREATE SCHEMA IF NOT EXISTS SENTINEL.STAGING;
CREATE SCHEMA IF NOT EXISTS SENTINEL.WAREHOUSE;


CREATE OR REPLACE FILE FORMAT SENTINEL.STAGING.PARQUET_FMT
    TYPE               = PARQUET
    SNAPPY_COMPRESSION = TRUE
    NULL_IF            = ('');


CREATE STORAGE INTEGRATION IF NOT EXISTS S3_SENTINEL_INTEGRATION
    TYPE                      = EXTERNAL_STAGE
    STORAGE_PROVIDER          = 'S3'
    ENABLED                   = TRUE
    STORAGE_AWS_ROLE_ARN      = 'arn:aws:iam::738090245246:role/snowflake-sentinel-role'
    STORAGE_ALLOWED_LOCATIONS = ('s3://sentinel-kunle/processed/');


CREATE OR REPLACE STAGE SENTINEL.STAGING.S3_PROCESSED_STAGE
    STORAGE_INTEGRATION = S3_SENTINEL_INTEGRATION
    URL                 = 's3://sentinel-kunle/processed/'
    FILE_FORMAT         = SENTINEL.STAGING.PARQUET_FMT;


CREATE OR REPLACE TABLE SENTINEL.STAGING.claims_fact (
    claim_id         VARCHAR,
    policy_id        VARCHAR,
    customer_id      VARCHAR,
    incident_date    DATE,
    report_date      DATE,
    incident_city    VARCHAR,
    incident_state   VARCHAR,
    incident_zip     VARCHAR,
    incident_type    VARCHAR,
    description      VARCHAR,
    status           VARCHAR,
    claim_amount     NUMBER(18, 2),
    approved_amount  NUMBER(18, 2),
    created_at       TIMESTAMP_TZ
);

CREATE OR REPLACE TABLE SENTINEL.STAGING.payments (
    payment_id        VARCHAR,
    claim_id          VARCHAR,
    adjuster_id       VARCHAR,
    payment_amount    NUMBER(18, 2),
    payment_type      VARCHAR,
    payment_timestamp TIMESTAMP_TZ
);

CREATE OR REPLACE TABLE SENTINEL.STAGING.dim_customer (
    customer_id  VARCHAR,
    first_name   VARCHAR,
    last_name    VARCHAR,
    dob          DATE,
    email        VARCHAR,
    city         VARCHAR,
    state        VARCHAR
);

CREATE OR REPLACE TABLE SENTINEL.STAGING.dim_agent (
    agent_id    VARCHAR,
    agent_name  VARCHAR,
    hire_date   DATE,
    territory   VARCHAR
);

CREATE OR REPLACE TABLE SENTINEL.STAGING.dim_policy (
    policy_id       VARCHAR,
    customer_id     VARCHAR,
    agent_id        VARCHAR,
    coverage_id     VARCHAR,
    start_date      DATE,
    end_date        DATE,
    premium_amount  NUMBER(21, 2),
    status          VARCHAR,
    coverage_type   VARCHAR
);

CREATE OR REPLACE TABLE SENTINEL.STAGING.dim_coverage (
    coverage_id     VARCHAR,
    coverage_code   VARCHAR,
    coverage_limit  NUMBER(21, 2),
    deductible      NUMBER(21, 2)
);

CREATE OR REPLACE TABLE SENTINEL.STAGING.weather_daily (
    weather_date  DATE,
    zip_code      VARCHAR,
    city          VARCHAR,
    state         VARCHAR,
    severity      VARCHAR
);


CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.claims_fact (
    claim_id         VARCHAR        NOT NULL PRIMARY KEY,
    policy_id        VARCHAR,
    customer_id      VARCHAR,
    incident_date    DATE,
    report_date      DATE,
    incident_city    VARCHAR,
    incident_state   VARCHAR,
    incident_zip     VARCHAR,
    incident_type    VARCHAR,
    description      VARCHAR,
    status           VARCHAR,
    claim_amount     NUMBER(18, 2),
    approved_amount  NUMBER(18, 2),
    created_at       TIMESTAMP_TZ
);

CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.payments (
    payment_id        VARCHAR        NOT NULL PRIMARY KEY,
    claim_id          VARCHAR,
    adjuster_id       VARCHAR,
    payment_amount    NUMBER(18, 2),
    payment_type      VARCHAR,
    payment_timestamp TIMESTAMP_TZ
);

CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.dim_customer (
    customer_id  VARCHAR  NOT NULL PRIMARY KEY,
    first_name   VARCHAR,
    last_name    VARCHAR,
    dob          DATE,
    email        VARCHAR,
    city         VARCHAR,
    state        VARCHAR
);

CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.dim_agent (
    agent_id    VARCHAR  NOT NULL PRIMARY KEY,
    agent_name  VARCHAR,
    hire_date   DATE,
    territory   VARCHAR
);

CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.dim_policy (
    policy_id       VARCHAR  NOT NULL PRIMARY KEY,
    customer_id     VARCHAR,
    agent_id        VARCHAR,
    coverage_id     VARCHAR,
    start_date      DATE,
    end_date        DATE,
    premium_amount  NUMBER(21, 2),
    status          VARCHAR,
    coverage_type   VARCHAR
);

CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.dim_coverage (
    coverage_id     VARCHAR  NOT NULL PRIMARY KEY,
    coverage_code   VARCHAR,
    coverage_limit  NUMBER(21, 2),
    deductible      NUMBER(21, 2)
);

CREATE TABLE IF NOT EXISTS SENTINEL.WAREHOUSE.weather_daily (
    weather_date  DATE     NOT NULL,
    zip_code      VARCHAR  NOT NULL,
    city          VARCHAR,
    state         VARCHAR,
    severity      VARCHAR,
    PRIMARY KEY (weather_date, zip_code)
);
