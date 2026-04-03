# 🚀 Migration Guide: Ollama to vLLM

This guide outlines the necessary steps to transition your LLM-Orchestrator from the lightweight **Ollama** engine to the high-performance **vLLM** engine.

---

## 🏗️ 1. Hardware Requirements

Unlike Ollama, which can run on a CPU, **vLLM strictly requires an NVIDIA GPU** with CUDA support.

- **GPU**: NVIDIA (e.g., RTX 3090, 4090, A100, etc.)
- **VRAM**:
  - 7B models: 12GB - 16GB
  - 13B models: 24GB+
  - 70B models: 80GB+ (or multi-GPU setup)
- **Software**: `nvidia-container-toolkit` must be installed on the host machine.

---

## ⚙️ 2. Configuration Changes

### A. Docker Compose
Modify the `include` section in your main `docker-compose.yml`:

```diff
include:
- - path: ollama.fragment.yml
+ # - path: ollama.fragment.yml
+ - path: vllm.fragment.yml
```

### B. Environment Variables (`.env`)
Update your `.env` file to point the services to the vLLM engine (internal Docker network):

```env
# Change this:
AI_ENGINE_URL=http://vllm:8000/v1/chat/completions
OLLAMA_BASE_URL=http://vllm:8000
```

---

## 🛠️ 3. Full Service Patching (Critical)

To fully ignore Ollama and use vLLM's OpenAI-standard API for model discovery, both the **AI Gateway** and **Chat Service** logic must be updated.

### 📄 Update AI Gateway (`ai/routes.py`)
Replace the tag fetch code in the `list_models` function to use the `/v1/models` endpoint:

```python
# In ai/routes.py around line 170:
v1_url = OLLAMA_BASE_URL.rstrip('/') + '/v1/models'
resp = requests.get(v1_url, timeout=5)
if resp.status_code == 200:
    vllm_models = resp.json().get('data', [])
    for m in vllm_models:
        mid = m['id']
        models_list.append({
            "name": f"models/{mid}",
            "displayName": f"vLLM: {mid}",
            "capabilities": ["generateContent"]
        })
```

### 📄 Update Chat Service (`chat/llm_client.py`)
Update the `list_available_models` function to parse the vLLM backend correctly:

```python
# In chat/llm_client.py around line 150:
resp = requests.get(f'{OLLAMA_BASE}/v1/models', timeout=10)
resp.raise_for_status()
vllm_models = resp.json().get('data', [])

models_list = []
for m in vllm_models:
    mid = m['id']
    # Skip models that are obviously for embeddings (optional filter)
    if any(k in mid.lower() for k in ['embed', 'minilm', 'arctic', 'sentence']):
        continue

    models_list.append({
        "name": f"models/{mid}",
        "displayName": f"vLLM: {mid}",
        "id": mid
    })
```

---

## 📦 4. Customizing Your Model

Modify the `command` section in `vllm.fragment.yml` to specify which model vLLM should load from HuggingFace.

```yaml
# vllm.fragment.yml
command: >
  --model mistralai/Mistral-7B-Instruct-v0.3
  --max-model-len 4096
  --gpu-memory-utilization 0.9
```

> **Note**: If you use a gated model (like Llama 3), you must add your `HF_TOKEN` to the `.env` file.

---

## 🚀 5. Deployment

Once all changes are applied, rebuild and restart the stack:

```bash
docker compose down
docker compose up -d --build ai chat
```

### Verification Steps:
1.  **Logs**: Check if the model is loading correctly: `docker logs -f llm_orchestrator_vllm`.
2.  **API**: Test the discovery endpoint: `curl http://localhost/api/ai/models`.
3.  **UI**: Refresh the Chat UI and check the model selection dropdown.

---

## ❓ Frequently Asked Questions

**Q: Can I run both Ollama and vLLM?**
A: Yes. If you have enough VRAM, you can run both simultaneously, but you will need separate `BASE_URL` variables for each service if you want discovery to work across both.

**Q: Why is my vLLM container crashing?**
A: Most commonly this is due to **Out of Memory (OOM)**. Try reducing `--gpu-memory-utilization` to `0.7` or `0.8`, or decrease `--max-model-len`.

---

## ⚡ Key Differences: Ollama vs. vLLM

Understanding these fundamental differences is crucial for a successful migration:

| Feature | Ollama | vLLM |
| :--- | :--- | :--- |
| **Model Management** | Dynamic swapping (can load many models on disk). | Static loading (serves **one base model** per instance). |
| **GPU Aggression** | Only uses VRAM when the model is active. | Dedicates ~90% of GPU VRAM persistently for throughput. |
| **Multi-Model Support** | **Yes** (automatic swapping). | **No** (requires multiple containers or **Multi-LoRA**). |
| **Embedding Models** | Native and lightweight (can run on CPU). | Primarily designed for generative LLMs (Chat/Instruct). |

> **💡 Best Practice**: For production RAG setups, it is often recommended to keep **Ollama** running specifically for your **Embedding models** (like `nomic-embed-text`) while using **vLLM** as the primary engine for your **Chat models** (like `Llama-3`).
