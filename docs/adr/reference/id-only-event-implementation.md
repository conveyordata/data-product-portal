# ADR Title

# ID event only implementation:

ID-Only Events: The system will emit IDs when changes occur to a data product, output port, or exploration. To get started,
we will only support a data product loop and exploration loop.

Reconciliation Loop: Any change (e.g., input/output ports, technical assets) will trigger the reconciliation loop.
The system will then use an SDK to fetch the latest data.

We will only implement 2 loops to get started:
- Data Product Loop
- Exploration Loop

# Advantages:

Better Exception Handling: If the system goes down, it can easily recover by booting up,
listing the products/explorations, and running the reconciliation loop. We will bake that in the provisioner SDK.

Simpler Bug Fixes: Fixing a bug just requires restarting the provisioner with the bug fixed code, this will trigger all
data product and exploration loops.

Event Collapsing: Multiple events for the same data product can be combined using a
slight delay to avoid over-triggering the loop.

# Deployment & Limitations:

A simple implementation can be achieved by running terraform apply fetching data from portal using the SDK.

A downside to this simple approach is that it doesn't automatically handle complex
migrations (like moving an S3 bucket location). As a user you should set prevent_destroy on terraform resources to
prevent issues.

## Handling migrations

We can rather easily handle migrations, for example when we want to manage something through the privisioner we can:
- automate a tf state removal
- start managing the resource
- pass variables to terraform

## s3 migration case

The s3 migration case from the [use case aws s3 provisioner](./use-case-aws-s3-provisioner.md) can be handled in a couple of ways:
- We can store the result of the s3 path in ssm under our exploration or data product name
- We can check all domains for if the s3 path does not exist to see if we should migrate

So all in all this is manageable


# Soft delete required

We also need to implement some soft delete mechanism. When people use terraform apply this might not be needed
necessarily, but in all other cases we do need it. However even for the terraform apply case you might want to be cautious
and verify if a data product or exploration is in a deletion scenario.

For now we only need to support soft delete on Data Product and Exploration. We can implement this similar to k8s
where we have a list of finalizers (delete blockers), we can use a pending deletion status to ensure we block deletion
until all finalizers are removed.
