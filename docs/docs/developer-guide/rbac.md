---
sidebar_position: 4
title: Role-Based Access Control
description: Understanding and configuring RBAC in the Data Product Portal
---

# Role-Based Access Control (RBAC)

The Data Product Portal uses a flexible Role-Based Access Control (RBAC) system to manage permissions across the platform. This system allows fine-grained control over who can perform specific actions at different levels of the organization.

## Core Concepts

The RBAC system is built on four key concepts: **Scopes**, **Actions**, **Roles**, and **Assignments**.

### Scopes

Scopes define the context or level at which permissions are applied. The portal supports four scopes:

- **Global**: Platform-wide permissions that apply across the entire portal (e.g., creating data products, managing users)
- **Data Product**: Permissions specific to a single data product (e.g., updating properties, managing team members)
- **Output Port**: Permissions for individual output ports (e.g., approving access requests, managing links)
- **Domain**: Permissions at the domain level for organizational grouping. (*this scope is not yet in use, but the ground works have been provided for future improvements*)
### Actions

Actions represent specific operations that can be performed in the portal. Each action is tied to both API endpoints and UI features. Your ability to perform an action depends on the roles assigned to you in the relevant scope.

Examples of actions include:

**Global Actions:**
- `GLOBAL__CREATE_DATAPRODUCT` - Create new data products
- `GLOBAL__CREATE_OUTPUT_PORT` - Create new output ports
- `GLOBAL__UPDATE_CONFIGURATION` - Modify platform configuration
- `GLOBAL__CREATE_USER` - Add users to the platform

**Data Product Actions:**
- `DATA_PRODUCT__UPDATE_PROPERTIES` - Modify data product metadata
- `DATA_PRODUCT__UPDATE_SETTINGS` - Change data product settings
- `DATA_PRODUCT__CREATE_USER` - Add team members
- `DATA_PRODUCT__APPROVE_USER_REQUEST` - Accept membership requests
- `DATA_PRODUCT__CREATE_TECHNICAL_ASSET` - Add technical assets

**Output port Actions:**
- `OUTPUT_PORT__UPDATE_PROPERTIES` - Modify output port metadata
- `OUTPUT_PORT__APPROVE_USER_REQUEST` - Accept access requests
- `OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST` - Approve data product links
- `OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS` - Remove data product access

:::note
Actions are defined in the backend codebase and can be extended by the development team. If you need additional actions for your use case, feel free to submit a pull request.
:::

### Roles

Roles are collections of actions grouped together for a specific purpose. The portal supports both predefined and custom roles.

**Predefined Roles (Prototypes):**
- **Owner**: Full control over resources within their scope
- **Everyone**: Default permissions available to all users
- **Custom**: Roles created specifically for your organization's needs

Roles can be created and customized for each scope. When creating a custom role:
1. Choose the scope (Global, Data Product, Domain, or Output Port)
2. Assign a descriptive name
3. Select the actions this role should be allowed to perform

### Role Assignments

Role assignments link users to roles within a specific scope:
- **Global roles** are assigned through the People page and apply platform-wide
- **Data Product roles** are assigned when adding team members to a data product
- **Output Port roles** are assigned when granting access to output ports
- Users can have different roles in different scopes simultaneously
- Each user can have only **one global role** at a time (excluding temporary admin privileges)

## Accessing RBAC Settings

### Gaining Admin Rights

To access and configure RBAC settings, you need temporary admin privileges:

1. **Verify Admin Eligibility**: Your user account must have the `can_become_admin` flag set to `true` in the database
   - If you don't have database access, contact an existing administrator
   - Administrators can grant this permission through the People page

2. **Activate Temporary Admin Privileges**:
   - Click your user menu in the top-right corner of the portal
   - Select **"Gain temporary admin privileges"**
   - Admin privileges are granted for 10 minutes
   - An admin badge will appear while active

3. **Access RBAC Settings**:
   - Once admin privileges are active, a **Settings** option appears in the navigation
   - Navigate to **Settings** → **Roles**
   - Here you can view and manage roles for all scopes

4. **Revoke Admin Privileges**:
   - Click your user menu
   - Select **"Remove admin privileges"**
   - Admin privileges automatically expire after 10 minutes if not manually revoked

:::important
Temporary admin privileges provide full access across the platform. All actions performed while in admin mode are still audited under your user account. Use admin privileges judiciously and revoke them when finished.
:::

:::warning
At least one user must have the `can_become_admin` permission enabled.
The system prevents removing this permission from the last eligible user.
:::

You can see what the RBAC settings page looks like below:
![An overview of the RBAC settings for the Data Product scope](./img/rbac.png)

## Managing Roles

### Creating Custom Roles

1. Navigate to **Settings** → **Roles** (This requires admin privileges)
2. Select the scope for which you want to create a role
3. Click **"Create Role"**
4. Provide:
   - **Role Name**: A descriptive name for the role
   - **Description**: A longer description that explains the context for the role
5. Click **Create**
6. Assign actions:
   - **Actions**: Select all actions this role should be permitted to perform by ticking the checkboxes

### Modifying Existing Roles

1. Navigate to **Settings** → **Roles**
2. Find the role you want to modify
3. Update the name (via modify) or adjust the permitted actions. Action changes are saved automatically
4. Save your changes

:::caution
Modifying a role affects all users currently assigned that role. Changes take effect immediately.
:::

## Assigning Roles to Users

### Global Role Assignment

Global roles must be assigned by administrators through the People page:

1. Navigate to **People** (requires admin privileges)
2. Find the user you want to assign a role to
3. Select the desired role from the dropdown in the **Role** column
4. The assignment takes effect immediately

Users can also be granted the ability to elevate to temporary admin by checking the **"Can become admin"** checkbox.

### Data Product Role Assignment

Data product team members are assigned roles when added to the product:

1. Navigate to the data product's detail page
2. Go to the **Team** tab
3. Click **"Add Team Member"**
4. Select the user and assign them a role (e.g., Owner, Viewer, Custom Role)
5. Users can also **request to join** a data product, specifying their desired role
6. Existing team members with appropriate permissions can approve these requests

### Output Port Role Assignment

Output port access is managed separately from data product membership:

1. Navigate to the output port detail page
2. Manage access through the **Access** tab
3. Grant permissions based on configured roles
4. Access can be requested by data product owners and approved by output port owners

## Use Cases

### Platform Administrator

A platform administrator needs to configure the entire portal:

1. Ensure their user has `can_become_admin` set to true
2. Gain temporary admin privileges through the user menu
3. Access **Settings** to configure platform-wide options
4. Manage global roles through the **People** page
5. Revoke admin privileges when finished

### Data Product Owner

As a data product owner, you have full control over your product:

1. By default, owners can:
   - Update data product properties and settings
   - Add and remove team members
   - Create and manage output ports
   - Approve access requests from other data products
2. These permissions are defined by the `OWNER` prototype role for the Data Product scope

### Custom Role Example: Data Steward

Create a Data Steward role with limited permissions:

1. Gain admin access
2. Navigate to **Settings** → **Roles**
3. Select **Data Product** scope
4. Create a new custom role named "Data Steward"
5. Assign actions:
   - `DATA_PRODUCT__UPDATE_PROPERTIES`
   - `DATA_PRODUCT__APPROVE_USER_REQUEST`
   - (Exclude deletion and settings changes)
6. Assign this role to appropriate users on relevant data products

## API Integration

The RBAC system is fully integrated with the portal's REST API. All endpoints enforce authorization checks based on the authenticated user's roles and permissions.

When making API calls:
- Include your access token in the `Authorization` header
- The backend validates your permissions for each action
- Unauthorized requests return `403 Forbidden`
- Actions performed via API are subject to the same RBAC rules as the UI

For more information on authentication, see the [Authentication Guide](./authentication.md).

## Best Practices

1. **Principle of Least Privilege**: Grant users only the permissions they need to perform their work
2. **Regular Audits**: Periodically review role assignments to ensure they remain appropriate
3. **Use Custom Roles**: Create custom roles that match your organization's specific workflows
4. **Minimize Admin Time**: Use temporary admin privileges only when needed and revoke them promptly
5. **Document Custom Roles**: Maintain documentation of any custom roles created and their intended purpose
6. **Test Permission Changes**: Before assigning new roles broadly, test them with a limited user group
