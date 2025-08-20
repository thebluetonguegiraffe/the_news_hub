run-chroma:
	@echo "Starting ChromaDB in background..."
	@python db/run_chroma_server.py

run-client:
	@chroma browse $(shell python3 -c "from src.config import db_configuration; print(db_configuration['collection_name'])") --local

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
