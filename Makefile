COMPOSE_BASE := docker compose -f docker-compose-local.yml

build-up:
	$(COMPOSE_BASE)	 up -d --build;

up:
	$(COMPOSE_BASE)	 up -d;

restart:
	$(COMPOSE_BASE)	 restart;

down:
	$(COMPOSE_BASE)	 down;

ui:
	streamlit run ./frontend/main.py --server.port 8090

backend:
	python ./api/main.py
