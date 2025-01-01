from openai import AsyncOpenAI
from app.core.config import settings, OPENAI_CONFIG
from typing import Dict, Any
import time

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_completion(
    prompt: str,
    config_type: str,
    system_message: str = None
) -> Dict[str, Any]:
    start_time = time.time()
    
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})
    
    config = OPENAI_CONFIG[config_type]
    
    try:
        response = await client.chat.completions.create(
            model=config['model'],
            messages=messages,
            temperature=config['temperature'],
            max_tokens=config['max_tokens']
        )
        
        processing_time = time.time() - start_time
        
        return {
            "content": response.choices[0].message.content,
            "metadata": {
                "processingTime": processing_time,
                "tokenUsage": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
        }
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}") 