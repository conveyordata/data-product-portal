# Lightweight data products technical design

## Context and Problem Statement
We have decided to create a lightweight version of a data product meant for experimentation purposes and to fix
personal access.
The idea is to not have people create a heavy data product, and to make it easy for us to differentiate.
For example for a full data product we will want to ensure people share their data, have data quality checks, data
contracts etc...
A lightweight data product won't be able to share data, but is used for:
- experimentation
- personal access
- answering business questions

For the experimentation case we want to be able to upgrade these lightweight data products to full data products.

## Decision Drivers

* Be able to upgrade to full data products
* Clearly differentiate from full data products

## Considered Options

* **Endpoints Option 1: Reusing the data products endpoints**: Reusing the data product endpoints, allows us to reuse the logic and even show them in a single table.
* **Endpoints Option 2: Make new endpoints**: Creating new endpoints but we can still use sql alchemy inheritance to reuse the logic.
* **Database Option 1: Joined table inheritance**: Base class has a table, and subclasses have a table that joins the base table.
* **Database Option 2: Single table inheritance**: Base class and subclasses share a single table.
* **Database Option 3: Concrete table inheritance**: Each subclass has its own table.

## Decision Outcome

**Chosen option:** *Endpoints Option 2: Make new endpoints*. A lot of logic can be reused via inheritance, and having seperate endpoints makes the logic easier to understand.
**Chosen option:** *Database Option 1: Joined table inheritance*. Allows us to easily query the base table, and keeps the base table clean.

### Confirmation

We will create new endpoints for lightweight data products, and use inheritance on the service and sql alchemy models to reuse certain logic.

## Pros and Cons of the Options

### Endpoints Option 1: Reusing the data products endpoints

For this options we will create a base abstract class in sql alchemy and have 2 different types inheriting from it.
Our service will be able to reuse the logic, but also has to be able to differentiate between the two types.

* **Good, because** we don't need to create a new endpoint
* **Good, because** we can reuse some logic
* **Bad, because** some endpoints do not make sense for lightweight data products, like all output port or technical asset endpoints
* **Bad, because** logical differences make things more complex
* **Bad, because** UI might render a page for a lightweight data product, fetch the data product and notice it's a full data product and need to redirect for the user. Might be weird, but more of an edge case hopefully.

### Endpoints Option 2: Make new endpoints

For this options we will create a base abstract class in sql alchemy and have 2 different types inheriting from it.
That way we can even have a base abstract service to extract common logic.

* **Good, because** clear split between full and lightweight data products
* **Good, because** you can upgrade it to a full data product, and keep your light weight data product in the mean time until the upgrade is done. For example if you have to wait for access requests to be approved.
* **Good, because** the UI knows which kind of data product we are showing just from which URL it's fetching
* **Neutral, because** we can still make an endpoint to show all lightweight and normal data products together
* **Bad, because** we need to create a whole new endpoint for this, and reimplement some of the logic. This can be partially offset with inheritance
* **Bad, because** migrating to a full data product might be more complex

### Database Option 1: Joined table inheritance

* **Good, because** You can query the base table making showing the base table easy and fast
* **Good, because** The specialised tables are not overloaded with columns of other types
* **Bad, because** when looking at the database you need to look at 2 tables to see the data of a data product
* **Bad, because** Upgrading is possible by switching the type and filling in some fields

### Database Option 2: Single table inheritance

* **Good, because** You can query the base table making showing the base table easy and fast
* **Good, because** Looking at the single table is easy
* * **Good, because** upgrading is just switching the type and filling in some fields, a lot of things can be untouched. However it might make more sense to make a copy for an upgrade.
* **Bad, because** can't use non-null requirements
* **Bad, because** the single table can be very bloated and big

### Database Option 3: Concrete table inheritance

* **Good, because** you can easily see all columns of a data product in the single table
* **Bad, because** heavily discouraged if we need to show the base class data anywhere, because this is solved via unions.
* **Bad, because** heavily discouraged by sql alchemy
* **Bad, because** Upgrading requires use to create a new line in the other table, and delete the old. Meaning a copy is needed or a lot of magic to keep referential integrity.
