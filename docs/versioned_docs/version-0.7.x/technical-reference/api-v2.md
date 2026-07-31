# API v2

We are currently working on a new API design
(see [adr 0008](https://github.com/conveyordata/data-product-portal/blob/main/docs/adr/0008-api-redesign.md)).


The new V2 api has the following advantages:
- Renamed the endpoint to match our new naming scheme that was already applied in the frontend, this reduces confusion
- Smaller return objects result in faster responses

This means we are deprecating the old API, and making a new V2 one available.
We have migrated the front end to use the new V2 API, meaning it has been tested and is ready.

In the 0.5.0 release both API's will still be supported, but we only added new functionality to the V2 API.

In the 0.6.0 release we will remove the old API.
