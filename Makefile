IMAGE_NAME=tcc-devsecops-api
IMAGE_TAG=local
CONTAINER_NAME=tcc-devsecops-api
APP_DIR=app
PORT=8000

install:
	python -m pip install -r $(APP_DIR)/requirements.txt

test:
	cd $(APP_DIR) && python -m pytest -v

run:
	cd $(APP_DIR) && python -m uvicorn main:app --reload

docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) ./$(APP_DIR)

docker-run:
	docker run --name $(CONTAINER_NAME) -p $(PORT):8000 $(IMAGE_NAME):$(IMAGE_TAG)

docker-stop:
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)

docker-clean:
	-docker stop $(CONTAINER_NAME)
	-docker rm $(CONTAINER_NAME)
	-docker rmi $(IMAGE_NAME):$(IMAGE_TAG)