# API v2

We are currently working on a new API design
(see [adr 0008](https://github.com/conveyordata/data-product-portal/blob/main/docs/adr/0008-api-redesign.md)).

This means we are deprecating the old API, and making a new V2 one available. Later we will migrate our Front end to use
the V2 API, and afterwards the old API will be removed.

Currently we encourage the use of this new V2 API, and please report any issues you encounter. The old API will still
be supported for a while. But new functionality might only be available in the V2 API.

We currently do not have a timeline yet, but we will communicate when the V2 API is fully available and when we start
the front end migration.
After the front end migration we will make a new announcement. The next minor release after the front end migration will
remove the old API.
