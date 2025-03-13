# Casbin model

## Policy design explained

The design supports four levels of access:

1) Everyone: This is a special role definition with identifier '*'.
   If a permission is granted to this role, these actions are considered available to all users, and will be allowed.
2) Resource: A user receives a role within the scope of a resource (e.g. a data_product, dataset).
   Access will be granted if the role specifies the requested action.
3) Domain: A user receives a role within the scope of a domain.
   Access will be granted to all resources under this domain if the role specifies the requested action.
4) Admin: The engine checks if the user has been registered as admin.
   If true, no action check is performed and access is granted directly.
   This avoids having to specify all actions for an admin, removing room for error.

## Example

We describe an example policy here that illustrates how the model can be used.
You can test this yourself by copying the policy and requests to the [casbin editor](https://casbin.org/editor).

### Policy

The `p` lines define policies (meaning a single rule to evaluate).
The `g`, `g2` and `g3` lines define different role assignments.

```
p, role1, read
p, role1, write
p, role1, update
p, role2, read
p, role2, delete
p, *, dance -- policy for everyone

g, alice, role1, dataset1 -- resource role assignment
g, bob, role1, dataset2 -- resource role assignment
g2, alice, role1, domain1 -- domain role assignment
g2, bob, role2, domain1 -- domain role assignment
g3, carol, * -- admin assignment
```

### Requests

Some example requests with their outputs.

```
alice, domain1, dataset1, read -- true, role1 can read dataset1
alice, domain1, dataset1, delete -- false, role1 cannot delete dataset1
bob, domain1, dataset1, delete -- true, role2 can delete in domain1
carol, foo, bar, baz -- true, carol is admin
john, foo, bar, dance -- true, everyone is allowed to dance
john, domain1, dataset1, read -- false, john has no role assigned
```
