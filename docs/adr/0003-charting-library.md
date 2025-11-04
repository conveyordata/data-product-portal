# Charting Library

## Context and Problem Statement

The new data product usage feature requires us to implement several new data visualizations, including a stacked area chart and a horizontal bar chart. These charts must be interactive, supporting filtering and tooltips. Our application currently uses the Ant Design component library. We need to select a charting library that integrates seamlessly with our existing design system and can fulfill these new requirements.

## Decision Drivers

* Ant Design Integration: The library must have a look and feel consistent with Ant Design to avoid visual fragmentation.
* Component Availability: Must natively support stacked area charts, horizontal bar charts, ...
* Performance: Must handle time-series data efficiently (e.g., 90+ days of data).
* Maintainability: A well-documented and actively maintained library is preferred to reduce the engineering burden.

## Considered Options

* **Option 1: Ant Design Charts (AntV)** This is the official charting library built by the Ant Design team. It is specifically designed to work with AntD applications.
* **Option 2: Recharts** A very popular, component-based charting library for React. It is known for its simplicity and composability.

## Decision Outcome

**Chosen option:** *Option 1: Ant Design Charts (AntV)*. This is the most logical and low-risk choice. It guarantees visual consistency with our existing design system, directly supports the required charts, and is maintained by the same organization. This alignment minimizes styling overhead and integration friction.

### Confirmation

N/A

## Pros and Cons of the Options

### Option 1: Ant Design Charts

* **Good, because** Seamless Integration: Designed to work perfectly with Ant Design; visual consistency is guaranteed.
* **Good, because** Component-Complete: Natively supports all required chart types (area, bar).
* **Good, because** Maintained by Ant: Aligned with the AntD ecosystem and release cycle.
* **Bad, because** Might be less flexible for highly bespoke or complex visualizations.

### Option 2: Recharts

* **Good, because** Popular & Simple: Large community and easy-to-use component-based API.
* **Bad, because** Visual Mismatch: Requires significant custom styling to match the Ant Design look and feel.
* **Bad, because** Separate Dependency: Another major library to maintain and manage.