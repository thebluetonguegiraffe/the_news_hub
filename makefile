include .env
export

run-api-dev:
	@echo "Starting FastAPI server..."
	PYTHONPATH=$(PWD) uvicorn api.main:app --host 0.0.0.0 --port 7001 --reload

deploy-api:
	docker compose -f api/the-news-hub-api.yml up --build -d

run-dashboard-dev:
	@cd dashboard && npm run dev

run-dashboard:
	@cd dashboard && rm -rf .next && rm -rf node_modules/.cache && npm run build && npm start


GITHUB_USER := thebluetonguegiraffe
IMAGE_NAME := the_news_hub
TAG ?= $(shell git rev-parse --short HEAD)
REGISTRY := ghcr.io
FULL_IMAGE := $(REGISTRY)/$(GITHUB_USER)/$(IMAGE_NAME):$(TAG)
LATEST_IMAGE := $(REGISTRY)/$(GITHUB_USER)/$(IMAGE_NAME):latest

cr-login:
	@echo $(CR_PAT) | docker login $(REGISTRY) -u $(GITHUB_USER) --password-stdin

build:
	docker build -t $(FULL_IMAGE) -t $(LATEST_IMAGE) .

build-no-cache:
	docker build --no-cache -t $(FULL_IMAGE) -t $(LATEST_IMAGE) .

push:
	docker push $(FULL_IMAGE)
	docker push $(LATEST_IMAGE)

all: build push