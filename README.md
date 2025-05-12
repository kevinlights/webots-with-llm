# webots-with-llm
Webots with LLM like qwen, deepseek, llama, etc.


## Environment 

- Python3.10
- Webots R2025a
- Ollama


## Run

### Start Ollama

```shell
export OLLAMA_CONTEXT_LENGTH=128000
export OLLAMA_DEBUG=true
export OLLAMA_FLASH_ATTENTION=true

ollama serve
```

The openai API will be avaiable on `http://localhost:11434/v1`

### Pull models

```shell
ollama pull qwen2.5-coder:3b
ollama pull qwen3:4b
```

