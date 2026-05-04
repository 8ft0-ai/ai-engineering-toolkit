Yes. For OpenCode, I would consider **Cerebras, Groq, Google Gemini API, OpenRouter Free Router, GitHub Models, Cloudflare Workers AI, Hugging Face Router, SambaNova Cloud, and possibly Z.ai direct**. I would not treat all of them equally, though. The key filters are: OpenAI-compatible API, reliable tool calling, enough context, stable free tier, and predictable model selection.

## Best additions to consider

| Priority | Endpoint                                      | Use with OpenCode                                      | Why                                                                                                                                                                                                                                                                                                                              |
| -------: | --------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|        1 | **Cerebras Inference**                        | Fast fallback / review / small build tasks             | Cerebras has a free tier, OpenAI-style `/v1/chat/completions`, and very fast hosted models such as `gpt-oss-120b`; however, its docs currently note reduced free-tier limits for some high-demand models and upcoming deprecations for some older models. ([Cerebras][1])                                                        |
|        2 | **Groq**                                      | Fast fallback, especially for simple code/review tasks | Groq has a documented free plan with model-specific RPM/RPD/TPM limits, including `llama-3.3-70b-versatile`, `moonshotai/kimi-k2-instruct`, `qwen/qwen3-32b`, and `openai/gpt-oss-*`. The free limits are usable but token ceilings can be tight for large OpenCode sessions. ([GroqCloud][2])                                   |
|        3 | **Google Gemini API**                         | Keep as cheap/free long-context fallback               | Google’s Gemini Developer API has a free tier with free input/output tokens for eligible models, but free-tier content may be used to improve Google products. It is already in your config, so I would refine rather than add it. ([Google AI for Developers][3])                                                               |
|        4 | **OpenRouter Free Router**                    | Experimental fallback only                             | `openrouter/free` is a free router with 200k context that filters for requested capabilities such as tool calling and structured outputs, but it chooses among free models rather than giving you fully deterministic model choice. That is useful for experimentation, not ideal as a daily OpenCode default. ([OpenRouter][4]) |
|        5 | **GitHub Models**                             | Very good for experiments if your account has quota    | GitHub Models exposes a model catalogue with capabilities, including streaming and tool-calling metadata, and every account receives some included free but rate-limited usage. This is promising for OpenCode because the catalogue exposes whether a model supports tool calling. ([GitHub Docs][5])                           |
|        6 | **Cloudflare Workers AI**                     | Low-cost/free small-model fallback                     | Cloudflare Workers AI has OpenAI-compatible chat completions and a free daily allocation of 10,000 neurons. It is useful for lightweight tasks, but the free allocation is modest for agentic coding loops. ([Cloudflare Docs][6])                                                                                               |
|        7 | **Hugging Face Router / Inference Providers** | Broad experimental router                              | Hugging Face’s Inference Providers include a free tier, many backend providers, and an OpenAI-compatible chat-completions endpoint at the router level. It is useful for testing many models, but I would not make it your primary OpenCode path without model-specific smoke tests. ([Hugging Face][7])                         |
|        8 | **SambaNova Cloud**                           | Trial-credit testing                                   | SambaNova has a free tier / no-payment-method mode and also currently advertises $5 free API credits, but that is more of a trial-credit setup than a long-term free default. ([SambaNova Documentation][8])                                                                                                                     |
|        9 | **Z.ai direct**                               | Worth checking for GLM Flash models                    | Z.ai’s pricing page currently lists `GLM-4.7-Flash` and `GLM-4.5-Flash` as free. This could be interesting, but I would test tool-calling carefully because you already found GLM-family tool-call compatibility reports. ([Z.AI Documentation][9])                                                                              |

## My practical recommendation

Add **Cerebras** and **GitHub Models** first. You already have Groq, Google, and OpenRouter in your config, so those mostly need cleanup and model selection rather than new providers.

I would test in this order:

```text
Cerebras gpt-oss-120b
Groq moonshotai/kimi-k2-instruct
Groq llama-3.3-70b-versatile
Google gemini-2.5-flash
GitHub Models: a tool-calling coding-capable model from the catalogue
OpenRouter openrouter/free
Cloudflare llama-3.3/3.1 models
Hugging Face router
Z.ai GLM-4.7-Flash
```

For your specific OpenCode use case, I would avoid making any random-router endpoint the default. Deterministic model choice matters when debugging tool-call behaviour.

## Suggested additions to your config

### Cerebras

```jsonc
"cerebras": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Cerebras Inference",
  "options": {
    "baseURL": "https://api.cerebras.ai/v1",
    "apiKey": "{env:CEREBRAS_API_KEY}",
    "timeout": 600000,
    "chunkTimeout": 90000
  },
  "models": {
    "gpt-oss-120b": {
      "name": "GPT OSS 120B on Cerebras"
    },
    "llama3.1-8b": {
      "name": "Llama 3.1 8B on Cerebras"
    }
  }
}
```

### GitHub Models

GitHub’s model catalogue is API-driven, so I would first list models available to your account and choose ones with `tool-calling` in their capabilities. GitHub’s catalogue endpoint returns model IDs, supported modalities, limits, rate-limit tier, and capabilities such as `streaming` and `tool-calling`. ([GitHub Docs][5])

```jsonc
"github-models": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "GitHub Models",
  "options": {
    "baseURL": "https://models.github.ai/inference",
    "apiKey": "{env:GITHUB_TOKEN}",
    "timeout": 600000,
    "chunkTimeout": 90000
  },
  "models": {
    "openai/gpt-4.1": {
      "name": "GPT-4.1 via GitHub Models"
    }
  }
}
```

Treat the model list above as a placeholder until you query your own GitHub Models catalogue, because availability and quota depend on account access.

### Cloudflare Workers AI

```jsonc
"cloudflare-ai": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Cloudflare Workers AI",
  "options": {
    "baseURL": "https://api.cloudflare.com/client/v4/accounts/{env:CLOUDFLARE_ACCOUNT_ID}/ai/v1",
    "apiKey": "{env:CLOUDFLARE_API_TOKEN}",
    "timeout": 600000,
    "chunkTimeout": 90000
  },
  "models": {
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast": {
      "name": "Llama 3.3 70B on Cloudflare"
    },
    "@cf/meta/llama-3.1-8b-instruct-fp8-fast": {
      "name": "Llama 3.1 8B on Cloudflare"
    }
  }
}
```

### Hugging Face Router

```jsonc
"huggingface": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Hugging Face Router",
  "options": {
    "baseURL": "https://router.huggingface.co/v1",
    "apiKey": "{env:HF_TOKEN}",
    "timeout": 600000,
    "chunkTimeout": 90000
  },
  "models": {
    "openai/gpt-oss-120b": {
      "name": "GPT OSS 120B via Hugging Face Router"
    }
  }
}
```

Hugging Face’s router is a drop-in OpenAI-compatible endpoint for chat completions, but model/provider availability can vary by account, provider, and quota. ([Hugging Face][10])

## What I would change in your current provider set

Keep:

```text
nvidia-openai
google
groq
openrouter
ollama
litellm
```

Add:

```text
cerebras
github-models
cloudflare-ai
huggingface
```

Maybe add later:

```text
sambanova
z-ai
```

I would not prioritise **Fireworks** or **Together** as “free online endpoints” unless you are happy with trial credits or model-specific temporary free research quotas; they are useful services, but less attractive than Cerebras/Groq/Gemini/OpenRouter/GitHub for a no-cost OpenCode rotation.

## Best role assignment

For OpenCode specifically, I would use:

```text
Daily default:          NVIDIA Step 3.5 Flash
Heavy fallback:         NVIDIA Mistral Large 3
Fast fallback:          Cerebras gpt-oss-120b
Cheap/fast fallback:    Groq llama-3.3-70b-versatile or kimi-k2-instruct
Long-context fallback:  Google Gemini 2.5 Flash
Experimental router:    OpenRouter openrouter/free
Catalogue testing:      GitHub Models
Small/light tasks:      Cloudflare Workers AI
```

The big caution is privacy: Google’s free Gemini tier explicitly says content is used to improve products, and Mistral’s Experiment plan help page also says API requests under that plan may be used to train Mistral’s models. Do not send private repo content to those free tiers unless that is acceptable for your project. ([Google AI for Developers][3])

[1]: https://www.cerebras.ai/pricing?utm_source=chatgpt.com "Cerebras"
[2]: https://console.groq.com/docs/rate-limits?utm_source=chatgpt.com "Rate Limits - GroqDocs"
[3]: https://ai.google.dev/gemini-api/docs/pricing?utm_source=chatgpt.com "Gemini Developer API pricing  |  Gemini API  |  Google AI for Developers"
[4]: https://openrouter.ai/openrouter/free?utm_source=chatgpt.com "Free Models Router - API Pricing & Providers | OpenRouter"
[5]: https://docs.github.com/en/rest/models/catalog?utm_source=chatgpt.com "REST API endpoints for models catalog - GitHub Docs"
[6]: https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/?utm_source=chatgpt.com "OpenAI compatible API endpoints · Cloudflare Workers AI docs"
[7]: https://huggingface.co/docs/inference-providers/en/index?utm_source=chatgpt.com "Inference Providers · Hugging Face"
[8]: https://docs.sambanova.ai/cloud/docs/models/rate-limits?utm_source=chatgpt.com "Rate Limits Policy - SambaNova Documentation"
[9]: https://docs.z.ai/guides/overview/pricing?utm_source=chatgpt.com "Pricing - Overview - Z.AI DEVELOPER DOCUMENT"
[10]: https://huggingface.co/docs/api-inference/main/en?utm_source=chatgpt.com "Inference Providers"
