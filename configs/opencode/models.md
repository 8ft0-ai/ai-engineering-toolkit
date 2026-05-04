That’s a much better result. Your revised probe is now separating the free models into genuinely useful buckets for **OpenCode agentic/tool use**, rather than just “responded at all”. 

The main takeaways from this run are:

* **Best dedicated coding choice:** `openrouter/qwen/qwen3-coder:free` now works in tool mode, but it is noticeably slower at about **25.18 seconds**. It still ranks highest by your scoring, so it looks like the strongest “quality first” default from the models that actually worked. 
* **Best fast practical default:** `openrouter/nvidia/nemotron-3-nano-30b-a3b:free` worked in **4.11 seconds** with a strong score, which makes it the best “daily driver” option if you care about responsiveness. 
* **Strong alternatives:** `openrouter/openai/gpt-oss-120b:free`, `openrouter/nvidia/nemotron-3-super-120b-a12b:free`, `openrouter/nvidia/nemotron-nano-9b-v2:free`, and `openrouter/openai/gpt-oss-20b:free` all worked in tool mode and look viable. 
* **Still not practical for you right now:** `qwen3-next-80b-a3b-instruct`, the two Gemma 4 models, and `llama-3.3-70b-instruct` all timed out even with a **90 second** timeout, so I would not use them as defaults. 
* **Not suitable for OpenCode agent mode in your current path:** the Gemma 3 family, Dolphin Mistral Venice, Liquid models, Llama 3.2 3B, and Hermes 3 all failed with **“No endpoints found that support tool use”**, which means they are not currently usable for this OpenCode tool-capable workflow. 
* **Odd one out:** `openrouter/nvidia/nemotron-nano-12b-v2-vl:free` failed with an `unknown` outcome rather than a timeout or tool-use error, so that one is worth a one-off manual check if you care about it. 

Based on your **actual measured results**, I would use this set:

* `model`: `openrouter/qwen/qwen3-coder:free`
* `small_model`: `openrouter/nvidia/nemotron-3-nano-30b-a3b:free`

And keep these available as manual switches:

* `openrouter/openai/gpt-oss-120b:free`
* `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
* `openrouter/nvidia/nemotron-nano-9b-v2:free`
* `openrouter/openai/gpt-oss-20b:free` 

I’d set your config like this:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "enabled_providers": ["openrouter"],

  "model": "openrouter/qwen/qwen3-coder:free",
  "small_model": "openrouter/nvidia/nemotron-3-nano-30b-a3b:free",

  "permission": {
    "edit": "ask",
    "bash": "ask"
  },

  "provider": {
    "openrouter": {
      "options": {
        "apiKey": "{env:OPENROUTER_API_KEY}",
        "timeout": 600000,
        "chunkTimeout": 90000
      },
      "models": {
        "qwen/qwen3-coder:free": {},
        "nvidia/nemotron-3-nano-30b-a3b:free": {},
        "openai/gpt-oss-120b:free": {},
        "nvidia/nemotron-3-super-120b-a12b:free": {},
        "nvidia/nemotron-nano-9b-v2:free": {},
        "openai/gpt-oss-20b:free": {},
        "z-ai/glm-4.5-air:free": {},
        "arcee-ai/trinity-large-preview:free": {}
      }
    }
  }
}
```


My practical recommendation is:

* use **Qwen3 Coder** when you want the best coding quality and can tolerate slower starts
* use **Nemotron 3 Nano 30B A3B** as the day-to-day fast default
* use **GPT-OSS 120B** as your “try another strong reasoning/coding model” fallback

The one thing your latest run also proved is that the free pool is volatile: earlier, some of these timed out; in this run, several of them succeeded. So the script is doing exactly the right job now: it is measuring what is usable **right now**, not what should work in theory.


