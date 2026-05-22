three data systems: 
 - policy administration
 - claims management
 - billing 

Customers, policies, agents
- PostgreSQL-backed policy admin platform

Claims
- vendor-managed claims management system that exports nested JSON files daily.

Billing Transactions live in a third system that produces flat-file CSV exports each night
- live in a third system that produces flat-file CSV exports

Goal: is to to create a unified view by moving all the data to one place. 


Stage 1:

- Build a multi-source extraction layer that reliably pulls from PostgreSQL (policy admin), JSON file drops (claims management), CSV exports (billing), and an external REST API (weather) on a daily schedule.

- Implement a multi-zone data lake architecture on Amazon S3 - landing and processed zones - to enforce clear data lifecycle boundaries and enable controlled promotion of validated data.

- Develop standardised, deduplicated datasets through batch transformation jobs that flatten nested JSON, enforce types, validate referential integrity, and produce Parquet outputs.
