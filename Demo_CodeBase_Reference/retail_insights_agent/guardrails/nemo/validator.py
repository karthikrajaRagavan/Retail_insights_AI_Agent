import re
import logging
import asyncio
from typing import Optional
from dataclasses import dataclass

from nemoguardrails import LLMRails, RailsConfig

from .config import RAILS_YAML, RAILS_COLANG, BLOCK_PATTERNS
from ...config import GUARDRAILS_BLOCKED_MESSAGE

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    allowed: bool
    message: str
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {"allowed": self.allowed, "message": self.message, "reason": self.reason}


class InputValidator:
    def __init__(self):
        self._patterns = [re.compile(p) for p in BLOCK_PATTERNS]

    def _quick_pattern_check(self, query: str) -> Optional[str]:
        for pattern in self._patterns:
            if pattern.search(query):
                return f"Blocked by pattern: {pattern.pattern}"
        return None

    def _create_rails(self) -> LLMRails:
        return LLMRails(
            RailsConfig.from_content(
                colang_content=RAILS_COLANG,
                yaml_content=RAILS_YAML,
            )
        )

    async def check_async(self, query: str) -> ValidationResult:
        pattern_match = self._quick_pattern_check(query)
        if pattern_match:
            logger.info(f"Query blocked by pattern: {query[:50]}...")
            return ValidationResult(
                allowed=False,
                message=GUARDRAILS_BLOCKED_MESSAGE,
                reason=pattern_match,
            )

        try:
            rails = self._create_rails()
            result = await rails.generate_async(
                messages=[{"role": "user", "content": query}],
                options={"rails": ["input"]}
            )

            logger.info(f"Guardrail result type: {type(result)}, attrs: {dir(result)}")

            response = ""
            if hasattr(result, 'response') and result.response:
                if isinstance(result.response, list) and len(result.response) > 0:
                    response = result.response[0].get("content", "") if isinstance(result.response[0], dict) else str(result.response[0])
                elif isinstance(result.response, str):
                    response = result.response

            if not response and hasattr(result, 'output') and result.output:
                response = str(result.output)

            log_blocked = False
            if hasattr(result, 'log') and result.log:
                log_str = str(result.log).lower()
                if "bot refuse" in log_str or "refuse to respond" in log_str:
                    log_blocked = True

            logger.info(f"Guardrail response: '{response[:100] if response else 'empty'}', log_blocked: {log_blocked}")

            is_blocked = False

            if log_blocked:
                is_blocked = True
            elif response:
                response_lower = response.lower()
                if (response.startswith("I can only help with") or
                    response.startswith("I can help with sales analytics") or
                    "cannot help" in response_lower or
                    "not able to" in response_lower or
                    "outside my scope" in response_lower):
                    is_blocked = True

            if is_blocked:
                logger.info(f"Query BLOCKED by LLM guardrail: {query[:50]}...")
                return ValidationResult(
                    allowed=False,
                    message=GUARDRAILS_BLOCKED_MESSAGE,
                    reason="Policy violation - LLM guardrail",
                )

            logger.info(f"Query ALLOWED by guardrail: {query[:50]}...")
            return ValidationResult(allowed=True, message=query)

        except Exception as e:
            logger.error(f"Guardrail check failed: {e}")
            return ValidationResult(
                allowed=True,
                message=query,
                reason=f"Guardrail error (fail-open): {str(e)}",
            )

    def check(self, query: str) -> ValidationResult:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.check_async(query))
                return future.result(timeout=30)
        except RuntimeError:
            return asyncio.run(self.check_async(query))


def validate_query(query: str) -> ValidationResult:
    validator = InputValidator()
    return validator.check(query)
