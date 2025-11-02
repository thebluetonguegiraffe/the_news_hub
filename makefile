
run-chroma-client:
	@chroma browse $(shell python3 -c "from config import chroma_configuration; print(chroma_configuration['collection_name'])") --host http://localhost:8000

run-api:
	@echo "Starting FastAPI server..."
	PYTHONPATH=$(PWD) uvicorn api.main:app --host 0.0.0.0 --port 7000 --reload

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