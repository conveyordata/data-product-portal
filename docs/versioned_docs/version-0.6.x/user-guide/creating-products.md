---
sidebar_position: 2
title: Creating Data Products
---

# Creating your first data Product

In this guide we will walk you through the creation flow of your product as well as connecting it with other Products
and describing the data that it will produce.
If you do not know what a Data Product is, take a look at the page describing [Data Products](../concepts/data-products.md).

## How to Create a Data Product

1. **Log in to the Portal**: First, make sure you have the necessary permissions to create a data product. If you’re unsure, ask your admin for access.
2. **Navigate to the 'Data Products' Page**: In the portal’s navigation, click on **Create Data Product**.
3. **Fill in the Details**: You’ll be asked to enter:
   - **Product Name**
   - **Namespace**: This generated field must be unique within your portal installation. It can not be changed after creation.
   - **Description**
   - **Product Owner** (typically your email address)
   - **Metadata**: Select the correct type, domain and status for your new data product.
4. **Submit the Product**: Once you’ve completed the form, click **Create**.

![Creating a Data Product](./img/create-data-product.png)

### The Detail page

If the **Data Product** is created successfully, you will navigate automatically to the detail page.

We strongly encourage you to write a proper *About* page as this is the first encounter users will have with your **Data Product**.
Interesting things to include here are SLA's, contract specifications and an overview of the data one can expect.

On this page you can find all of the information regarding your **Data Product**. This includes the current team, status, domain and type.

You can also interact with the various enabled **tools and integrations**.

![Detailed Data Product](./img/data-product-detail.png)

## Creating a technical asset

Now that you have your data product, it is time to describe the technical assets that your data product produces.
More information about technical assets can be found on the following [concept page](../concepts/technical-assets.md).

Technical assets are linked to and owned by a single **Data Product**.

## How to add a technical asset to a Data Product

1. **Go to the Data Product that will expose the technical assets**.
2. **Go to the Output Ports Tab**.
3. **Click 'Add a technical Asset'**: You will need to have the correct access rights on the **Data Product** to be able to do this action.
4. **Specify Metadata**: Include necessary metadata such as:
   - **Name**
   - **Description**
   - **Technical Mapping** Choose between *Default* and *Custom* (see [Technical mapping](#technical-mapping) below).
   - **Technology** Choose from one of the enabled technologies within your organization.
   - **Technology specific information** Add some technical information such as database name and schema, prefix paths, ... This depends on the chosen technology.
5. **Save Your Data Output**: Click **Create** to add the data output to your product.

![Data Output Creation](./img/technical-asset-modal.png)

### Technical mapping

*Default* is the **recommended option for most users**. Default mapping uses the platform's standard provisioning conventions, automatically generating technical identifiers (paths, table names, schemas, etc.) based on your Data Product's namespace and configuration. More information can be found in [Technical assets - Technical mapping](../concepts/technical-assets.md#%EF%B8%8F-technical-mapping)

## Creating an output port for your product

The output port describes which technical assets your data product exposes through a common interface.
It is the missing link when you want to share the data-product's data with other data products.
For more information about output ports, take a look at the concept page describing [Output Ports](../concepts/output-ports.md).

### How to Create an output port

1. **Navigate to the Output Ports Section**.
2. **Click 'Add Output Port'**.
3. **Specify Metadata**: Include necessary metadata such as:
   - **Name**
   - **Owners**
   - **Domain**
   - **Status**: Identifying the lifecycle stage of this output port.
   - **Access Type**: Identifying who can see and request access to this Output Port (see [Access Types](#access-types) below).
   - **Description**
4. **Submit**: Once your Output Port is configured, click **Create Output Port**.

### Access Types

There are currently 3 possible access types.

- Public: All access requests are immediately approved. Any Data Product can use your dataset as input.
- Restricted: Access requests are delivered to the dataset owners. These owners are in control over which Data Products can use the data downstream.
- Private: Private datasets don't show up in the overview. It is only possible to link to a private dataset if you are an owner of both the Dataset and the requesting Data Product.

![Creating an output port](./img/output-port-modal.png)

## Adding the Technical Assets to your Output Port

Now that you have created both Technical Assets and an Output Port, it is time to link them together.

1. **Go to the Data Product that will expose your data**.
2. **Go to the Output Ports Tab**.
3. **Link the Technical Assets to your Output Port**.
   You can drag the Technical Assets from the right side to the Output Port on the left side or use the 'Link Technical Asset' link.

![Linking technical assets to an output port](./img/linking-assets-to-output-ports.png)

## (Optional) Creating an Input Port for your Product

If your data product needs to consume data from other data products, you will need to create an Input Port.
For more information about input ports, take a look at the concept page describing [Input Ports](../concepts/input-ports.md).

### How to Create an Input Port

1. **Navigate to the Data Product that will consume data**.
2. **Go to the Input Ports Section**.
3. **Click the 'Link Output Port' button**.
4. **Request access to the Output Ports that you need**.
   You can only use them after your request has been approved by the owners of the Output Port.

![Linking an Output port to an Input port](./img/linking-output-input-port.png)

## Conclusion

Congratulations :tada:! you succeeded in creating your first Data Product and made it discoverable and consumable through:

- Writing a clear description and an about page
- Identifying the Technical assets that will be produced
- Providing at least one interface that other Data Products can use to consume the data
- Optionally, consuming data from other Data Products through Input Ports

Well done!
