"""Vendor-neutral generation contract and the initial Nebius chat adapter."""

import math
import os
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlsplit

import httpx


@dataclass(frozen=True)
class GenerationDiagnostic:
    """Allowlisted diagnostic fields only; never raw model text or exception data."""

    stage: str
    category: str
    statement_index: int | None = None
    evidence_index: int | None = None
    source_id: str | None = None
    quote_characters: int | None = None
    quote_sha256: str | None = None
    matching_source_ids: tuple[str, ...] = ()
    missing_sections: tuple[str, ...] = ()
    http_status: int | None = None
    field_name: str | None = None
    value_type: str | None = None
    item_index: int | None = None
    exception_type: str | None = None  # Allowlisted class name, never exception text.


class GenerationError(ValueError):
    """Sanitized configuration, transport, or model-response failure."""

    def __init__(self, message: str, *, diagnostic: GenerationDiagnostic | None = None):
        super().__init__(message)
        self.diagnostic = diagnostic or GenerationDiagnostic("provider_communication", "provider_error")


class GenerationProvider(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return a JSON response to the grounded-answer contract, or raise."""
        ...


class NebiusGenerationProvider:
    """Verify account model access, then use nonstreaming chat completions.

Model listing does not prove chat compatibility. chat_verified becomes true only
after a successful nonempty completed assistant message; grounded schema validity
is checked separately by KnowledgeService. No credential or response logging.
"""

    def __init__(self, *, model: str | None = None, timeout: float = 45,
                 max_tokens: int = 1800, client: httpx.Client | None = None):
        key = os.getenv("NEBIUS_API_KEY", "").strip()
        if not key:
            raise GenerationError("NEBIUS_API_KEY is required", diagnostic=GenerationDiagnostic("configuration", "missing_credentials"))
        self.model = (model or os.getenv("NEBIUS_GENERATION_MODEL", "")).strip()
        if not self.model:
            raise GenerationError("NEBIUS_GENERATION_MODEL is required", diagnostic=GenerationDiagnostic("configuration", "missing_model"))
        self.base_url = (os.getenv("NEBIUS_BASE_URL") or "https://api.tokenfactory.nebius.com/v1").rstrip("/")
        url = urlsplit(self.base_url)
        if url.scheme != "https" or not url.netloc or url.username or url.password or url.query or url.fragment:
            raise GenerationError("Nebius endpoint must be a credential-free HTTPS URL", diagnostic=GenerationDiagnostic("configuration", "invalid_endpoint"))
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise GenerationError("timeout must be positive and finite", diagnostic=GenerationDiagnostic("configuration", "invalid_timeout"))
        if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens < 1:
            raise GenerationError("max_tokens must be a positive integer", diagnostic=GenerationDiagnostic("configuration", "invalid_output_limit"))
        self.timeout, self.max_tokens = timeout, max_tokens
        self._headers = {"Authorization": f"Bearer {key}"}
        self._client = client or httpx.Client(timeout=timeout, follow_redirects=False)
        self._owns_client = client is None
        self.model_verified = False
        self.chat_verified = False

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _request(self, method: str, path: str, **kwargs):
        try:
            response = self._client.request(method, self.base_url + path, headers=self._headers,
                                            timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            raise GenerationError("Nebius generation request timed out", diagnostic=GenerationDiagnostic("provider_communication", "timeout")) from None
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            raise GenerationError("Nebius generation request failed", diagnostic=GenerationDiagnostic(
                "provider_communication", "authentication_failed" if status in (401, 403) else "http_error", http_status=status,
            )) from None
        except httpx.HTTPError:
            raise GenerationError("Nebius generation transport failed", diagnostic=GenerationDiagnostic("provider_communication", "transport_error")) from None
        except ValueError:
            raise GenerationError("Nebius returned invalid response JSON", diagnostic=GenerationDiagnostic("provider_communication", "invalid_provider_json")) from None

    def verify_model(self) -> None:
        payload = self._request("GET", "/models")
        try:
            rows = payload["data"]
            if not isinstance(rows, list) or any(not isinstance(row, dict) or not isinstance(row.get("id"), str) for row in rows):
                raise TypeError
            available = any(row["id"] == self.model for row in rows)
        except (KeyError, TypeError):
            raise GenerationError("Nebius model-list response is malformed", diagnostic=GenerationDiagnostic("provider_communication", "malformed_model_list")) from None
        if not available:
            raise GenerationError("Configured generation model is unavailable to this account", diagnostic=GenerationDiagnostic("configuration", "model_unavailable"))
        self.model_verified = True

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not system_prompt.strip() or not user_prompt.strip():
            raise GenerationError("Generation prompts must be nonempty", diagnostic=GenerationDiagnostic("configuration", "empty_prompt"))
        if not self.model_verified:
            self.verify_model()
        payload = self._request("POST", "/chat/completions", json={
            "model": self.model, "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ], "temperature": 0, "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"}, "stream": False,
        })
        try:
            choices = payload["choices"]
            if not isinstance(choices, list) or len(choices) != 1:
                raise TypeError
            choice = choices[0]
            message = choice["message"]
            text = message["content"]
            if choice["finish_reason"] == "length":
                raise GenerationError("Nebius chat response was truncated", diagnostic=GenerationDiagnostic("provider_communication", "truncated_response"))
            if (choice["finish_reason"] != "stop" or message.get("role") != "assistant"
                    or message.get("tool_calls") or not isinstance(text, str) or not text.strip()):
                raise TypeError
        except (KeyError, TypeError, IndexError):
            raise GenerationError("Nebius returned an incomplete or malformed chat response", diagnostic=GenerationDiagnostic("provider_communication", "malformed_chat_response")) from None
        self.chat_verified = True
        return text


def create_generation_provider(*, provider: str | None = None, model: str | None = None) -> NebiusGenerationProvider:
    """Only Nebius ships initially; inject any GenerationProvider into the service."""
    name = provider or os.getenv("KNOWLEDGE_GENERATION_PROVIDER", "nebius")
    if name != "nebius":
        raise GenerationError("Unsupported generation provider; supply an explicit provider adapter", diagnostic=GenerationDiagnostic("configuration", "unsupported_provider"))
    return NebiusGenerationProvider(model=model)
