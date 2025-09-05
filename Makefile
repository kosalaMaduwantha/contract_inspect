install_dependencies:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

install_ollama:
	@echo "Installing Ollama..."
	curl -fsSL https://ollama.com/install.sh | sh

invoke_ollama_llm:
	@echo "Invoking Ollama LLM..."
	ollama serve

deploy_weaviate_local:
	@echo "Deploying Weaviate locally using Docker..."
	docker compose -f compose-files/compose-weaviate.yml -d