---
sidebar_position: 1
title: Getting Started
---

# Getting Started with the Data Product Portal

---

## Introduction

Welcome to the **Data Product Portal**! In this guide, we'll walk you through the process of using the portal to build, manage, and share data products. Whether you're a data product owner or a member of a data team, this guide will help you get started quickly.

:::info

This section of the documentation is aimed at **end users**. If you are interested in how to get the Data Product Portal up and running, please visit the [Quickstart](../getting-started/quickstart) page instead.

:::

---

## Step 1: Create a Data Product

### What is a Data Product?

A **Data Product** is a scoped data initiative with a clear objective, driven by a data product owner. It includes data outputs and datasets, and it follows governance processes to ensure compliance with your organization's standards. For more information have a look at the [Data Product](../concepts/data-products) concept.

### How to Create a Data Product

1. **Log in to the Portal**: First, make sure you have the necessary permissions to create a data product. If you’re unsure, ask your admin for access.
2. **Navigate to the 'Data Products' Page**: In the portal’s navigation, click on **Create Data Product**.
3. **Fill in the Details**: You’ll be asked to enter:
   - **Product Name**
   - **Namespace** This generated field must be unique within your portal installation. It can not be changed after creation.
   - **Description**
   - **Product Owner** (typically your email address)
   - **Metadata** Select the correct type, domain and status for your new data product.
4. **Submit the Product**: Once you’ve completed the form, click **Create**.

If the **Data Product** is created successfully you will navigate automatically to the detailed page.
Here you can change the *About* page, add **Data Outputs** and link **Datasets**.
From here you can also access some of the configured **tools**.

---

## Step 2: Add Data Outputs to Your Data Product

### What is a Data Output?

A **Data Output** is a technical endpoint, such as an S3 bucket, a database table, or an API endpoint, where data is stored, shared, or accessed. Data outputs are created and managed within the context of a data product.

### How to Add Data Outputs

1. **Go to the Data Outputs Section**: Once your data product is created, navigate to the **Data Outputs** tab within the product’s page.
2. **Click 'Add Data Output'**: Select the type of output (e.g., S3 bucket, table, or API) and configure it.
3. **Specify Metadata**: Include necessary metadata such as:
   - **Output Name**
   - **Format** (e.g., CSV, JSON)
   - **Access Controls**: Specify who can read/write to the data output.
4. **Save Your Data Output**: Click **Save** to add the data output to your product.

**Diagram**: A simple diagram showing the relationship between data products and data outputs, with examples like S3 buckets or SQL tables.

---

## Step 3: Bundle Data Outputs into Datasets

### What is a Dataset?

A **Dataset** is a collection of data outputs grouped together for sharing or use by other products. Datasets grant **read access** to the data outputs they contain. These are governed and approved by dataset owners to ensure proper access control.

### How to Create a Dataset

1. **Navigate to the Datasets Section**: Go to the **Datasets** tab within your data product.
2. **Click 'Create Dataset'**: Provide a name for the dataset and select the data outputs you wish to bundle together.
3. **Set Access Controls**: Define who can access the dataset and the level of access (read-only, etc.).
4. **Submit**: Once your dataset is configured, click **Create Dataset**.

**Diagram**: Show a diagram that links data outputs to datasets, explaining the access control model.

---

## Step 4: Request Access to Datasets and Data Outputs

### How Does Access Work?

In a governed environment, access to datasets and data outputs must be requested and approved. This ensures that data is used responsibly and in the right context.

### Requesting Access

1. **Request Access**: If you need access to a dataset or data output owned by someone else, navigate to the **Access Requests** section of the portal.
2. **Fill in the Details**: Select the dataset/data output you want to access, and specify your purpose (e.g., project or task).
3. **Submit the Request**: Your request will be sent to the dataset owner for approval.
4. **Approval**: Once the owner approves the request, you’ll receive access to the resource.

**Diagram**: Include a flowchart showing how access requests are made and approved.

---

## Step 5: Create and Manage New Data Products Using Datasets

### Using Datasets in New Data Products

Once you have datasets available, you can use them as **inputs** for creating new data products. This allows you to build on top of existing data and extend its usage within your organization.

### How to Use Datasets in New Products

1. **Start a New Data Product**: Navigate to the **Create Data Product** page.
2. **Select Input Datasets**: Choose the datasets that will serve as the foundation for your new product.
3. **Define Data Outputs**: Specify the data outputs for the new product, using the datasets as input.
4. **Approve Access**: Ensure all relevant users have access to the new product’s outputs, following the same access approval workflow as before.

---

## Conclusion

Congratulations! You’ve now completed the key steps for creating, managing, and sharing data products within the portal. From here, you can continue expanding your data ecosystem, using datasets and data outputs to build scalable, governed data products.

If you need help along the way, refer to the portal’s **Documentation** section for more in-depth guides on each part of the process, or reach out to your organization’s admin for assistance.

---

### Diagrams/Images to Include:

1. **Creating a Data Product**: Flow diagram showing the steps and the role of the data product owner.
2. **Data Outputs in a Data Product**: Diagram that shows how data outputs are added to a data product and their technical endpoints.
3. **Datasets and Access Control**: Visual of how datasets group data outputs and provide controlled access.
4. **Request and Approval Process**: Flowchart for how access requests are made and approved.
5. **Using Datasets for New Data Products**: Diagram showing how datasets are used as input for creating new data products.

---
