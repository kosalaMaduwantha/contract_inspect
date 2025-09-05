# Installation Guide

This guide provides detailed instructions for setting up the Contract Inspector system on different platforms.

## Table of Contents

- [System Requirements](#system-requirements)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Step-by-Step Installation](#step-by-step-installation)
- [Verification](#verification)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

- **Minimum**: 8GB RAM, 4 CPU cores, 20GB disk space
- **Recommended**: 16GB RAM, 8 CPU cores, 50GB disk space
- **For large document sets**: 32GB+ RAM, NVMe SSD storage

### Software Requirements

- **Python**: 3.12 or higher
- **Docker**: 20.10+ with Docker Compose
- **Git**: Latest version
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10/11 with WSL2

## Platform-Specific Instructions

### Ubuntu/Debian Linux

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-pip python3.12-venv -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Log out and back in for Docker group changes to take effect
```

### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop from Applications
open -a Docker
```

### Windows (WSL2)

1. **Enable WSL2**:
   ```powershell
   # Run in PowerShell as Administrator
   wsl --install
   # Restart computer
   ```

2. **Install Ubuntu in WSL2**:
   ```bash
   wsl --install -d Ubuntu-22.04
   ```

3. **Follow Ubuntu instructions above** within WSL2 environment

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/kosalaMaduwantha/contract_inspect.git
cd contract_inspect
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3.12 -m venv env

# Activate virtual environment
# On Linux/macOS:
source env/bin/activate
# On Windows (WSL2):
source env/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify critical packages
python -c "import weaviate, ollama, yaml; print('Core packages installed successfully')"
```

### Step 4: Install and Configure Ollama

#### Option A: Automatic Installation (Linux/macOS)

```bash
# Download and install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Option B: Manual Installation

1. **Download Ollama**:
   - Visit [https://ollama.com/download](https://ollama.com/download)
   - Download appropriate version for your OS
   - Follow installation instructions

2. **Install Models**:
   ```bash
   # Start Ollama service (run in separate terminal)
   ollama serve
   
   # In another terminal, pull required models
   ollama pull llama3.2
   ollama pull nomic-embed-text
   
   # Verify models are installed
   ollama list
   ```

### Step 5: Set Up Weaviate Vector Database

```bash
# Start Weaviate using Docker Compose
docker compose -f compose-files/compose-weaviate.yml up -d

# Wait for Weaviate to be ready (may take 30-60 seconds)
sleep 30

# Verify Weaviate is accessible
curl -f http://localhost:8080/v1/meta || echo "Weaviate not ready yet, wait a bit more"
```

### Step 6: Configure the System

1. **Update Configuration Paths** (if needed):
   ```bash
   # Edit config.py to match your system paths
   vim src/core/config.py
   
   # Update these variables if your paths differ:
   # METADATA_CONFIG_PATH
   # DATA_FOLDER
   ```

2. **Prepare Document Directory**:
   ```bash
   # Create data directory if it doesn't exist
   mkdir -p data
   
   # Copy your PDF contracts to the data directory
   cp /path/to/your/contracts/*.pdf data/
   ```

3. **Update Metadata Configuration**:
   ```bash
   # Edit metadata.yml to describe your documents
   vim metadata.yml
   ```

### Step 7: Index Your Documents

```bash
# Navigate to indexer directory
cd src/core/retriver

# Run the document indexer
python index_invoker.py

# You should see output like:
# Processing Oracle_Cloud_Agreement.pdf...
# Content part extracted: ...
```

## Verification

### Test 1: Check All Services

```bash
# Check Python environment
python --version  # Should show 3.12+

# Check Ollama
ollama list  # Should show llama3.2 and nomic-embed-text

# Check Weaviate
curl http://localhost:8080/v1/meta  # Should return JSON metadata

# Check Docker containers
docker ps  # Should show weaviate container running
```

### Test 2: Run a Sample Query

```bash
# Navigate to core directory
cd src/core

# Run a test query
python rag.py

# Should output an answer about Oracle agreement
```

### Test 3: Direct Search Test

```bash
# Test search functionality
python -c "
from retriver.util.search_lib import weaviate_search
from sp_adapters.weaviate_adapter import WeaviateVectorDBAdapter
import retriver.util.search_lib as search_lib

adapter = WeaviateVectorDBAdapter()
adapter.connect()
search_lib.init(adapter)

results = search_lib.weaviate_search('oracle', 'hybrid', 'Page', 2)
print('Search results:', len(results))
adapter.close()
"
```

## Configuration

### Environment Variables

You can set these environment variables to customize paths:

```bash
# Add to your ~/.bashrc or ~/.zshrc
export METADATA_CONFIG_PATH="/path/to/your/metadata.yml"
export DATA_FOLDER="/path/to/your/data/"
export PYTHONPATH="${PYTHONPATH}:/path/to/contract_inspect"
```

### Ollama Configuration

If you need to use a different Ollama endpoint:

```bash
# Edit src/core/config.py
vim src/core/config.py

# Update LLM_CONFIG:
LLM_CONFIG = {
    "provider": "ollama",
    "model": "llama3.2",
    "api_endpoint": "http://your-ollama-host:11434"  # Change this
}
```

### Weaviate Configuration

To use an external Weaviate instance:

```bash
# Edit src/sp_adapters/weaviate_adapter.py
# Update the connect() method to use your Weaviate URL
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues

```bash
# If python3.12 not found
which python3.12  # Check if installed
python3 --version  # Check default version

# Use python3 if 3.12 is default
python3 -m venv env
```

#### 2. Permission Denied (Docker)

```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Or use sudo temporarily
sudo docker compose -f compose-files/compose-weaviate.yml up -d
```

#### 3. Port Already in Use

```bash
# Check what's using port 8080
sudo lsof -i :8080

# Stop conflicting services or change Weaviate port
# Edit compose-files/compose-weaviate.yml to use different port
```

#### 4. Ollama Connection Failed

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama if not running
ollama serve &

# Check if models are available
ollama list

# Test Ollama directly
curl http://localhost:11434/api/version
```

#### 5. Weaviate Connection Timeout

```bash
# Check Weaviate logs
docker logs weaviate

# Restart Weaviate
docker compose -f compose-files/compose-weaviate.yml restart

# Check if Weaviate is healthy
curl http://localhost:8080/v1/.well-known/ready
```

#### 6. Import Errors

```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in development mode
pip install -e .
```

### Performance Optimization

#### For Large Document Sets

1. **Increase Weaviate Memory**:
   ```yaml
   # In compose-files/compose-weaviate.yml, add:
   environment:
     LIMIT_RESOURCES: 'false'
   deploy:
     resources:
       limits:
         memory: 8G
   ```

2. **Use SSD Storage**:
   ```yaml
   # Mount to SSD location
   volumes:
     - /path/to/ssd/weaviate_data:/var/lib/weaviate
   ```

3. **Tune Batch Sizes**:
   ```python
   # In index_invoker.py, adjust batch_size
   index_lib.store_data_in_vector_db(
       content_extractor.get_processed_content(),
       WEAVIATE_SCHEMA["class"],
       batch_size=50  # Reduce for limited memory
   )
   ```

### Getting Help

If you encounter issues not covered here:

1. Check the main [Troubleshooting](TROUBLESHOOTING.md) guide
2. Search existing GitHub issues
3. Create a new issue with:
   - Your OS and Python version
   - Complete error messages
   - Steps to reproduce
   - Output of verification commands

## Next Steps

After successful installation:

1. Read the [Architecture Guide](ARCHITECTURE.md) to understand the system
2. Check the [Configuration Guide](CONFIGURATION.md) for advanced settings
3. Try the [Examples](EXAMPLES.md) to learn common usage patterns
4. See the [API Documentation](API.md) for integration details