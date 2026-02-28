# Standardize Event Delivery from Portal to External Systems

## Context and Problem Statement
The data product portal must emit events when significant actions occur, such as:
- product creation
- access grants
- team changes
to enable external systems to react and provision necessary infrastructure.
We will implement this as an extension from the existing audit mechanism, by enriching them to business events and sending them to a queue.
From there the customer can implement a client that processes the events and provisions the necessary infrastructure.

## Decision Drivers
* Multi-deployment support (cloud/on-premise)
* Decoupling portal from the consumer infrastructure provisioning
* Reliability (at-least-once delivery, acknowledgments)
* Extensibility for new event types/consumers
* Operational simplicity and troubleshooting

## Considered Options
* **Option 1: Cloud-native message brokers** (Queueing system like SQS, Azure queues)
* **Option 2: NATS JetStream** (lightweight, reliable, Python-friendly)
* **Option 3: RabbitMQ** (feature-rich, heavier)
* **Option 4: Mosquitto (MQTT)** (ultra-lightweight, less cloud-compatible)
* **Option 5: Webhook delivery** (HTTP callbacks to external systems)
* **Option 6: Task queue implementation** (custom or existing task queue for event delivery)

## Decision Outcome
**Chosen option:** Use cloud-native brokers for cloud deployments and NATS JetStream for on-premise setups.
NATS JetStream is lightweight, fast, easy to deploy, supports reliable message processing with acknowledgments, and integrates well with Python.
As a fallback we can still support webhook delivery for integrating with external systems where a message broker would be too complex.

We only guarantee at least once delivery and thus require the clients to be idempotent when performing changes.
To do this correctly, we will need to implement the outbox pattern to guarantee we send every event.
We provide no guarantees about the order of events atm.

## Pros and Cons of the Options

### Option 1: Cloud-native message brokers
* **Good, because** managed, scalable, reliable, easy integration in cloud setups
* **Neutral, because** not available on-premise
* **Bad, because** vendor lock-in, cost

### Option 2: NATS JetStream
* **Good, because** lightweight, fast, easy to deploy, reliable, Python support, cloud-like API
* **Good, because** decouples Portal from the infrastructure provisioning at client side.
* **Neutral, because** does not have all features available for message brokers.
* **Bad, because** requires operational knowledge about Nats

### Option 3: RabbitMQ
* **Good, because** mature, feature-rich, strong Python support
* **Good, because** decouples Portal from the infrastructure provisioning at client side.
* **Neutral, because** heavier, more complex to operate by us.
* **Bad, because** overkill for simple eventing system, higher resource usage

### Option 4: Mosquitto (MQTT)
* **Good, because** ultra-lightweight, simple setup, Python clients
* **Neutral, because** best for IoT/pub-sub, not general eventing
* **Bad, because** less compatible with cloud APIs, limited durability

### Option 5: Webhook delivery
* **Good, because** simple, direct integration with external systems, no extra infrastructure needed
* **Neutral, because** relies on external system availability, may require retries
* **Bad, because** less reliable (no built-in delivery guarantees), harder to monitor and troubleshoot

### Option 6: Task queue implementation (Celery)
* **Good, because** flexible, can be tailored to requirements, supports retries and durability
* **Bad, because** adds operational complexity as we need to manage a broker and the client framework to process tasks (taskiq,...)
* **Bad, because** it introduces coupling between Portal and the tasks being executed, as we need to manage retries, failures, ...
* **Bad, because** Overkill as Portal does not need to care about the state management of tasks.
  Clients can choose to implement state transitions if they want to inform the users

### Option 7: Kafka as message broker
* **Good, because** flexible and popular technology.
* **Neutral, because** we cannot assume that every client has a Kafka broker that we can use.
* **Bad, because** heavy to operate as it requires a lot of operational expertise
* **Bad, because** overkill to set it up for the limited number of portal events.

## Event Flow Diagram
```mermaid
graph LR
    A[Portal<br />Audit events]--> B[Portal<br/>Event enricher] --> C[Portal<br/>Event Producer] -->|Publish Event| D[Message Broker<br/>Pub-Sub/NATS]
    D -->|Subscribe & Consume| E[External Consumer<br/>Infrastructure Provisioning]
    style A fill:#345F5C
    style B fill:#668C80
    style C fill:#586E82
    style D fill:#B4AEA2
    style E fill:#8FAFAF
```

## Example Event Types
The content of the events still needs to be defined, but some examples are:
- Data Product Creation / Deletion
- Output Port Creation / Deletion
- Technical Asset Creation / Change / Deletion
- Accepted Access / Revoked Access

We aim to provide business events with all relevant info in them for clients to perform the infrastructure provisioning.
