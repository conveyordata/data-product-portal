# Slow queries with SQL Alchemy and how to solve them

## Context and Problem Statement

In the past we have had many issues with SQL Alchemy loading too much data from the database resulting in too many queries.

## Decision Drivers

* Slow calls to fetch a single data product or output port through the API
* Hidden objects being fetched without the developer knowing
* ...

## Considered Options


* **Option 1: Write SQL ALchemy best practices guide**
* **Option 2: Encode SQL Alchemy best practices**
* **Option 3: Migrate to another ORM**
* ...

## Decision Outcome

**Chosen option:** *Option 2: Encode SQL Alchemy best practices*. We will also implement option 2 to write down the reasoning.
.

## Pros and Cons of the Options

### Option 1: Write SQL ALchemy best practices guid

* **Good, because** Writing a guide is easier than coding it.
* **Bad, because** People might not read the guide.
* **Bad, because** People might not follow the guide.

### Option 2: Encode SQL Alchemy best practices

* **Good, because** Having a test fail ensures that best practices are followed.
* **Good, because** Quickly tried to write an example test, and it was reasonably easy See [Appendix A](#appendix-a-example-test-for-sql-alchemy-best-practices)
* **Bad, because** Tests might be harder to maintain.

### Option 3: Migrate to another ORM

SQL Alchemy requires you to set the back relationship on models, which makes it easy to accidentally load too much data.

* **Good, because** Another ORM might be easier to use, or use these best practices by default.
* **Bad, because** This is a big migration
* **Bad, because** Other issues might pop up.

# Appendix A: Example test for SQL Alchemy best practices
```python
import pytest
from sqlalchemy import inspect

from app.database.database import Base

# 1. Collect all models from the SQLAlchemy registry
models = [mapper.class_ for mapper in Base.registry.mappers]


@pytest.mark.parametrize("model", models)
def test_relationships_use_lazy_raise(model):
    """
    Ensures all relationships on a model are configured with lazy='raise'.
    """
    mapper = inspect(model)

    for relationship in mapper.relationships:
        # We check the 'lazy' attribute of the relationship
        # 'raise' is the value we are looking for.

        # Optional: If you only care about collections (one-to-many/many-to-many)
        # and want to allow joined loading for many-to-one, uncomment below:
        # if not relationship.uselist:
        #     continue
        if relationship.uselist:
            assert relationship.lazy == 'raise', (
                f"Relationship '{relationship.key}' on model '{model.__name__}' "
                f"is set to lazy='{relationship.lazy}'. It must be set to 'raise'."
            )
```
