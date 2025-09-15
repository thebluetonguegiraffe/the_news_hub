run-chroma-server:
	@echo "Starting ChromaDB in background..."
	@python db/run_chroma_server.py

run-chroma-client:
	@chroma browse $(shell python3 -c "from config import db_configuration; print(db_configuration['collection_name'])") --local

run-api:
	@echo "Starting FastAPI server..."
	@cd api && uvicorn main:app --host 0.0.0.0 --port 7000 --reload

test-api: # TO DO: move to general test
	@echo "Testing API endpoints..."
	@python api/test_api.py


AIRFLOW_SCRIPT := ./airflow/airflow_setup.sh

.PHONY: start stop

start-airflow:
	@echo "Starting Airflow..."
	@exec bash $(AIRFLOW_SCRIPT)

build-mongo.container:
	@docker compose --env-file ./.env -f ./db/mongo-container.yml up -d

run-frontend-dev:
	@cd dashboard && npm run dev

run-frontend:
	@cd dashboard && rm -rf .next && rm -rf node_modules/.cache && npm run build && npm start

stop-dashboard-cloudflare-tunnel:
	@echo "Stopping Cloudflare tunnel..."
	@sudo systemctl stop cloudflared-dashboard.service

start-dashboard-cloudflare-tunnel:
	@echo "Starting Cloudflare tunnel..."
	@sudo systemctl start cloudflared-dashboard.service

stop-api-cloudflare-tunnel:
	@echo "Stopping Cloudflare tunnel..."
	@sudo systemctl stop cloudflared.service

start-api-cloudflare-tunnel:
	@echo "Starting Cloudflare tunnel..."
	@sudo systemctl start cloudflared.service