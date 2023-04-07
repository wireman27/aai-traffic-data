# Airports Authority of India - Traffic Data

The Airports Authority of India releases monthly airport-specific aircraft movement, passenger and freight data on [its website](https://www.aai.aero/en/business-opportunities/aai-traffic-news).

The data is spread over different tables in different PDF files and does not contain airport codes.

The data in [data.csv](./data.csv) unifies the data in one file with the following columns:
  - `airport_code`
  - `aircraftmov_intl`
  - `aircraftmov_domestic`
  - `pax_intl`
  - `pax_domestic`
  - `freight_intl`
  - `month`
  - `year`

This should enable SQL-like queries to answer many questions about trends in India's aviation traffic.

_(I used ChatGPT to get IATA codes for a list of poorly written airports - it got about 85% of them right but still needed a final manual check)_
