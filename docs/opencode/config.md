I would rewrite it as a **NVIDIA-free-endpoint-first config**, with Qwen3-Coder kept out of the daily-driver path. OpenCode supports JSONC, `model`, `small_model`, `provider`, and `default_agent`, and `default_agent` must be a primary agent; its agent system also lets you define primary agents and subagents with per-agent permissions. ([OpenCode][1])

The key changes are: use `stepfun-ai/step-3.5-flash` as the default, keep `mistralai/mistral-large-3-675b-instruct-2512` as the heavy model, use `z-ai/glm-4.7` mainly for review/fallback, keep Qwen3-Coder out of normal use because vLLM documents Qwen3-Coder as requiring a `qwen3_xml` tool-call parser, and keep MiniMax experimental because there are public reports of malformed repeated tool names. ([Hugging Face][2])

Here is the rewrite I would use:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  // Daily-driver defaults.
  // Keep this on a model that is less likely to leak raw tool-call syntax.
  "model": "nvidia-openai/stepfun-ai/step-3.5-flash",
  "small_model": "nvidia-openai/nvidia/nemotron-mini-4b-instruct",
  "default_agent": "build",

  // Conservative global defaults. Individual agents can loosen or tighten these.
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "webfetch": "ask",
    "question": "allow"
  },

  "provider": {
    "nvidia-openai": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA NIM Free",
      "options": {
        "baseURL": "https://integrate.api.nvidia.com/v1",
        "apiKey": "{env:NVIDIA_API_KEY}",
        "timeout": 600000,
        "chunkTimeout": 90000
      },
      "models": {
        // Recommended default
        "stepfun-ai/step-3.5-flash": {
          "name": "Step 3.5 Flash",
          "limit": {
            "context": 256000,
            "output": 65536
          }
        },

        // Heavy reasoning / large refactors
        "mistralai/mistral-large-3-675b-instruct-2512": {
          "name": "Mistral Large 3 675B",
          "limit": {
            "context": 262144,
            "output": 65536
          }
        },

        // Useful fallback / review model, but not my first default
        "z-ai/glm-4.7": {
          "name": "GLM 4.7",
          "limit": {
            "context": 200000,
            "output": 65536
          }
        },

        // Function-calling-oriented fallback to test
        "mistralai/mistral-nemotron": {
          "name": "Mistral Nemotron",
          "limit": {
            "context": 128000,
            "output": 65536
          }
        },

        // Small helper model from your free endpoint list
        "nvidia/nemotron-mini-4b-instruct": {
          "name": "Nemotron Mini 4B",
          "limit": {
            "context": 8192,
            "output": 4096
          }
        },

        // Larger free helper from OpenRouter/NVIDIA-style lists; keep as optional
        "nvidia/nemotron-3-nano-30b-a3b": {
          "name": "Nemotron 3 Nano 30B A3B",
          "limit": {
            "context": 128000,
            "output": 65536
          }
        },

        // Quarantined: strong model, but risky on NVIDIA NIM/OpenCode until tool parsing is fixed
        "qwen/qwen3-coder-480b-a35b-instruct": {
          "name": "Qwen3 Coder 480B A35B — tool-call parser risk",
          "limit": {
            "context": 262144,
            "output": 65536
          }
        },

        // Experimental only: public reports of repeated/malformed tool names
        "minimaxai/minimax-m2.7": {
          "name": "MiniMax M2.7 — experimental",
          "limit": {
            "context": 200000,
            "output": 65536
          }
        }
      }
    },

    // Keep LiteLLM available, but do not make it the default while debugging NIM tool behaviour.
    // If your LiteLLM proxy is configured without /v1 and already works, keep your existing URL.
    "litellm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LiteLLM",
      "options": {
        "baseURL": "http://localhost:4000/v1",
        "apiKey": "{env:LITELLM_MASTER_KEY}",
        "timeout": 600000,
        "chunkTimeout": 90000
      },
      "models": {
        // These should match LiteLLM model aliases in your litellm_config.yaml.
        "opencode-build": {
          "name": "OpenCode Build via LiteLLM"
        },
        "opencode-heavy": {
          "name": "OpenCode Heavy via LiteLLM"
        },
        "opencode-review": {
          "name": "OpenCode Review via LiteLLM"
        },
        "qwen2.5-coder:7b": {
          "name": "Qwen2.5 Coder 7B Local via LiteLLM"
        }
      }
    },

    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Local",
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "timeout": 600000,
        "chunkTimeout": 90000
      },
      "models": {
        "qwen2.5-coder:7b": {
          "name": "Qwen2.5 Coder 7B Local"
        }
      }
    },

    // Keep OpenRouter only for explicitly selected backup/free models.
    // I would not route daily OpenCode work through this unless the direct NVIDIA path is down.
    "openrouter": {
      "options": {
        "apiKey": "{env:OPENROUTER_API_KEY}",
        "timeout": 600000,
        "chunkTimeout": 90000
      },
      "models": {
        "nvidia/nemotron-3-nano-30b-a3b:free": {
          "name": "Nemotron 3 Nano 30B A3B Free"
        },
        "nvidia/nemotron-nano-9b-v2:free": {
          "name": "Nemotron Nano 9B v2 Free"
        },
        "openai/gpt-oss-120b:free": {
          "name": "GPT OSS 120B Free"
        },
        "openai/gpt-oss-20b:free": {
          "name": "GPT OSS 20B Free"
        },
        "z-ai/glm-4.5-air:free": {
          "name": "GLM 4.5 Air Free"
        }
      }
    }
  },

  "agent": {
    // Main day-to-day coding agent.
    // Step 3.5 Flash is the default because it has strong external coding/agent benchmark evidence
    // and fewer obvious OpenCode tool-call complaints than Qwen/MiniMax.
    "build": {
      "description": "Default coding agent for normal repository work.",
      "mode": "primary",
      "model": "nvidia-openai/stepfun-ai/step-3.5-flash",
      "temperature": 0.2,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "webfetch": "ask",
        "question": "allow"
      }
    },

    // Use when the default model gets stuck, or for larger design/refactor reasoning.
    "heavy": {
      "description": "Use for harder reasoning, larger refactors, or difficult debugging.",
      "mode": "primary",
      "model": "nvidia-openai/mistralai/mistral-large-3-675b-instruct-2512",
      "temperature": 0.15,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "webfetch": "ask",
        "question": "allow"
      }
    },

    // Read-only-ish review agent.
    "review": {
      "description": "Review code and suggest changes without editing files.",
      "mode": "subagent",
      "model": "nvidia-openai/z-ai/glm-4.7",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask",
        "webfetch": "ask",
        "question": "allow"
      }
    },

    // Fallback if Step has latency or behaviour issues.
    "fallback": {
      "description": "Alternative primary coding agent when the default model misbehaves.",
      "mode": "primary",
      "model": "nvidia-openai/mistralai/mistral-nemotron",
      "temperature": 0.2,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "webfetch": "ask",
        "question": "allow"
      }
    },

    // Local-only escape hatch for small edits or offline work.
    "local": {
      "description": "Local Ollama coding agent for small tasks and offline experiments.",
      "mode": "primary",
      "model": "ollama/qwen2.5-coder:7b",
      "temperature": 0.2,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "webfetch": "deny",
        "question": "allow"
      }
    },

    // Keep Qwen available only as an explicit manual test.
    // Do not use this as the default unless the tool-call parser path is fixed.
    "qwen-nim-test": {
      "description": "Manual test agent for Qwen3-Coder on NVIDIA NIM; avoid for normal tool-heavy sessions.",
      "mode": "primary",
      "model": "nvidia-openai/qwen/qwen3-coder-480b-a35b-instruct",
      "temperature": 0.2,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "webfetch": "ask",
        "question": "allow"
      }
    },

    // MiniMax has promising capability, but the malformed-tool-name reports make it unsuitable as default.
    "minimax-test": {
      "description": "Manual test agent for MiniMax M2.7; use only for smoke tests until tool calls prove reliable.",
      "mode": "primary",
      "model": "nvidia-openai/minimaxai/minimax-m2.7",
      "temperature": 0.2,
      "permission": {
        "edit": "ask",
        "bash": "ask",
        "webfetch": "ask",
        "question": "allow"
      }
    }
  }
}
```

I intentionally removed **DeepSeek V4**, **Devstral 2**, **Kimi K2 Thinking**, and several older/deprecating entries from the main provider list because your pasted free-endpoint list marked several of those as near-deprecation, while your current goal is a stable free setup rather than a broad model catalogue. 

Two details worth noting. First, I changed the LiteLLM base URL to `http://localhost:4000/v1` because OpenCode’s OpenAI-compatible examples use `/v1`, and AI SDK/OpenAI-compatible endpoints normally expose `/v1/chat/completions`; keep `http://localhost:4000` only if your current LiteLLM proxy already works that way. ([OpenCode][3]) Second, I kept LiteLLM in the file but did not route the default through it, because while LiteLLM is useful for a unified OpenAI-format proxy, routing Qwen through LiteLLM will not itself fix Qwen’s custom parser issue. ([docs.litellm.ai][4])

[1]: https://opencode.ai/docs/config/?utm_source=chatgpt.com "Config | OpenCode"
[2]: https://huggingface.co/stepfun-ai/Step-3.5-Flash-FP8?utm_source=chatgpt.com "stepfun-ai/Step-3.5-Flash-FP8 · Hugging Face"
[3]: https://opencode.ai/docs/providers/?utm_source=chatgpt.com "Providers | OpenCode"
[4]: https://docs.litellm.ai/?utm_source=chatgpt.com "liteLLM"
