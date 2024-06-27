<!-- PROJECT INFO -->
<br />
<div align="center">
<h1 align="center">Data Product Portal Installation Guide</h1>
  <p align="center">
    INSERT SHORT DESCRIPTION HERE
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#quick-start">Quick Start</a>
      <ul>
        <li><a href="#limited-functionality">Limited Functionality</a></li>
      </ul>
    </li>
    <li>
      <a href="#production-installation">Production Installation</a>
      <ul>
        <li><a href="#helm-chart">Helm Chart</a>
          <ul>
            <li><a href="#database">Database</a></li>
            <li><a href="#ingress">Ingress</a></li>
            <li><a href="#service-account">Service account</a></li>
            <li><a href="#oidc">OIDC</a></li>
            <li><a href="#conveyor">Conveyor</a></li>
            <li><a href="#cli">CLI</a></li>
          </ul>
        </li>
    </li>
    <li><a href="#local-developer-set-up">Local Developer Set-up</a></li>
  </ol>
</details>

## Quick-start
To have the portal quickly up and running with limited amount of features, we propose to use `Docker compose`. You can find the installation instructions [here](https://docs.docker.com/compose/install/).

To start up the portal, just run `docker compose up` inside of the root folder.
All of the services will start up in their own container.
This process makes use of the pre-made `.env.docker` configuration file. Feel free to adjust this to your own needs. For example, if you want to customize the Postgresql database that we connect to.

**Warning** The docker script will drop and recreate the postgresql database at startup, do not link it to any live production database systems.

### Limited functionality
The docker compose version of the portal serves as a quick-start tool to allow you to get up and running fast.
However, because of the limited setup, most of the integration features are disabled.
By default, none of the integrations will work. If you want to test these out you need to make sure the correct dependencies are installed and provide them in the configuration file. The functionality of the docker compose version focuses mainly on getting a feel for the portal and it's uses and explaining the concepts behind purpose-based access control.


See below for detailed instructions on how to do a production installation.

## Production installation
Portal provides 2 separate services that can be installed together for a full production installation.
We provide a backend and a frontend service, they are available as Docker images.
Easiest way of productionizing this is by including them in a working Kubernetes setup, we have provided a Helm chart for easy installation.

### Helm chart
A publicly accessible Helm chart is available [here](`public.ecr.aws/conveyordata/data-product-portal`)
Change the `values.yaml` file to your needs to be able to access all of the pods.
By default, the backend and frontend images are using the correct version for the helm chart. We do not recommend overwriting these values.
Below you find a set of configurations that should be adjusted

#### Database
Either change the values.yaml so that you use your own database credentials. Preferred way is to set up an external RDS (or similar service) database outside of the cluster. Another option is to use the provided postgresql dependency to set up a postgres pod alongside the backend and frontend services.

#### Ingress
Ingress is created by default, but will require the correct annotations to function with e.g. AWS Load balancers.

#### Service account
A service account is created by default. This needs to be linked with IRSA to an AWS service account if you want to enable the AWS integration.

#### OIDC
To enable OIDC you will need to provide the OIDC credentials to the values.yaml
A working Cognito user pool setup is required.

#### Conveyor
To have a working Conveyor integration you will need to pass the conveyor api key and secret of your tenant's CI/CD user to the values.yaml.

#### CLI
The executable for the Portal CLI can be found here. Installation instructions can be found on the same page.

## Local Developer set-up
For local developer set-up we refer to the READMEs of the corresponding folders.
