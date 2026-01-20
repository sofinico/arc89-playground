.PHONY: setup lint format type-check new-address create-asa get-asa delete-asa create-metadata get-metadata delete-metadata use-localnet use-testnet env-files

help:
	@echo "Available commands:"
	@echo "  setup         		 Set up the environment"
	@echo "  lint          		 Run linting"
	@echo "  format        		 Format code"
	@echo "  type-check    		 Run type checking"
	@echo "  new-address    	 Create a new Algorand address"
	@echo "  create-asa    		 Create a new ASA on the configured network"
	@echo "  get-asa	 		 Fetch ASA information from the configured network"
	@echo "  delete-asa	 		 Delete an ASA on the configured network"
	@echo "  create-metadata 	 Create ARC-89 metadata for an ASA on the configured network"
	@echo "  get-metadata 	     Get ARC-89 metadata for an ASA on the configured network"
	@echo "  delete-metadata 	 Delete ARC-89 metadata for an ASA on the configured network"
	@echo "  use-localnet   	 Set NETWORK=localnet in .env"
	@echo "  use-testnet    	 Set NETWORK=testnet in .env"
	@echo "  env-files      	 Copy example env files to .env, .env.localnet, .env.testnet"

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

create-asa:
	poetry run python -m examples.create_asa

get-asa:
	poetry run python -m examples.get_asa

delete-asa:
	poetry run python -m examples.delete_asa

create-metadata:
	poetry run python -m examples.create_metadata

get-metadata:
	poetry run python -m examples.get_metadata

delete-metadata:
	poetry run python -m examples.delete_metadata

use-localnet:
	poetry run python scripts/switch_network.py localnet
	@echo "\nEnsure algokit localnet is running (\`algokit localnet status\`)." 
	@echo "Run \`make setup\` to set up the environment.\n"

use-testnet:
	poetry run python scripts/switch_network.py testnet
	@echo "\nEnsure CALLER_MNEMONIC environment variable is available and funded (\`export CALLER_MNEMONIC=...\` or set in \`.env.testnet\`)." 
	@echo "Run \`make setup\` to set up the environment.\n"

env-files:
	cp .env.example .env
	cp .env.localnet.example .env.localnet
	cp .env.testnet.example .env.testnet
