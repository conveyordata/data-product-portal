---
id: schema-information
title: Output port Schema information
sidebar_label: Schema information
sidebar_position: 7
---

# Output port Schema information

The goal of Portal is to provide data product consumers with all necessary information to understand whether an output port fits their needs.
The goal of this feature is to give consumers a clear view of the structure of the data behind an output port: the tables/objects it exposes and the properties (columns) of each, together with their types, descriptions and examples.

Portal is not a catalog or schema registry itself. Instead, it lets data product producers ingest the schema they already describe in their data contract, so consumers can discover the shape of the data without leaving the portal.

## BitOL Schema summary

Portal ingests schema information from a [BitOL Open Data Contract Standard (ODCS)](https://bitol-io.github.io/open-data-contract-standard/) data contract.
This means you can reuse the same data contract you maintain alongside your data product, instead of describing your schema a second time in a Portal-specific format.

When you ingest a contract, Portal focuses on the `schema` section of the contract.
The `schema` section describes one or more objects (typically tables), each with a list of properties (columns) that may be nested.
The relevant part of an ODCS contract looks as follows:

```yaml
apiVersion: v3.1.0
kind: DataContract
id: clinical-trial-dashboard
name: Clinical Trial Dashboard
version: "1.0.0"

schema:
  - name: trial_master
    logicalType: object
    physicalType: table
    physicalName: "clinical-trial-dashboard.trial_master"
    description: "Main table of clinical trial performance metrics"
    properties:
      - name: trial_id
        businessName: "Trial Identifier"
        logicalType: string
        physicalType: varchar
        description: "Unique identifier for the clinical trial"
        primaryKey: true
        primaryKeyPosition: 1
        required: true
        examples:
          - "CT-12345"
          - "AX-45678"
      - name: enrollment_count
        businessName: "Enrollment Count"
        logicalType: number
        physicalType: integer
        description: "Number of enrolled patients"
        examples:
          - 100
          - 2000
```

## Visualizing schema information

Portal shows the ingested schema on the output port page, listing each object together with its properties, their types, descriptions and examples.
This gives consumers a quick understanding of the structure of the data an output port exposes, including which fields are primary keys, required or used for partitioning.

## Ingesting schema data

Obtain or create the BitOL ODCS data contract that describes your output port.
A complete example contract is available [here](https://github.com/conveyordata/data-product-portal/blob/main/integrations/bitol/data-contract-example.yml)

Portal accepts the full ODCS document, so you can post the contract as-is; only its `schema` section is used.
Each ingestion replaces the previously stored schema for that output port, so posting an updated contract keeps the displayed schema in sync with your data.

### API endpoint

- [`POST /api/v2/data_products/{data_product_id}/output_ports/{output_port_id}/data_contract`](/docs/api/#tag/Output-Ports-Contract/operation/ingest_output_port_contract)
- [`GET /api/v2/data_products/{data_product_id}/output_ports/{output_port_id}/data_contract`](/docs/api/#tag/Output-Ports-Contract/operation/get_output_port_schema)
