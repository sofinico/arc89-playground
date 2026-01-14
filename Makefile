.PHONY: setup lint format type-check new-wallet

help:
	@echo "Available commands:"
	@echo "  setup         		 Set up the environment"
	@echo "  lint          		 Run linting"
	@echo "  format        		 Format code"
	@echo "  type-check    		 Run type checking"
	@echo "  new-wallet    		 Create a new Algorand address"

setup:
	poetry run python config.py

lint:
	poetry run ruff check . --fix

format:
	poetry run ruff format . 
	poetry run check-yaml 
	poetry run check-toml
	poetry run mdformat .

type-check:
	poetry run mypy .

new-address:
	poetry run python scripts/create_address.py
