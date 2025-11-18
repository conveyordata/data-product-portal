# Admin privilege should be toggleable

## Context and Problem Statement
Currently the admin role is granted permanently to users. This means that they always have blanket permissions.
Any action they take within the frontend or API will be allowed. This can be a source of confusion because you can e.g. take actions on products where you are not part of the team, ... and you also don't get the 'normal user' experience as an admin dev.

To solve this we should allow for the admin privilege to be acquired for a period of time.

## Decision Drivers

* Impact on current RBAC implementation
* Impact on customer integration
* Ease of use for customers
* Auditability.

## Considered Options

* **Option 1: Within Portal**
Elevated privileges need to be enabled prior to using them. By default everyone logs in with a regular (= not superuser) role. Users with the correct rights can elevate themselves temporarily towards a superuser role.
- Add an admin flag to the event to show that admin privileges were used.
- Add a toggle API call that adds the user to the global role assignment.
- Add a timestamp how long it is valid and at each RBAC check we can see if it is still valid and remove it otherwise.

* **Option 2: Outside Portal**
We can advise companies to reserve a special user for this or to provide a non-admin and admin user for the same person. In case they need superuser access to fix something in portal, they use this separate account to login to portal, apply the changes and log back out.

## Decision Outcome

**Chosen option:** *Option 1: Within portal*. Lack of auditability and shared users are too much of a disadvantage compared to the required rework of RBAC.

### Confirmation
Description how this will be reflected in the appliction.

Users will log in with normal access rights as any other user. They might have the right to elevate towards admin rights.
This is done for a temporary amount of time (5 minutes?)
While they are admin they are still audited as the same user. Perhaps it should be stored that they had admin privileges at the time.
The admin role will be granted temporarily to the user.
RBAC changes are therefor minimal.

## Pros and Cons of the Options

### Option 1: Within Portal

* **Good, because** role management stays within portal, no dependency on other system.
* **Good, because** no impact on customer integration.
* **Good, because** auditability of admin role stays intact.
* **Bad, because** requires rework of global role RBAC system.

### Option 2: Outside Portal

* **Good, because** RBAC requires almost no changes.
* **Bad, because** organisations need to track admin audits.
* **Bad, because** same person would need multiple users to differentiate, changing experience requires log out and relogin.
