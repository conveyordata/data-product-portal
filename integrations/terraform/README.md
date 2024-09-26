# Integrating the data product portal with AWS

## Configuring the terraform setup

### AWS permissions
To be able to run terraform code, you first need to assume the correct AWS role before you can run terraform apply. There
are many different ways on how to do that, but the most straightforward way is to configure your AWS profile in your
~/.aws/config file and assume the role in that configuration as follows:
```bash
export AWS_PROFILE <profile-name>
```
You can validate whether the correct AWS role is assumed by running the following command:
```bash
aws sts get-caller-identity
```
This role should preferable have admin permissions to run the terraform code base as described below.

### Terraform state
When working with terraform the first thing you need to do is set up your terraform state. The terraform state is
configured in the [state.tf](./envs/portal/state.tf) file. There are many ways to setup the terraform state, but for
AWS the most common way is to store the terraform state in an S3 bucket your admin role has permissions to. In following
[article](https://developer.hashicorp.com/terraform/language/settings/backends/s3) you can find a description on how to
do that and I recommend to update the state file accordingly.

### Module overview
The terraform code base consists of 4 modules and depending on your setup, some modules are optional:
- **account:** This contains AWS account level configuration and is mostly related to route53 and DNS related stuff that
is required if you want run services like datahub or portal inside your AWS account ontop of a kubernetes cluster.
- **networking:** This module will set up a VPC with 2 groups of subnets (routable and non-routable subnets) that can act
as a good default networking configuration. Routable subnets are usually part of the CIDR IP plan of your organisation
and are usually restricted in the amount of IP addresses that are available to you. Non-routable subnets are there for
running your workloads and have a secondary CIDR with a /16 range giving you all the IP addresses you might ever need.
- **infrastructure:** The infrastructure module will set up a bastion host and optionally an EKS cluster where you can
install relevant services for your data platform: ie. datahub as a data catalog or the data product portal. This module
is optional.
- **environment:** This module will introduce the data environment concept and will create S3 buckets, glue databases
and other resources that are considered environment specific. Each environment will have an identical setup and will be
prefixed accordingly.
- **data_products:** This module will generate the dedicated IAM roles and permissions per data environment and will
do that based on the configuration in the [config](./envs/portal/config) folder. In a next step you will replace these
config files by retrieving this information directly from the portal API's. More on that later. These IAM roles will
grant you permissions to specific paths in your datalake buckets, glue databases/tables and grant you access to the glue
metastore and Athena services. We intend to add support for AWS Redshift serverless in a later release.

Only the **environment** and **data_product** modules are mandatory for a simple setup, the other ones can be considered
as convenience if you don't have a proper core VPC setup already in your AWS account. By commenting out the modules you
don't need in the [modules.tf](./envs/portal/modules.tf) file, you can select the models you truly need. It might mean
that you have to make some adaptions to the code by defining some terraform locals and extract information directly from
the AWS console if there is a need for it.

### Configuration
The [configuration file](./envs/portal/config.tf) contains the parts where you as a data platform admin can change
configuration for. There is a description for most of the parts that are configurable. I leave it to the reader to delve
a bit deeper in the terraform code in what those different configuration options mean.

## Retrieving the configuration files from the data product portal
You can configure the data product portal with an API key that you can choose yourselves. If you install the portal via
a [HELM chart](../../helm/values.yaml) you can set this API key directly via the api_key configuration option. With that
API key you can directly interact with the data product portal to retrieve information from it directly via API calls.

We also included a sample [python script](./envs/portal/read_portal_config.py) that will retrieve the portal configuration
and convert it to the same config representation that you can find in the [config folder](./envs/portal/config)

## Automatically updating the terraform configuration with the retrieved configuration files
For now the data product portal does not support automatically updating the terraform configuration if the configuration
has changed, so the easiest would be to run the python script and update the configuration files manually or on a schedule
(daily, hourly,...). We intend to add this functionality in a later release as part of the core data platform portal
release.
