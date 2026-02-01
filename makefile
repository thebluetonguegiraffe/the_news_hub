include .env
export

run-api-dev:
	@echo "Starting FastAPI server..."
	PYTHONPATH=. uvicorn api.main:app --host 0.0.0.0 --port 7001 --reload --reload-dir api

deploy-api:
	docker compose -f api/the-news-hub-api.yml up --build -d

run-dashboard-dev:
	@cd dashboard && npm run dev -- -H 0.0.0.0


GITHUB_USER := thebluetonguegiraffe
IMAGE_NAME := the_news_hub
TAG ?= $(shell git rev-parse --short HEAD)
REGISTRY := ghcr.io
FULL_IMAGE := $(REGISTRY)/$(GITHUB_USER)/$(IMAGE_NAME):$(TAG)
LATEST_IMAGE := $(REGISTRY)/$(GITHUB_USER)/$(IMAGE_NAME):latest

PLATFORMS=linux/aarch64

cr-login:
	@echo $(CR_PAT) | docker login $(REGISTRY) -u $(GITHUB_USER) --password-stdin

add-translator:
	@echo "Adding QEMU translators for cross-platform builds..."
	docker run --privileged --rm tonistiigi/binfmt --install all

setup-buildx:
	docker buildx inspect $(BUILDER_NAME) > /dev/null 2>&1 || docker buildx create --name $(BUILDER_NAME) --use
	docker buildx inspect --bootstrap

build: setup-buildx
	docker buildx build \
		--platform $(PLATFORMS) \
		-t $(FULL_IMAGE) \
		-t $(LATEST_IMAGE) \
		--load \
		.

build-no-cache:
build-no-cache: setup-buildx
	docker buildx build \
		--no-cache \
		--platform $(PLATFORMS) \
		-t $(FULL_IMAGE) \
		-t $(LATEST_IMAGE) \
		--load \
		.

push:
	docker push $(FULL_IMAGE)
	docker push $(LATEST_IMAGE)

all: build push