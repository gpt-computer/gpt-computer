#!/bin/bash

# gpt-computer-style OpenClaw route setup
# Works on: macOS, Linux, Windows (WSL/Git Bash/MSYS2)
# Usage: curl -fsSL https://raw.githubusercontent.com/gpt-computer/gpt-computer/main/scripts/setup-openclaw.sh | bash -s -- <POLLINATIONS_API_KEY>

set -e

if [ -z "$1" ]; then
  echo "No API key provided. Proceeding without an API key."
  API_KEY=""
else
  API_KEY="$1"
fi

if ! command -v python >/dev/null 2>&1; then
  echo "Python not found. Please install Python 3.10+ first."
  exit 1
fi

if ! python -m gptc --help >/dev/null 2>&1; then
  echo "gptc not installed. Installing with pip..."
  python -m pip install -U gptc[all]
fi

CONFIG_DIR="${HOME}/.gptc/cookies"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"
ENV_FILE="${CONFIG_DIR}/.env"

mkdir -p "${CONFIG_DIR}"

cat > "${CONFIG_FILE}" <<'EOF'
models:
  - name: "openclaw"
    providers:
      - provider: "GeminiCLI"
        model: "gemini-3-flash-preview"
        condition: "quota.models.gemini-3-flash-preview.remainingFraction > 0 and error_count < 3"
      - provider: "Antigravity"
        model: "gemini-3-flash"
        condition: "quota.models.gemini-3-flash.quotaInfo.remainingFraction > 0 and error_count < 3"
      - provider: "PollinationsAI"
        model: "openai"
        condition: "balance > 0 or error_count < 3"
EOF

cat > "${ENV_FILE}" <<EOF
POLLINATIONS_API_KEY=${API_KEY}
OPENAI_API_KEY=
GEMINI_API_KEY=
EOF

# OpenClaw onboarding and configuration (if available)
if command -v openclaw >/dev/null 2>&1; then
  echo "OpenClaw CLI found. Configuring OpenClaw..."
  OPENCLAW_CONFIG_FILE="${HOME}/.openclaw/openclaw.json"
  mkdir -p "${HOME}/.openclaw"

  if [ ! -f "${OPENCLAW_CONFIG_FILE}" ]; then
    echo "Fresh install — running OpenClaw setup..."
    openclaw onboard \
      --non-interactive \
      --accept-risk \
      --mode local \
      --flow quickstart \
      --auth-choice custom-api-key \
      --custom-base-url "http://localhost:8080/v1" \
      --custom-provider-id gpt-computer \
      --custom-model-id openclaw \
      --custom-api-key "${API_KEY}" \
      --secret-input-mode plaintext \
      --skip-channels \
      --skip-daemon \
      --skip-skills \
      --skip-ui \
      --skip-health \
      2>&1 | grep -v "^$" || true
  else
    echo "OpenClaw config already exists at ${OPENCLAW_CONFIG_FILE}, skipping onboard."
  fi

  echo "Patching OpenClaw provider and model list..."

    echo "using Python to patch OpenClaw config..."
    python - <<PYEOF
import json, sys, os

config_file = os.path.expanduser("~/.openclaw/openclaw.json")

provider = {
    "baseUrl": "http://localhost:8080/v1",
    "api": "openai-completions",
    "models": [
        {
            "id": "openclaw",
            "name": "Custom GPT-Computer",
            "reasoning": True,
            "input": ["text", "image"],
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
            "contextWindow": 256000,
            "maxTokens": 8192,
        }
    ],
}

try:
    with open(config_file) as f:
        cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cfg = {}

cfg.setdefault("models", {})["providers"] = cfg.get("models", {}).get("providers", {})
cfg["models"]["providers"]["gpt-computer"] = provider
cfg["models"]["providers"]["gptc-perplexity"] = {
    "baseUrl": "https://perplexity.gptc-dev.workers.dev",
    "api": "openai-completions",
    "models": [
        {
            "id": "turbo",
            "name": "perplexity"
        }
    ]
}
cfg["tools"] = cfg.get("tools", {})
cfg["tools"]["web"] = cfg["tools"].get("web", {})
cfg["tools"]["web"]["search"] = {
    "provider": "gptc-perplexity",
}

with open(config_file, "w") as f:
    json.dump(cfg, f, indent=2)

print("OpenClaw config patched via Python.")
PYEOF

  # apply models with openclaw commands if available
  openclaw models set gpt-computer/openclaw >/dev/null 2>&1 || true
  openclaw gateway restart >/dev/null 2>&1 || true
else
  echo "OpenClaw CLI not found; skipping OpenClaw setup steps."
fi

printf "\n🚀 OpenClaw route configured in %s\n" "${CONFIG_FILE}"
printf "✅ .env written to %s\n" "${ENV_FILE}"

cat <<'INFO'

Next steps:
  gptc client "Hello OpenClaw" --model openclaw
  or use python:
    from gptc.client import Client
    client = Client()
    resp = client.chat.completions.create(model='openclaw', messages=[{'role':'user','content':'Hello'}])
    print(resp.choices[0].message.content)

Start the server:
  gptc api --debug --port 8080

And auth into Antigravity and GeminiCLI (or any other provider you wish to use).

For more setting options, edit config.yaml and add other providers or condition values.
INFO
