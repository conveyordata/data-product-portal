# Scenario: The Owner Approves Agent Access

A short demo (about 5 minutes) in three steps: an agent can't do something, the owner of the data gives permission, and now it can.
The story is about organisations and agreements rather than technology: access to data goes through the owner, whether the consumer is an application or an agent.

For the setup of the demo environment, see the [README](../README.md). This scenario relies on two things `task create-products` configures:

- Jane Researcher (`jane.researcher@pharma.com`) owns Inventory Snapshot. John Scientist owns the other two data products.
- The Inventory Data output port is Restricted, so an access request stays pending until Jane decides.

## Before You Start

- Start from a clean state, so the access request does not exist yet:

  ```bash
  task reset
  task create-products
  ```

- Open the portal at http://localhost:5050. You are logged in as John Scientist.
- Open the agent chat UI connected to `http://localhost:7070`.
- Start a new chat for every question.

## Setup (30 seconds)

Show the three data products in the Product Studio.

> "A fictional company with three domains, each with its own data product. Each data product has its own agent, which only sees its own data and knows what that data means."

## Moment 1: the Agent Doesn't Fall for It (about 1.5 minutes)

Ask the Sales Transaction Ledger agent a question with a wrong assumption:

> *"Our average order is $150. How much revenue do we make from 10 orders?"*

The agent reads its semantic model, calculates the real average order value and corrects the premise: the average order is $125.10, so 10 orders bring in $1,251, not $1,500. It cites the `average_order_value` metric. Amounts are stored in cents, and the rule to divide by 100 also comes from the semantic model.

> "That rule isn't in the prompt, it's in the data product. Any agent that uses this product gets it for free."

## Moment 2: the Owner Approves Access (about 3 minutes)

1. Ask the Sales Transaction Ledger agent a question that needs stock data:

   > *"Which of our top-selling SKUs are at risk of going out of stock?"*

   The agent lists the top sellers, but says it has no inventory data to check stock levels.

2. In the portal, as John, request access for Sales Transaction Ledger to the Inventory Data output port of Inventory Snapshot. The request shows up in the Product Studio under My Requests, with status pending.

3. Switch user to Jane Researcher (user menu, Switch user). As the owner of Inventory Snapshot, she sees the request in the Product Studio under Pending Requests. Approve it.

   On approval, the provisioner grants the Sales Transaction Ledger database user read access to the `inventory_snapshot` schema and adds the inventory semantic model to the Sales Transaction Ledger agent. The agent server reloads automatically.

4. Ask the same question again, in a new chat. The agent now combines sales with current stock and flags HIKE-BOOTS-M as out of stock. It also checks the retired flag of the inventory, a rule it received with the inventory semantic model.

> "Someone requests access, the owner of the source decides. That's how access between applications works today. The only difference is that this user is an agent."

## Notes

- John is admin, so he also sees the pending request. Approve as Jane to show that the owner decides.
- Only the owner can approve: other users, such as Bob Johnson, are refused.
- Agent answers vary slightly between runs. Rehearse once, then reset before presenting.
