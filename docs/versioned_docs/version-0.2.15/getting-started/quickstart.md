---
sidebar_position: 1
---

# Quickstart

Get the **Data Product Portal** up and running in just a few steps.

---

## 🧱 Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)

---

## 🛠️ Clone the Repository

```bash
git clone https://github.com/conveyordata/data-product-portal.git
cd data-product-portal
```

---

## ▶️ Start the Application

Run the following to spin up the full stack in *Sandbox mode*:

```bash
docker-compose up
```

This will start:
- The **backend**
- The **frontend**
- A **PostgreSQL** database
- A **mailhog** local mail server
- A **nginx** server to direct backend and frontend traffic

Wait until the backend service is fully ready before accessing the app. The logs should display
```
INFO: Uvicorn running on http://0.0.0.0:5050 (Press CTRL+C to quit)
```

---

## 🌐 Open the App in Browser

Visit http://localhost:8080


You should see the **Data Product Portal** UI!

:::danger[Warning]

The Docker setup will **drop and recreate the PostgreSQL database** on startup. Do not connect this setup to any live production database.

:::

### Limited Functionality

The Docker setup is meant for evaluation and exploration. Most integrations are disabled by default.
If you'd like to test integrations (e.g., *OIDC*, *Conveyor*, *AWS*), you must install the necessary dependencies and update your configuration accordingly.

---

## 🧪 Try It Out

- Search for a data product
- Explore metadata and domains
- Add governance rules or tags
- Play around with the settings

---

## 🙋 Need Help?

Check the [Troubleshooting guide](../user-guide/troubleshooting.md)
Or open an [issue on GitHub](https://github.com/conveyordata/data-product-portal/issues)

---

## 🧱 Next Steps

- Learn about the [Concepts](../concepts/data-products)
- Customize your [Configuration](./configuration)
- Start [Creating Data Products](../user-guide/creating-products)
```
