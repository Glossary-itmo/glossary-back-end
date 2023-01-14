run:
	pipenv shell \
	uvicorn main:app --reload

build:
	docker compose up -d

down:
	docker compose down