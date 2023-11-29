run:
	docker-compose up --build

down:
	docker-compose down

feed:
	docker-compose exec app flask create-objects