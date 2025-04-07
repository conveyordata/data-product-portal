
# Quickstart

Get the **Data Product Portal** up and running in just a few steps.

---

## 🧱 Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Node.js ≥ 18](https://nodejs.org/)
- [Git](https://git-scm.com/)

---

## 🛠️ Clone the Repository

```bash
git clone https://github.com/conveyordata/data-product-portal.git
cd data-product-portal
```

---

## ▶️ Start the Application

Run the following to spin up the full stack:

```bash
docker-compose up -d
```

This will start:
- The **backend**
- The **frontend**
- A **PostgreSQL** database

Wait until the backend service is fully ready before accessing the app.

---

## 🌐 Open the App in Browser

Visit:

```
http://localhost:8585
```

You should see the **Data Product Portal** UI!

---

## 🧪 Try It Out

- Search for a data product
- Explore metadata and domains
- Add governance rules or tags

---

## 🙋 Need Help?

Check the [Troubleshooting guide](../user-guide/troubleshooting.md)
Or open an [issue on GitHub](https://github.com/conveyordata/data-product-portal/issues)

---

## 🧱 Next Steps

- Learn about [Architecture](../concepts/architecture.md)
- Customize your [Configuration](./configuration.md)
- Start [Creating Data Products](../user-guide/creating-products.md)
```
