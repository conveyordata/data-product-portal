SELECT
    shipment_id,
    order_ref,
    shipped_date,
    delivery_status
FROM
    {{ source('sources', 'wms_shipments') }}
