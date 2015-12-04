psql -c "CREATE USER tot with PASSWORD 'tot' CREATEDB SUPERUSER;" -U postgres
psql -c "CREATE DATABASE opencivicdata;" -U postgres
psql -c "CREATE EXTENSION postgis;" -U postgres -d opencivicdata
gunzip -c /dump.sql.gz | psql -U postgres -d opencivicdata
