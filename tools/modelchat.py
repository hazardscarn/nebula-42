import os
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass, asdict
import json
import re
from groq import Groq
import openai
import google.generativeai as genai
from anthropic import Anthropic


class UnifiedChatAssistant:
    def __init__(self, model: str = "gpt-4o", system_prompt: str = "You are a helpful assistant", 
                 reasoning_effort: Optional[str] = None, add_history: bool = False):
        """
        Initialize chat assistant with any supported model.
        
        Args:
            model: Model name
            system_prompt: System prompt for the assistant
            reasoning_effort: For Groq reasoning models - "low", "medium", or "high"
            add_history: If True, maintains conversation history. If False, each call is independent.
        """
        self.model = model
        self.system_prompt = system_prompt
        self.reasoning_effort = reasoning_effort
        self.add_history = add_history
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.reasoning_history = []
        
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate API client based on model name"""
        model_lower = self.model.lower()
        
        if "gpt" in model_lower and "/" not in model_lower:
            self.provider = "openai"
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif "gemini" in model_lower:
            self.provider = "gemini"
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.client = genai.GenerativeModel(model_name=self.model)
        elif "claude" in model_lower:
            self.provider = "claude"
            self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            self.provider = "groq"
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def chat(self, user_input: str, reasoning: Optional[bool] = False) -> Tuple[str, str]:
        """Chat with the assistant - works with any provider"""
        
        if not self.add_history:
            self.messages = [{"role": "system", "content": self.system_prompt}]
        
        self.messages.append({"role": "user", "content": user_input})
        
        if self.provider == "groq":
            response, reasoning_content = self._call_groq()
        elif self.provider == "openai":
            response, reasoning_content = self._call_openai()
        elif self.provider == "gemini":
            response, reasoning_content = self._call_gemini()
        elif self.provider == "claude":
            response, reasoning_content = self._call_claude()
        
        if self.add_history:
            self.messages.append({"role": "assistant", "content": response})
        
        self.reasoning_history.append(reasoning_content)
        
        print(f"🤖 Response: {response}")
        if reasoning and reasoning_content:
            print(f"-----------------------------------------------------------------------------------------------------")
            print(f"🧠 Reasoning: {reasoning_content}")
        
        return response, reasoning_content
    
    def _call_groq(self) -> Tuple[str, str]:
        """Call Groq API"""
        params = {
            "model": self.model,
            "messages": self.messages,
            "temperature": 0.9,
            "max_completion_tokens": 8192,
            "top_p": 1,
            "stream": False,
            "seed": 20
        }
        
        if self.reasoning_effort is not None:
            params["reasoning_effort"] = self.reasoning_effort
        
        completion = self.client.chat.completions.create(**params)
        
        response = completion.choices[0].message.content
        reasoning_content = ""
        
        if hasattr(completion.choices[0].message, 'reasoning'):
            if completion.choices[0].message.reasoning:
                reasoning_content = completion.choices[0].message.reasoning.strip()
        
        return response, reasoning_content
    
    def _call_openai(self) -> Tuple[str, str]:
        """Call OpenAI API"""
        newer_models = ["gpt-5", "o1", "o3"]
        is_newer_model = any(model in self.model.lower() for model in newer_models)
        
        params = {
            "model": self.model,
            "messages": self.messages,
        }
        
        if is_newer_model:
            params["max_completion_tokens"] = 8192
            if "o1" not in self.model.lower() and "o3" not in self.model.lower():
                params["temperature"] = 0.9
        else:
            params["max_tokens"] = 8192
            params["temperature"] = 0.9
        
        completion = self.client.chat.completions.create(**params)
        
        response = completion.choices[0].message.content
        reasoning_content = ""
        if hasattr(completion.choices[0].message, 'reasoning') and completion.choices[0].message.reasoning:
            reasoning_content = completion.choices[0].message.reasoning.strip()
        
        return response, reasoning_content
    
    def _call_gemini(self) -> Tuple[str, str]:
        """Call Google Gemini API"""
        prompt = self._convert_messages_for_gemini()
        
        generation_config = genai.GenerationConfig(
            temperature=0.9,
            max_output_tokens=8192,
        )
        
        response_obj = self.client.generate_content(prompt, generation_config=generation_config)
        response = response_obj.text.strip()
        reasoning_content = ""
        
        return response, reasoning_content
    
    def _call_claude(self) -> Tuple[str, str]:
        """Call Anthropic Claude API"""
        claude_messages = [msg for msg in self.messages if msg["role"] != "system"]
        
        response_obj = self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=claude_messages,
            temperature=0.9,
            max_tokens=8192
        )
        
        response = response_obj.content[0].text.strip()
        reasoning_content = ""
        
        return response, reasoning_content
    
    def _convert_messages_for_gemini(self) -> str:
        """Convert message history to Gemini prompt format"""
        prompt_parts = []
        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts)
    
    def reset(self):
        """Reset conversation history"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.reasoning_history = []