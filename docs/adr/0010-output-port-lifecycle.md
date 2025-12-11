# Output Port Lifecycle Management

## Context and Problem Statement

Data Producers want to have the ability to control the visibility of their Output Ports during development.
Data Consumers want to have visibility on the state of a Data Output, in order to estimate if it is a good fit.

## Decision Drivers

* Ease of use
* Control for the Data Producer
* Clarity for the Data Consumer

## Considered Options

* **Option 1: Simple toggle** An Output Port can be switched between 'draft' and 'published'.
  Draft Output Ports are not visible to people outside the data product, published outputs are visible.
* **Option 2: State machine** An Output Port has four states: 'draft', 'active', 'deprecated' and 'retired'.
  The addition of the deprecated and retired states over the simple toggle allows existing consumers to be gradually moved away from the Output Port.
* **Option 3: A configurable state machine** We use the current lifecycles but add a view strategy to them to govern whether users can see the Output port.
  This allows users to only use the lifecycles they have.

## Decision Outcome

**Chosen option:** *Option 2: State machine*.
A simple toggle for the visibility is insufficient to properly manage consumer expectations.
The addition of more explicit states allows producers to manage the lifecycle of their outputs in a more gradual way,
resulting in clearer communication towards the data consumers, and success in meeting expectations.

## Confirmation

We will introduce a lifecycle property on the Data Output model.
This property can take the form of four stages.

#### Draft

Lifecycle for a newly created Data Output. Not visible yet to outside consumers, so cannot be requested.
Consumers can be added by invitation in order to test a new Data Output while it’s still under development.

#### Active

Data Output is published and visible in the Marketplace. Consumers can view and request the Output.

#### Deprecated

The Data Output is no longer maintained. It should not be listed in the Marketplace anymore.
Consumers that already have access can still view and access the output, but it cannot be requested by new Consumers, not even by invitation.

#### Retired

The Output Port has reached End-of-Life. By moving to this stage, all remaining consumers are removed (should be done with an explicit approval in case there are still consumers). At this point, only the team working on the parent Data Product can still view this Data Output. The team can now decide to remove the Data Output from portal altogether. Removal should not be possible in other lifecycle stages.

### Constraints

- Output Ports can only be removed in the Retired stage, when they are guaranteed to no longer have consumers.
- Output Ports that are in draft (with consumers) can be deleted if the producer does not want to move forward with publishing.
- Once a Data Output has left the Draft phase to Active, it cannot move back.
- Output Ports can only reach Retired from Deprecated.
- Output Ports that are Deprecated can move back to Active should the product team decide so.
- A Retired Output port can move back to Draft should the product team decide so.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Active
    Draft --> [*]
    Active --> Deprecated
    Deprecated --> Retired
    Deprecated --> Active
    Retired --> Draft
    Retired --> [*]
```

## Pros and Cons of the Options

### Option 1: Simple toggle

* **Good, because** there is little implementation effort
* **Good, because** it is conceptually very simple
* **Bad, because** it provides no guidance on how to gradually remove an Output Port
* **Bad, because** it provides no signal to consumers if they should keep using the output or not

### Option 2: State machine

* **Good, because** we provide an opinion on how the lifecycle of an Output Port should be managed instead of only controlling visibility
* **Good, because** the lifecycle can be used to notify consumers, and provide a gentle path towards the EOL of an Output Port
* **Neutral, because** the state transitions need to be correctly modeled, so the implementation effort is higher
* **Neutral, because** data producers need to understand the process that portal offers

### Option 3: Configurable state machine

* **Good, because** we give flexibility to data producers to choose their own lifecycles
* **Good, because** we can add automation between the steps to notify consumers, or even enforce certain actions.
* **Neutral, because** the state transitions need to be correctly modeled, so the implementation effort is higher
* **Neutral, because** migrating to this model after implementing option 2 is straightforward
* **Bad, because** it is overkill to implement a flexible mechanism at this time.
