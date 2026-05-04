# OpenCode Direct vs LiteLLM

## Current setup

Your existing OpenCode direct providers remain unchanged.

LiteLLM is configured as an optional extra provider, not your default path.

Current routed LiteLLM models:

- `litellm/qwen2.5-coder:7b`
- `litellm/qwen/qwen3-coder-480b-a35b-instruct`
- `litellm/gemini-2.5-flash`

These are available through the `litellm` provider in `~/.config/opencode/opencode.jsonc`.

## Usage pattern

Use direct providers when:

- you want the fewest moving parts
- you want provider-native behavior
- you are debugging provider-specific issues
- you do not need the LiteLLM proxy layer

Use `litellm/...` when:

- you want one stable proxy endpoint
- you want local and hosted models to feel uniform
- you want LiteLLM UI/admin visibility
- you want optional routed behavior without changing your normal defaults

## Practical rule

- Direct = default path
- LiteLLM = optional proxy path

## Recommended routed models

Fast local coding:

- `litellm/qwen2.5-coder:7b`

Strong hosted coding through proxy:

- `litellm/qwen/qwen3-coder-480b-a35b-instruct`

Fast general-purpose routed model:

- `litellm/gemini-2.5-flash`

## Naming convention

Keep direct models exactly as provider/model.

Keep routed models as `litellm/<model-name>`.

Current routed names are explicit and should stay as-is unless shorter aliases become necessary.

## LiteLLM notes

LiteLLM is currently healthy for:

- `qwen2.5-coder:7b`
- `qwen/qwen3-coder-480b-a35b-instruct`
- `gemini-2.5-flash`

The previous DeepSeek routed alias was removed.

## Simple decision guide

If you want simplicity and reliability, use direct providers.

If you want routing, proxy visibility, or a unified endpoint, use `litellm/...`.
