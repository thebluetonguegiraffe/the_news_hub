# Project Setup Guide

## Airflow Setup

---

The **Airflow service** (scheduler, workers, and UI) is containerized and can be deployed via this [repository](https://github.com/thebluetonguegiraffe/dockerized_airflow). The project’s DAGs are located in the `airflow_dags` folder and are integrated into the environment by mounting that directory as a  **Docker volume** .

```bash
>> dockerized_airflow/airflow.yaml
- ${HOME}/the_news_hub/airflow_dags:/opt/airflow/dags/the_news_hub
```

To execute the code defined in the DAGs, the environment requires specific system dependencies. Consequently, the project is **dockerized** and pushed to  **GitHub Container Registry (GHCR)**. When Airflow triggers a DAG, it builds a container with all necessary dependencies to execute the script in an isolated, consistent environment.

To create The News Hub docker image and push it into GHCR:

```bash
make cr-login
make build-no-cache
make push
```

Notice that to authenticate with the **GitHub Container Registry (GHCR)** and push or pull your Docker images, you need a  **Personal Access Token (PAT)**.

## API deploy

---

The **News Hub API** is containerized for portability and exposed securely via a  **Cloudflare Tunnel** , which eliminates the need to open firewall ports on your server.

```bash
make deploy api
```

Tunnel can be set up by adding this to the tunnel `config.json`

```bash
>> cat /etc/cloudflared/tunnels-config.yml
tunnel: tunnel-id
credentials-file: /etc/cloudflared/tunnel-id.json
ingress:
  - hostname: the-news-hub-api.thebluetonguegiraffe.online
    service: http://localhost:7010
```


## Dashboard Deploy

---

Dashboard deploy is perfomed via Vercel.
