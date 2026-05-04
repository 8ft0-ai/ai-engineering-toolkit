I would use **Devstral 2 or GLM 4.7 as your main OpenCode model**, not Qwen3-Coder on NVIDIA NIM.

My practical ranking for your NVIDIA set is:

|          Rank | Model                                     | Best OpenCode role                                | Verdict                                          |
| ------------: | ----------------------------------------- | ------------------------------------------------- | ------------------------------------------------ |
|             1 | `mistralai/devstral-2-123b-instruct-2512` | Default build/edit model                          | Best first replacement                           |
|             2 | `z-ai/glm-4.7`                            | Stable fallback or default if Devstral misbehaves | Very sensible for OpenCode                       |
|             3 | `moonshotai/kimi-k2-thinking`             | Planning, architecture, debugging analysis        | Use as plan/review, not edit-heavy default       |
|             4 | `deepseek-ai/deepseek-v4-flash`           | Long-context read-only analysis                   | Useful, but I would avoid for edit loops for now |
|             5 | `deepseek-ai/deepseek-v4-pro`             | Heavy reasoning / long-context analysis           | Powerful, but risky for OpenCode tool loops      |
|             6 | `minimaxai/minimax-m2.7`                  | Experimental agentic fallback                     | Worth testing, not my default                    |
| Avoid for now | `qwen/qwen3-coder-480b-a35b-instruct`     | —                                                 | Your exact failure mode is known                 |

## Why I would start with Devstral 2

NVIDIA describes **Devstral 2 123B** as an agentic software-engineering model that excels at using tools to explore codebases, editing multiple files, and powering software-engineering agents. That maps directly to OpenCode’s read/search/edit loop. NVIDIA’s catalog also labels it as a code model with deep reasoning and 256k context. ([build.nvidia.com][1])

I would use this as your first default:

```jsonc
"model": "nvidia-openai/mistralai/devstral-2-123b-instruct-2512"
```

## Why GLM 4.7 is the best fallback

NVIDIA describes **GLM-4.7** as a multilingual agentic coding partner with stronger reasoning, tool use and UI skills. ([build.nvidia.com][2]) Z.AI also has explicit OpenCode integration documentation that tells users to select models such as GLM-4.7 through OpenCode, which is a good signal that this model family is intended for this style of workflow. ([Z.AI][3])

I would keep it as your “reliability fallback”, and possibly make it your default if Devstral has latency or tool-call issues in your environment:

```jsonc
"model": "nvidia-openai/z-ai/glm-4.7"
```

## Where Kimi K2 Thinking fits

**Kimi K2 Thinking** looks better suited to planning than direct file editing. NVIDIA describes it as an open reasoning model with a 256k context window and enhanced tool use. ([build.nvidia.com][4]) I would use it for OpenCode’s `plan` agent or for architecture/debugging review, not as the model that performs most edits.

## Why I would be cautious with DeepSeek V4

DeepSeek V4 looks very attractive on paper: NVIDIA says **DeepSeek V4 Pro** has 1.6T total parameters and 49B active parameters, while **V4 Flash** has 284B total and 13B active parameters; both support 1M-token context, and Flash is aimed at higher-speed workloads. ([NVIDIA Developer][5]) However, there is a very recent NVIDIA Developer Forum report saying DeepSeek V4 Pro and Flash have streaming tool-call compatibility issues on NVIDIA NIM via the OpenAI-compatible endpoint. The report says MiniMax worked in the same test setup while DeepSeek did not continue correctly after tool calls. ([NVIDIA Developer Forums][6])

So I would use DeepSeek V4 Flash for **long-context analysis**, not as the OpenCode build/edit model.

## Why I would not default to MiniMax M2.7

MiniMax M2.7 is intended for complex software engineering and agentic tool use, according to NVIDIA’s model page. ([build.nvidia.com][7]) But there are recent reports of NVIDIA NIM MiniMax M2.7 producing invalid repeated tool names such as `search_filessearch_files`, `read_fileread_file`, and `terminalterminal`. ([NVIDIA Developer Forums][8])

It may work in some clients, but for OpenCode I would treat it as experimental until you have tested a few sessions with real file reads, edits, and terminal commands.

## Suggested OpenCode config

This is the setup I would try first:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  "model": "nvidia-openai/mistralai/devstral-2-123b-instruct-2512",
  "small_model": "nvidia-openai/z-ai/glm-4.7",

  "provider": {
    "nvidia-openai": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA NIM",
      "options": {
        "baseURL": "https://integrate.api.nvidia.com/v1",
        "apiKey": "{env:NVIDIA_API_KEY}",
        "timeout": 600000,
        "chunkTimeout": 90000
      },
      "models": {
        "mistralai/devstral-2-123b-instruct-2512": {
          "name": "Devstral 2 123B",
          "limit": {
            "context": 262144,
            "output": 65536
          }
        },
        "z-ai/glm-4.7": {
          "name": "GLM 4.7",
          "limit": {
            "context": 131072,
            "output": 65536
          }
        },
        "moonshotai/kimi-k2-thinking": {
          "name": "Kimi K2 Thinking",
          "limit": {
            "context": 262144,
            "output": 65536
          }
        },
        "deepseek-ai/deepseek-v4-flash": {
          "name": "DeepSeek V4 Flash",
          "limit": {
            "context": 1000000,
            "output": 65536
          }
        },
        "deepseek-ai/deepseek-v4-pro": {
          "name": "DeepSeek V4 Pro",
          "limit": {
            "context": 1000000,
            "output": 65536
          }
        },
        "minimaxai/minimax-m2.7": {
          "name": "MiniMax M2.7",
          "limit": {
            "context": 1000000,
            "output": 65536
          }
        }
      }
    }
  },

  "agent": {
    "build": {
      "model": "nvidia-openai/mistralai/devstral-2-123b-instruct-2512",
      "temperature": 0.2
    },
    "plan": {
      "model": "nvidia-openai/moonshotai/kimi-k2-thinking",
      "temperature": 0.1
    },
    "review": {
      "description": "Review code and propose changes without editing files.",
      "mode": "subagent",
      "model": "nvidia-openai/z-ai/glm-4.7",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "long-context": {
      "description": "Analyse large files, logs, traces, or repository context without editing.",
      "mode": "subagent",
      "model": "nvidia-openai/deepseek-ai/deepseek-v4-flash",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    }
  }
}
```

OpenCode supports configuring `provider`, `model` and `small_model` in config, and it also supports specialised agents with their own models and permissions. ([OpenCode][9])

## The short recommendation

Use this order:

1. **Default:** `mistralai/devstral-2-123b-instruct-2512`
2. **Fallback/default alternative:** `z-ai/glm-4.7`
3. **Planning:** `moonshotai/kimi-k2-thinking`
4. **Long-context read-only work:** `deepseek-ai/deepseek-v4-flash`
5. **Avoid for now:** `qwen/qwen3-coder-480b-a35b-instruct` on NVIDIA NIM for OpenCode tool-heavy sessions

That gives you the best chance of avoiding the raw `<tool_call>` and malformed streaming-tool problems while still staying entirely on NVIDIA NIM.

[1]: https://build.nvidia.com/mistralai/devstral-2-123b-instruct-2512/modelcard?utm_source=chatgpt.com "devstral-2-123b-instruct-2512 Model by Mistral AI"
[2]: https://build.nvidia.com/z-ai/glm-4.7?utm_source=chatgpt.com "glm-4.7 Model by Z-ai"
[3]: https://docs.z.ai/devpack/tool/opencode?utm_source=chatgpt.com "OpenCode - Overview - Z.AI DEVELOPER DOCUMENT"
[4]: https://build.nvidia.com/moonshotai/kimi-k2-thinking?utm_source=chatgpt.com "kimi-k2-thinking Model by Moonshotai"
[5]: https://developer.nvidia.com/blog/build-with-deepseek-v4-using-nvidia-blackwell-and-gpu-accelerated-endpoints/ "Build with DeepSeek V4 Using NVIDIA Blackwell and GPU-Accelerated Endpoints | NVIDIA Technical Blog"
[6]: https://forums.developer.nvidia.com/t/deepseek-v4-pro-v4-flash-on-nvidia-nim-streaming-tool-calls-do-not-continue-in-claude-code-anthropic-compatible-agent-workflow/368085 "DeepSeek V4 Pro / V4 Flash on NVIDIA NIM: streaming tool calls do not continue in Claude Code / Anthropic-compatible agent workflow - Models - NVIDIA Developer Forums"
[7]: https://build.nvidia.com/minimaxai/minimax-m2.7/modelcard?utm_source=chatgpt.com "minimax-m2.7 Model by Minimaxai | NVIDIA NIM"
[8]: https://forums.developer.nvidia.com/t/minimax-m2-7-error/366423?utm_source=chatgpt.com "Minimax-M2.7 Error - Models"
[9]: https://opencode.ai/docs/config/?utm_source=chatgpt.com "Config"

---

Yes — if you want to stay on **free NVIDIA NIM endpoints**, I would narrow the set quite aggressively.

NVIDIA says Developer Program members get free access to NVIDIA-hosted NIM API endpoints for development and testing, and the model catalogue currently exposes a **Free Endpoint** filter. ([NVIDIA Developer][1])

## Best free NVIDIA models for OpenCode

| Priority | Model                                     | Use in OpenCode                 | Why                                                                                                                                                                                  |
| -------: | ----------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|        1 | `mistralai/devstral-2-123b-instruct-2512` | Default build/edit model        | Best fit for agentic coding; NVIDIA lists it as a free endpoint and describes it as a state-of-the-art open code model with deep reasoning and 256k context. ([build.nvidia.com][2]) |
|        2 | `z-ai/glm-4.7`                            | Fallback default / review model | NVIDIA lists it as a free endpoint and describes it as having stronger reasoning, tool use and UI skills. ([build.nvidia.com][3])                                                    |
|        3 | `minimaxai/minimax-m2.7`                  | Experimental fallback           | Free endpoint, strong on paper for coding/reasoning, but I would not make it default because of recent tool-call reliability reports. ([build.nvidia.com][3])                        |
|        4 | `nvidia/nemotron-3-nano-30b-a3b`          | Small/cheap helper model        | Free endpoint in NVIDIA’s catalogue; useful as a small model or review helper, not necessarily the main editor. ([build.nvidia.com][4])                                              |
|        5 | `mistralai/magistral-small-2506`          | Reasoning subagent              | Free endpoint and coding-tagged, but less obviously suited to file-edit loops than Devstral. ([build.nvidia.com][2])                                                                 |

I would **exclude** these from a free-only OpenCode config unless the catalogue explicitly shows “Free Endpoint” for your account:

| Model                                 | Reason                                                                                                   |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `qwen/qwen3-coder-480b-a35b-instruct` | Listed as downloadable, and you already saw tool-call parser failures.                                   |
| `deepseek-ai/deepseek-v4-flash`       | Listed as downloadable, not free endpoint in the catalogue result I found. ([build.nvidia.com][3])       |
| `deepseek-ai/deepseek-v4-pro`         | Same issue: downloadable, not free endpoint in the catalogue result. ([build.nvidia.com][3])             |
| `moonshotai/kimi-k2-thinking`         | I did not find a current official free-endpoint signal for this one.                                     |
| `mistralai/mistral-small-4-119b-2603` | Free endpoint, but currently marked for deprecation soon in the Mistral listing. ([build.nvidia.com][2]) |
| `mistralai/mistral-nemotron`          | Function-calling friendly, but also marked for deprecation soon. ([build.nvidia.com][2])                 |

## Free-only OpenCode config I would try

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  "model": "nvidia-openai/mistralai/devstral-2-123b-instruct-2512",
  "small_model": "nvidia-openai/nvidia/nemotron-3-nano-30b-a3b",

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
        "mistralai/devstral-2-123b-instruct-2512": {
          "name": "Devstral 2 123B"
        },
        "z-ai/glm-4.7": {
          "name": "GLM 4.7"
        },
        "minimaxai/minimax-m2.7": {
          "name": "MiniMax M2.7"
        },
        "nvidia/nemotron-3-nano-30b-a3b": {
          "name": "Nemotron 3 Nano 30B A3B"
        },
        "mistralai/magistral-small-2506": {
          "name": "Magistral Small 2506"
        }
      }
    }
  },

  "agent": {
    "build": {
      "model": "nvidia-openai/mistralai/devstral-2-123b-instruct-2512",
      "temperature": 0.2
    },
    "review": {
      "description": "Review code and propose changes without editing files.",
      "mode": "subagent",
      "model": "nvidia-openai/z-ai/glm-4.7",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "fallback": {
      "description": "Alternative coding model when the default model has tool or latency issues.",
      "mode": "primary",
      "model": "nvidia-openai/minimaxai/minimax-m2.7",
      "temperature": 0.2
    },
    "reason": {
      "description": "Reason about bugs, designs, and plans before implementation.",
      "mode": "subagent",
      "model": "nvidia-openai/mistralai/magistral-small-2506",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    }
  }
}
```

## My final recommendation

Use this order:

1. **Default:** `mistralai/devstral-2-123b-instruct-2512`
2. **Fallback/default alternative:** `z-ai/glm-4.7`
3. **Experimental fallback:** `minimaxai/minimax-m2.7`
4. **Small helper:** `nvidia/nemotron-3-nano-30b-a3b`
5. **Reasoning-only helper:** `mistralai/magistral-small-2506`

Before relying on a model, confirm the NVIDIA page for that exact model still says **Free Endpoint**. NVIDIA’s catalogue labels are changing quickly, and some free Mistral endpoints are already marked for deprecation.

[1]: https://developer.nvidia.com/nim "NIM for Developers | NVIDIA Developer"
[2]: https://build.nvidia.com/mistralai "AI Models by Mistral AI | Try NVIDIA NIM APIs"
[3]: https://build.nvidia.com/models "Try NVIDIA NIM APIs"
[4]: https://build.nvidia.com/nvidia?utm_source=chatgpt.com "AI Models by NVIDIA | Try NVIDIA NIM APIs"

---

You are right. Re-ranking this on external evidence, not NVIDIA catalogue blurbs, I would **not** put GLM 4.7 first any more. I would make **Step 3.5 Flash** your first serious test, then **Mistral Large 3**, then **GLM 4.7**.

I used your pasted list only to constrain the candidates to current **free endpoints**; it shows the relevant free LLM-style options include `glm-4.7`, `minimax-m2.7`, `step-3.5-flash`, `mistral-large-3-675b-instruct-2512`, `qwen3-coder-480b-a35b-instruct`, `mistral-nemotron`, `llama-4-maverick-17b-128e-instruct`, `dracarys-llama-3.1-70b-instruct`, and some smaller/helper models. 

## Recommendation

| Rank | Model                                          | Use with OpenCode                  | Why I rank it there                                                                                                                                                                                                                                                                                                              |
| ---: | ---------------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|    1 | `stepfun-ai/step-3.5-flash`                    | Main default candidate             | Best mix of agentic benchmark evidence and low apparent compatibility noise. StepFun’s Hugging Face card claims strong agent/coding results, including **74.4% SWE-bench Verified** and **51.0% Terminal-Bench 2.0**, which are much more relevant to OpenCode than generic chat scores. ([Hugging Face][1])                     |
|    2 | `mistralai/mistral-large-3-675b-instruct-2512` | Heavy reasoning / larger refactors | Strong general model evidence, but likely slower. Mistral says Large 3 is 675B total / 41B active and ranked highly on LMArena among open models; a community OpenCode+NVIDIA test also called Mistral Large 3 the best reasoning model but noted it was slow on the free tier. ([Mistral AI][2])                                |
|    3 | `z-ai/glm-4.7`                                 | Fallback default, not first choice | Strong model family for agentic coding, but there are several OpenCode/tool-call issue reports: tool calls inside reasoning tags, malformed thinking blocks, and object-parameter parsing issues. ([GitHub][3])                                                                                                                  |
|    4 | `mistralai/mistral-nemotron`                   | Experimental fallback              | It is plausibly designed for tool/function calling, but I found much less OpenCode-specific evidence than for Step/Mistral/GLM. I would test it, but not lead with it.                                                                                                                                                           |
|    5 | `minimaxai/minimax-m2.7`                       | Avoid unless testing               | Recent reports show malformed repeated tool names such as `read_fileread_file`, `terminalterminal`, and `search_filessearch_files`, which is exactly the sort of failure that breaks OpenCode sessions. ([NVIDIA Developer Forums][4])                                                                                           |
|    6 | `qwen/qwen3-coder-480b-a35b-instruct`          | Avoid on NVIDIA NIM/OpenCode       | The model is excellent on coding benchmarks when served with the right parser, but your observed raw `<tool_call>` failure matches known parser-path problems. vLLM’s Qwen3-Coder recipe explicitly uses a special `qwen3_coder` tool-call parser, which is the missing piece in many OpenAI-compatible proxy paths. ([vLLM][5]) |
|    7 | `llama-4-maverick-17b-128e-instruct`           | Low-priority fallback              | Llama 4 can support tool calling, but there are OpenCode/NVIDIA reports of some Llama models emitting `<tool_call>` text instead of actual tool calls. That is too close to the issue you are trying to avoid. ([GitHub][6])                                                                                                     |

## Config I would try first

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  "model": "nvidia-openai/stepfun-ai/step-3.5-flash",
  "small_model": "nvidia-openai/nvidia/nemotron-mini-4b-instruct",

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
        "stepfun-ai/step-3.5-flash": {
          "name": "Step 3.5 Flash"
        },
        "mistralai/mistral-large-3-675b-instruct-2512": {
          "name": "Mistral Large 3 675B"
        },
        "z-ai/glm-4.7": {
          "name": "GLM 4.7"
        },
        "mistralai/mistral-nemotron": {
          "name": "Mistral Nemotron"
        },
        "minimaxai/minimax-m2.7": {
          "name": "MiniMax M2.7"
        },
        "nvidia/nemotron-mini-4b-instruct": {
          "name": "Nemotron Mini 4B"
        }
      }
    }
  },

  "agent": {
    "build": {
      "model": "nvidia-openai/stepfun-ai/step-3.5-flash",
      "temperature": 0.2
    },
    "heavy": {
      "description": "Use for difficult reasoning, larger refactors, or when the default model gets stuck.",
      "mode": "primary",
      "model": "nvidia-openai/mistralai/mistral-large-3-675b-instruct-2512",
      "temperature": 0.15
    },
    "review": {
      "description": "Review code and suggest changes without editing files.",
      "mode": "subagent",
      "model": "nvidia-openai/z-ai/glm-4.7",
      "temperature": 0.1,
      "permission": {
        "edit": "deny",
        "bash": "ask"
      }
    },
    "fallback": {
      "description": "Alternative coding model if Step 3.5 Flash has latency or tool-call problems.",
      "mode": "primary",
      "model": "nvidia-openai/mistralai/mistral-nemotron",
      "temperature": 0.2
    }
  }
}
```

## Why this differs from my earlier answer

The stronger external evidence pushed **Step 3.5 Flash** up. Its published agentic benchmarks are directly relevant to terminal/code-agent tasks, especially SWE-bench Verified and Terminal-Bench 2.0. ([Hugging Face][1]) I also found fewer direct OpenCode compatibility complaints for Step 3.5 Flash than for GLM, MiniMax, Qwen or some Llama paths.

I moved **GLM 4.7 down** because the OpenCode issue tracker and Hugging Face discussions contain multiple concrete tool-call parsing complaints. GLM may still be good, but for your specific need — reliable OpenCode tools — those reports matter more than catalogue claims. ([GitHub][3])

I kept **Mistral Large 3** high because independent/community OpenCode testing found it usable and strong for reasoning, but the same test reported very slow response time for it on NVIDIA, so I would not make it the everyday default unless you value quality over speed. ([Reddit][7])

My final testing order would be:

```text
stepfun-ai/step-3.5-flash
mistralai/mistral-large-3-675b-instruct-2512
z-ai/glm-4.7
mistralai/mistral-nemotron
minimaxai/minimax-m2.7
```

For the smoke test, ask OpenCode to read two files, search for a symbol, make a tiny edit in a scratch file, run a harmless command, then revert the edit. Any model that prints `<tool_call>` or repeats tool names should be removed from your default rotation immediately.

[1]: https://huggingface.co/stepfun-ai/Step-3.5-Flash "stepfun-ai/Step-3.5-Flash · Hugging Face"
[2]: https://mistral.ai/news/mistral-3 "Introducing Mistral 3 | Mistral AI"
[3]: https://github.com/anomalyco/opencode/issues/6708 "GLM 4.7 on Zai coding plan puts tool calls inside the thinking/reasoning tag. · Issue #6708 · anomalyco/opencode · GitHub"
[4]: https://forums.developer.nvidia.com/t/minimax-m2-7-error/366423 "Minimax-M2.7 Error - Models - NVIDIA Developer Forums"
[5]: https://docs.vllm.ai/projects/recipes/en/latest/Qwen/Qwen3-Coder-480B-A35B.html "Qwen3-Coder Usage Guide - vLLM Recipes"
[6]: https://github.com/anomalyco/opencode/issues/10885 "NVIDIA connector is experiencing CRITICAL issues · Issue #10885 · anomalyco/opencode · GitHub"
[7]: https://www.reddit.com/r/opencodeCLI/comments/1s6444s/i_tested_20_models_on_opencode_nvidia_nim_so_you/ "I tested 20+ models on OpenCode + NVIDIA NIM so you don’t have to (Benchmarks & \"What actually works\") : r/opencodeCLI"
