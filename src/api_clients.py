"""
API clients for LLM providers (Ollama, Gemini, OpenAI/ChatGPT, Grok)
All cloud providers use the same OpenAI-compatible interface where possible.
"""

import time
import logging
import os
from typing import Tuple, Optional
from abc import ABC, abstractmethod

import config

try:
    import openai
except ImportError:
    openai = None

logger = logging.getLogger(__name__)

class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1500) -> Tuple[str, dict]:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> dict:
        """Get model information"""
        pass


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client"""
    
    def __init__(self, base_url: str = config.OLLAMA_BASE_URL, 
                 model: str = config.OLLAMA_DEFAULT_MODEL,
                 timeout: int = config.OLLAMA_TIMEOUT):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.provider = "ollama"
    
    def generate(self, prompt: str, max_tokens: int = 1500) -> Tuple[str, dict]:
        """Generate text using Ollama"""
        try:
            if not openai:
                raise ImportError("openai package not installed")
            
            # Minimal client initialization - no timeout or proxies
            client = openai.OpenAI(api_key="ollama", base_url=self.base_url)
            
            start_time = time.time()
            
            # Create request with sensible defaults
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                'model': self.model,
                'provider': self.provider,
                'tokens': {
                    'prompt': len(prompt.split()),
                    'completion': len(response.choices[0].message.content.split()),
                    'total': len(prompt.split()) + len(response.choices[0].message.content.split()),
                },
                'processing_time_ms': processing_time,
                'success': True,
            }
            
            logger.info(f"Ollama generation successful ({processing_time}ms)")
            return response.choices[0].message.content, result
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            result = {
                'provider': self.provider,
                'success': False,
                'error': str(e),
            }
            return None, result
    
    def get_model_info(self) -> dict:
        """Get Ollama model information"""
        return {
            'provider': self.provider,
            'model': self.model,
            'base_url': self.base_url,
            'features': ['free', 'local', 'no_quota', 'offline'],
        }
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            if not openai:
                return False
            
            # Simple connectivity check without creating full client
            import http.client
            conn = http.client.HTTPConnection("localhost", 11434, timeout=2)
            conn.request("GET", "/api/tags")
            response = conn.getresponse()
            available = response.status == 200
            conn.close()
            return available
            
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            return False


class GeminiClient(BaseLLMClient):
    """Google Gemini API client"""
    
    def __init__(self, api_key: str = config.GEMINI_API_KEY, 
                 model: str = config.GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self.provider = "gemini"
    
    def generate(self, prompt: str, max_tokens: int = 1500) -> Tuple[str, dict]:
        """Generate text using Gemini"""
        try:
            import google.generativeai as genai

            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not set")

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                self.model,
                generation_config=genai.GenerationConfig(max_output_tokens=max_tokens),
            )

            start_time = time.time()
            response = model.generate_content(prompt)
            processing_time = int((time.time() - start_time) * 1000)

            prompt_tokens = 0
            completion_tokens = 0
            try:
                prompt_tokens = response.usage_metadata.prompt_token_count
                completion_tokens = response.usage_metadata.candidates_token_count
            except Exception:
                prompt_tokens = len(prompt.split())
                completion_tokens = len(response.text.split())

            result = {
                'model': self.model,
                'provider': self.provider,
                'tokens': {
                    'prompt': prompt_tokens,
                    'completion': completion_tokens,
                    'total': prompt_tokens + completion_tokens,
                },
                'processing_time_ms': processing_time,
                'success': True,
            }

            logger.info(f"Gemini generation successful ({processing_time}ms)")
            return response.text, result

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            result = {
                'provider': self.provider,
                'success': False,
                'error': str(e),
            }
            return None, result

    def is_available(self) -> bool:
        """Check if Gemini is configured"""
        return bool(self.api_key)

    def get_model_info(self) -> dict:
        """Get Gemini model information"""
        return {
            'provider': self.provider,
            'model': self.model,
            'features': ['cloud', 'fast', 'high_quality', 'has_quota'],
        }


class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: str = config.OPENAI_API_KEY,
                 model: str = config.OPENAI_MODEL):
        self.api_key = api_key
        self.model = model
        self.provider = "openai"
    
    def generate(self, prompt: str, max_tokens: int = 1500) -> Tuple[str, dict]:
        """Generate text using OpenAI"""
        try:
            if not openai:
                raise ImportError("openai package not installed")
            
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not set")
            
            # Minimal client initialization
            client = openai.OpenAI(api_key=self.api_key)
            
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                'model': self.model,
                'provider': self.provider,
                'tokens': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens,
                },
                'processing_time_ms': processing_time,
                'success': True,
            }
            
            logger.info(f"OpenAI generation successful ({processing_time}ms)")
            return response.choices[0].message.content, result
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            result = {
                'provider': self.provider,
                'success': False,
                'error': str(e),
            }
            return None, result
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.api_key)

    def get_model_info(self) -> dict:
        """Get OpenAI model information"""
        return {
            'provider': self.provider,
            'model': self.model,
            'features': ['cloud', 'fast', 'highest_quality', 'paid'],
        }


class GrokClient(BaseLLMClient):
    """xAI Grok API client — OpenAI-compatible endpoint"""

    def __init__(self, api_key: str = config.XAI_API_KEY,
                 model: str = config.GROK_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = config.GROK_BASE_URL
        self.provider = "grok"

    def generate(self, prompt: str, max_tokens: int = 2000) -> Tuple[str, dict]:
        """Generate text using Grok"""
        try:
            if not openai:
                raise ImportError("openai package not installed")
            if not self.api_key:
                raise ValueError("XAI_API_KEY not set")

            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

            start_time = time.time()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=max_tokens,
            )
            processing_time = int((time.time() - start_time) * 1000)

            result = {
                'model': self.model,
                'provider': self.provider,
                'tokens': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens,
                },
                'processing_time_ms': processing_time,
                'success': True,
            }

            logger.info(f"Grok generation successful ({processing_time}ms)")
            return response.choices[0].message.content, result

        except Exception as e:
            logger.error(f"Grok error: {e}")
            return None, {'provider': self.provider, 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        return bool(self.api_key)

    def get_model_info(self) -> dict:
        return {
            'provider': self.provider,
            'model': self.model,
            'base_url': self.base_url,
            'features': ['cloud', 'fast', 'reasoning', 'paid'],
        }


class LLMClientFactory:
    """Factory for creating LLM clients"""

    _REGISTRY = {
        'ollama': OllamaClient,
        'gemini': GeminiClient,
        'openai': OpenAIClient,
        'grok': GrokClient,
    }

    @staticmethod
    def create(provider: str) -> Optional[BaseLLMClient]:
        cls = LLMClientFactory._REGISTRY.get(provider.lower())
        if not cls:
            logger.warning(f"Unknown provider: {provider}")
            return None
        try:
            return cls()
        except Exception as e:
            logger.error(f"Failed to create client for {provider}: {e}")
            return None

    @staticmethod
    def get_available_providers() -> list:
        """Return status info for all known providers."""
        checks = [
            {
                'cls': OllamaClient,
                'name': 'Ollama (Local)',
                'provider': 'ollama',
                'unavailable_reason': 'Ollama not running — start with: ollama serve',
            },
            {
                'cls': GeminiClient,
                'name': 'Gemini (Google)',
                'provider': 'gemini',
                'unavailable_reason': 'Set GEMINI_API_KEY in your .env file',
            },
            {
                'cls': OpenAIClient,
                'name': 'ChatGPT (OpenAI)',
                'provider': 'openai',
                'unavailable_reason': 'Set OPENAI_API_KEY in your .env file',
            },
            {
                'cls': GrokClient,
                'name': 'Grok (xAI)',
                'provider': 'grok',
                'unavailable_reason': 'Set XAI_API_KEY in your .env file',
            },
        ]

        results = []
        for check in checks:
            try:
                client = check['cls']()
                available = client.is_available()
                entry = {
                    'name': check['name'],
                    'provider': check['provider'],
                    'available': available,
                }
                if available:
                    entry['info'] = client.get_model_info()
                else:
                    entry['reason'] = check['unavailable_reason']
                results.append(entry)
            except Exception as e:
                results.append({
                    'name': check['name'],
                    'provider': check['provider'],
                    'available': False,
                    'reason': f'Error: {e}',
                })

        return results


if __name__ == "__main__":
    for p in LLMClientFactory.get_available_providers():
        status = "✓" if p['available'] else "✗"
        print(f"{status} {p['name']}")
