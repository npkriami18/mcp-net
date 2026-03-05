# MCP-Net

**A Dynamic Discovery Layer for MCP Servers**
<table>
<tr>
<td width="40%" valign="top">

## Table of Contents

- [The Idea](#the-idea)
- [Architecture Diagram](#architecture-diagram)
- [High-Level Concept](#high-level-concept)
- [Core Components](#core-components)
- [Routing Protocol](#routing-protocol)
- [Example Execution Flow](#example-execution-flow)
- [What This Project Demonstrates](#what-this-project-demonstrates)
- [Current Limitations](#current-limitations)
- [Future Directions](#future-directions)
- [Running the System](#running-the-system)

</td>

<td width="60%" valign="top">

<img src="https://github.com/user-attachments/assets/81e28457-0c46-4011-b0f2-bb429b3033af" width="100%">

</td>
</tr>
</table>

#### Note

This project is an **architecture experiment** exploring how MCP servers can form a **dynamic discovery network**.


## The Idea

Traditional **Model Context Protocol (MCP)** systems typically look like this:

```
Client → MCP Server → Tools
```

The tools behind the server may be dynamic, but the **MCP server itself is static**.  
This creates an architectural limitation: the client must already know which MCP servers exist.

This project explores a simple question:

> If tools can be dynamic, why can't **MCP servers themselves be discovered dynamically?**

Historically, computer networks had a similar problem.

Before the creation of the **Domain Name System (DNS)**, machines stored **static host mappings** locally.  
As networks grew, this became impossible to maintain.

DNS solved this by introducing a **hierarchical discovery system**.

```
Root → TLD → Domain → Host
```

This project explores a similar idea for **MCP ecosystems**.

Instead of statically wiring every MCP server into the client, we introduce a **hierarchical discovery network** of MCP nodes.

The client only knows **one root MCP node**, and the rest of the system is discovered dynamically.

---
## Architecture Diagram

<img width="2395" height="1311" alt="mcp-net" src="https://github.com/user-attachments/assets/81e28457-0c46-4011-b0f2-bb429b3033af" />

**Note-1. Simplified Tool and Service Names**

The tool names and MCP service names shown in the diagram (e.g., `CSV Loader`, `JSON Loader`, `Transform Service MCP`, etc.) are used **purely for illustration**.

In real-world systems:

- MCP servers may expose **many more tools**
- Tools may represent **complex services, APIs, workflows, or pipelines**
- Domain boundaries may differ depending on the application

The goal of the diagram is to demonstrate the **routing architecture**, not to represent a specific tool ecosystem.

---

**Note-2. Numbered Execution Flow**

The red numbers in the diagram represent the **idealized sequence of interactions** during a query execution.

A typical flow looks like:

1. Client sends the request to **MCP Navigator**
2. Navigator queries the **Root MCP**
3. Root MCP performs **LLM-based reasoning** and selects the appropriate **Domain MCP** -> MCP Navigator -> mcp_invoker -> domain MCP
4. Domain MCP performs further **LLM-based reasoning** 
5. The request is forwarded to the relevant **Service MCP**
6. The **MCP Invoker** connects to the leaf MCP server
7. The leaf MCP exposes its available **tools**
8. The invoker selects and executes the appropriate tool
9. The result flows back through the same chain to the client

This numbered flow represents the **ideal execution path** to help illustrate how requests traverse the MCP network.

---

**Note-3. Resolver Nodes**

Nodes such as the **Root MCP** and **Domain MCPs** act as **resolver nodes**.

Their role is to:

- analyze the query using LLM reasoning
- determine the most appropriate next node
- return the endpoint of the next MCP server

They **do not execute tools** themselves.

---

**Note-4. Leaf Nodes**

Leaf nodes represent **actual MCP servers exposing executable tools**.

These nodes are responsible for:

- exposing tool schemas
- executing tool logic
- returning results


## High-Level Concept

The system behaves like a **routing network for MCP services**.

A user query flows through multiple routing layers until it reaches the **leaf MCP server** that actually executes the tool.

```
Client
  ↓
Root MCP
  ↓
Domain MCP
  ↓
Service MCP
  ↓
Tool Execution
```

Each MCP node performs **semantic routing** and returns the **next endpoint**.

The client continues traversing the network until a **leaf node** is reached.

---

# Architecture Overview

The system is structured as a **hierarchical MCP graph(DAG)**.

```
Client
↓
MCP Orchestrator/Navigator
↓
Root MCP
↓
Domain MCP
├ Data Domain MCP
├ Dev Domain MCP
└ Utility Domain MCP
↓
Service MCP (Leaf)
↓
Tool Execution
```

Each layer has a **specific responsibility**.

---

# Core Components

## MCP Orchestrator/Navigator

The orchestrator acts as the **entry point** for the client.

Responsibilities:

- coordinate routing across the MCP network
- invoke downstream MCP servers
- interpret routing responses
- continue traversal until a leaf node is reached

The orchestrator hides the **multi-hop routing complexity** from the client.

---

## Root MCP

The **Root MCP** performs the first level of routing.

It determines which **domain** should handle the request.

Example domains:

```
data_domain
dev_domain
utility_domain
```

Routing decisions are performed using an **LLM-based semantic classifier**.

---

## Domain MCPs

Each domain MCP handles **service-level routing** within its domain.

Example:

```
data_domain
  ↓
transform_service
file_service
dataset_service
```

Domain MCPs **do not execute tools**.  
They only determine which **service MCP** should receive the request.

---

## Leaf MCP Services

Leaf MCP servers expose the **actual tools**.

Examples:

```
csv_to_json
load_dataset
analyze_text
summarize_logs
```

These nodes perform the **real computation**.

---

## Universal MCP Invoker

The **mcp_invoker** enables dynamic execution of tools from any MCP server.

Workflow:

1. Connect to a remote MCP server
2. Discover available tools (`list_tools`)
3. Use an LLM agent to choose the correct tool
4. Generate arguments dynamically
5. Execute the tool
6. Return the result

This makes it possible to invoke **unknown MCP services dynamically** without writing custom integrations.

---

# Routing Protocol

Every routing MCP returns a **standardized JSON response**.

Example:

```json
{
  "status": "success",
  "node_type": "intermediate",
  "service_name": "data_domain",
  "endpoint": "http://localhost:10000/data-domain-mcp/mcp",
  "description": "Handles data loading and transformation tasks.",
  "confidence": 0.95,
  "reason": "The query was routed to data_domain."
}
```

### Node Types

```
intermediate → another MCP node must be invoked
leaf → tool execution node
```

This schema allows the client to **traverse the MCP graph dynamically**.

---

# Example Execution Flow

User query:

```
convert csv dataset to json
```

Execution path:

```
Client
↓
Orchestrator
↓
Root MCP → routes to data_domain
↓
Data Domain MCP → routes to transform_service
↓
Transform Service MCP
↓
csv_to_json tool executed
```

Each step returns the **next endpoint** until the tool is executed.

---

# What This Project Demonstrates

### Hierarchical MCP Networks (DAG)

Instead of a single monolithic agent, the system uses a **network of MCP services**.

---

### Dynamic MCP Discovery

Clients only need to know the **root node**.

All other services are discovered through **semantic routing**.

---

### LLM-Driven Routing

Language models determine:

- domain classification
- service routing
- tool selection

---

### Universal Tool Invocation

Tools are discovered dynamically via MCP APIs rather than statically registered.

---

# Current Limitations

This repository demonstrates an **architecture concept**, not a production-ready framework.

### Static Endpoints

Currently MCP endpoints are hardcoded.

Possible improvement:

```
distributed registry
dynamic service registration
heartbeat-based discovery
```

---

### Tool Metadata Overhead & Caching not implemented 

Each invocation performs:

```
list_tools()
```

Caching tool schemas could significantly reduce latency.

---

### Sequential Traversal

The current design performs **sequential MCP calls**.

Future versions could explore:

```
parallel routing
candidate evaluation
latency-aware selection
```

---

### Limited Error Recovery

Failures are returned directly to the client.

Future improvements could include:

```
automatic retries
argument repair
fallback services
```

---

# Future Directions

This project opens the door for several interesting ideas.

### MCP Service Registry

A distributed registry where MCP nodes can **self-register**.

```
root
 ↓
registry
 ↓
auto-discovered services
```

---

### Cached Tool Graphs

Cache tool schemas and service metadata to reduce repeated discovery calls.

---

### Self-Healing Invocations

Automatically repair tool arguments when execution fails.

---

### Adaptive Routing

Use historical success signals to improve routing decisions.

---

# Why This Exists

This project explores an architectural question:

> What if AI agents were not monolithic systems, but **networks of discoverable MCP services**?

Possible benefits:

- scalable tool ecosystems
- modular domain separation
- dynamic capability discovery
- reusable services

---

# Running the System

Start the MCP services:

```
root_mcp
data_domain_mcp
dev_domain_mcp
utility_domain_mcp
mcp_invoker
```

Then start the **orchestrator**.

The client only needs the **orchestrator endpoint**.

---
