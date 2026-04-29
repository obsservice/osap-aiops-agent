UV ?= uv
HOST ?= 0.0.0.0
PORT ?= 3080
APP_MODULE ?= aiops_agent.main:app

install: 
	$(UV) sync

run: install
	$(UV) run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --no-access-log --reload
