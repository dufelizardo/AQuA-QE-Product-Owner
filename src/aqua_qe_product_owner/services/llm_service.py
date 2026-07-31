import json
import os

import ollama
from openai import OpenAI

_DEFAULT_MODEL = "mistral"
_DEFAULT_REVIEW_MODEL = "phi4"
_DEFAULT_NVIDIA_MODEL = "deepseek-ai/deepseek-v4-pro"
_DEFAULT_NVIDIA_REVIEW_MODEL = "meta/llama-3.3-70b-instruct"
_NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
# Fallback documentado se deepseek-v4-pro saturar por capacidade (mesma família do
# deepseek-v4-flash, que saturou no piloto original do agente irmão AQuA-QE Product
# Manager): openai/gpt-oss-120b, confirmado acessível na mesma conta NVIDIA — mas com
# status "Preview"/sem garantia lá. Motivou avaliar a Cerebras e o Google AI Studio como
# provedores alternativos (ver LLM_PROVIDER=cerebras|google abaixo).

_DEFAULT_CEREBRAS_MODEL = "gpt-oss-120b"
_DEFAULT_CEREBRAS_REVIEW_MODEL = "zai-glm-4.7"
_CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"

# Modelos confirmados pelo usuário no dashboard do Google AI Studio, os mesmos já
# validados ao vivo com sucesso nos agentes irmãos AQuA-QE Product Manager/Solution
# Architect (Solution Design real gerado de ponta a ponta sem erro). gemini-3.1-flash-lite
# (gerador) e gemini-2.5-flash-lite (revisor, variante menor/mais rápida) — mesma família
# Gemini nos dois papéis (Google AI Studio não oferece modelos de terceiros como
# NVIDIA/Cerebras oferecem), mitigação de self-preference bias mais fraca aqui do que nos
# outros provedores, mas ainda são checkpoints/tiers distintos. gemini-3.5-flash foi
# testado primeiro no SA, mas o tier gratuito tem quota de só 20 requisições/dia para esse
# modelo especificamente — esgotada rapidamente pelo pipeline (~10 chamadas por geração).
# Outros fallbacks documentados pelo usuário, ainda não testados: gemma-4-26b, gemma-4-31b.
_DEFAULT_GOOGLE_MODEL = "gemini-3.1-flash-lite"
_DEFAULT_GOOGLE_REVIEW_MODEL = "gemini-2.5-flash-lite"
_GOOGLE_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# Sem isso, a resposta vem truncada em conteúdo real mais rico (achado ao vivo no SA,
# processando um PRD real de verdade) — o default de max_tokens da API do Google é
# pequeno demais para esse tipo de agente. Aplicado a qualquer modelo Google, não
# chaveado por modelo (ainda sem dados de tuning por modelo, diferente do NVIDIA).
_GOOGLE_DEFAULT_PARAMS: dict = {"max_tokens": 8192}

# Adicionado ao vivo processando o PRD real "Mais Saúde Pública" no PO — os 3 provedores
# em nuvem anteriores (NVIDIA/Cerebras/Google) saturaram ou tiveram rate limit baixo demais
# (15 ou 5 req/min no tier gratuito do Google) para gerar 5 stories em lote (~30 chamadas em
# rajada). Groq confirmado pelo usuário com 30 req/min tanto no gerador quanto no revisor —
# folga bem maior que qualquer tier gratuito do Google testado. gpt-oss-120b como revisor
# (família diferente de llama, mesmo princípio de mitigar self-preference bias).
_DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
_DEFAULT_GROQ_REVIEW_MODEL = "openai/gpt-oss-120b"
_GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Parâmetros de sampling recomendados pela NVIDIA por modelo NIM (build.nvidia.com/playground)
# — chaveados por nome do modelo, não por papel (gerador/revisor), para continuar corretos se
# um dos dois for trocado via NVIDIA_MODEL/NVIDIA_REVIEW_MODEL. Modelo sem entrada aqui usa a
# chamada sem parâmetros extras (só model/messages/response_format).
_NVIDIA_MODEL_PARAMS: dict[str, dict] = {
    "deepseek-ai/deepseek-v4-flash": {
        "temperature": 1,
        "top_p": 0.95,
        "max_tokens": 16384,
        "extra_body": {"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}},
    },
}


def _nvidia_params(modelo: str) -> dict:
    return dict(_NVIDIA_MODEL_PARAMS.get(modelo, {}))


def _provider() -> str:
    return os.getenv("LLM_PROVIDER", "ollama")


def _ollama_client() -> ollama.Client:
    host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ollama.Client(host=host)


def _nvidia_client() -> OpenAI:
    return OpenAI(base_url=_NVIDIA_BASE_URL, api_key=os.environ["NVIDIA_API_KEY"])


def _cerebras_client() -> OpenAI:
    return OpenAI(base_url=_CEREBRAS_BASE_URL, api_key=os.environ["CEREBRAS_API_KEY"])


def _google_client() -> OpenAI:
    return OpenAI(base_url=_GOOGLE_BASE_URL, api_key=os.environ["GOOGLE_API_KEY"])


def _groq_client() -> OpenAI:
    return OpenAI(base_url=_GROQ_BASE_URL, api_key=os.environ["GROQ_API_KEY"])


def generator_model() -> str:
    """Resolve o modelo gerador conforme o provedor ativo (LLM_PROVIDER=ollama|nvidia|cerebras|google|groq)."""
    if _provider() == "nvidia":
        return os.getenv("NVIDIA_MODEL", _DEFAULT_NVIDIA_MODEL)
    if _provider() == "cerebras":
        return os.getenv("CEREBRAS_MODEL", _DEFAULT_CEREBRAS_MODEL)
    if _provider() == "google":
        return os.getenv("GOOGLE_MODEL", _DEFAULT_GOOGLE_MODEL)
    if _provider() == "groq":
        return os.getenv("GROQ_MODEL", _DEFAULT_GROQ_MODEL)
    return os.getenv("OLLAMA_MODEL", _DEFAULT_MODEL)


def reviewer_model() -> str:
    """Resolve o modelo revisor conforme o provedor ativo (LLM_PROVIDER=ollama|nvidia|cerebras|google|groq)."""
    if _provider() == "nvidia":
        return os.getenv("NVIDIA_REVIEW_MODEL", _DEFAULT_NVIDIA_REVIEW_MODEL)
    if _provider() == "cerebras":
        return os.getenv("CEREBRAS_REVIEW_MODEL", _DEFAULT_CEREBRAS_REVIEW_MODEL)
    if _provider() == "google":
        return os.getenv("GOOGLE_REVIEW_MODEL", _DEFAULT_GOOGLE_REVIEW_MODEL)
    if _provider() == "groq":
        return os.getenv("GROQ_REVIEW_MODEL", _DEFAULT_GROQ_REVIEW_MODEL)
    return os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)


def _chat(modelo: str, messages: list[dict], json_mode: bool) -> str:
    provider = _provider()
    if provider in ("nvidia", "cerebras", "google", "groq"):
        if provider == "nvidia":
            kwargs = _nvidia_params(modelo)
        elif provider == "google":
            kwargs = dict(_GOOGLE_DEFAULT_PARAMS)
        else:
            kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        if provider == "nvidia":
            cliente = _nvidia_client()
        elif provider == "cerebras":
            cliente = _cerebras_client()
        elif provider == "google":
            cliente = _google_client()
        else:
            cliente = _groq_client()
        resposta = cliente.chat.completions.create(model=modelo, messages=messages, **kwargs)
        return resposta.choices[0].message.content

    kwargs = {"format": "json"} if json_mode else {}
    resposta = _ollama_client().chat(model=modelo, messages=messages, **kwargs)
    return resposta["message"]["content"]


def complete(prompt: str, system: str = "", model: str | None = None) -> str:
    """Envia um prompt ao provedor de LLM ativo (Ollama ou provedor em nuvem) e retorna o texto de resposta."""
    modelo = model or generator_model()
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    return _chat(modelo, messages, json_mode=False)


def complete_json(prompt: str, system: str = "", model: str | None = None) -> dict:
    """Envia um prompt ao provedor de LLM ativo e retorna a resposta já parseada como JSON.

    Usa `raw_decode` em vez de `json.loads` — aceita o primeiro objeto JSON válido e ignora
    qualquer lixo depois dele (achado ao vivo no SA: o Gemini às vezes devolve um objeto JSON
    válido seguido de chaves de fechamento extras, mesmo com response_format=json_object).
    Continua rejeitando qualquer coisa que não comece com JSON válido, inclusive JSON truncado.
    Também rejeita um JSON tecnicamente válido mas que não seja um objeto (`{...}`) — achado ao
    vivo com gemini-3.5-flash-lite, que às vezes devolve uma lista solta (`[...]`) em vez do
    objeto pedido no prompt; sem essa checagem, cada skill chamadora quebra com um
    AttributeError confuso (`'list' object has no attribute 'get'`) em vez de um erro claro aqui.
    """
    modelo = model or generator_model()
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    conteudo = _chat(modelo, messages, json_mode=True)
    try:
        dados, _ = json.JSONDecoder().raw_decode(conteudo.strip())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Resposta do LLM não é um JSON válido: {conteudo!r}") from exc
    if not isinstance(dados, dict):
        raise ValueError(f"Resposta do LLM não é um objeto JSON: {conteudo!r}")
    return dados
