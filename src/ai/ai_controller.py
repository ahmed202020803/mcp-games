"""
AI Controller with MCP Integration
"""

import logging
import json
from typing import Dict, List, Any, Optional
import requests

from ..engine.game_engine import GameEngine, NPC
from .behavior import Behavior

class MCPClient:
    """Client for Model Context Protocol API"""
    
    def __init__(self, api_key: str, endpoint: str = "https://api.example.com/mcp"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.logger = logging.getLogger("mcp_games.ai.mcp")
        
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via MCP"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "tool": tool_name,
            "parameters": params
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/tools/execute",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"MCP tool execution failed: {str(e)}")
            return {"error": str(e)}
            
    def generate_text(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text via MCP"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/generate",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json().get("text", "")
        except Exception as e:
            self.logger.error(f"MCP text generation failed: {str(e)}")
            return ""


class AIController:
    """Controller for AI-driven game objects"""
    
    def __init__(self, engine: GameEngine, mcp_api_key: Optional[str] = None):
        self.engine = engine
        self.behaviors: Dict[str, Behavior] = {}
        self.npc_behaviors: Dict[str, str] = {}  # Maps NPC ID to behavior name
        self.logger = logging.getLogger("mcp_games.ai.controller")
        
        # Initialize MCP client if API key is provided
        self.mcp_client = None
        if mcp_api_key:
            self.mcp_client = MCPClient(mcp_api_key)
            self.logger.info("MCP client initialized")
        
    def register_behavior(self, name: str, behavior: Behavior):
        """Register a behavior"""
        self.behaviors[name] = behavior
        self.logger.debug(f"Registered behavior: {name}")
        
    def set_behavior(self, npc: NPC, behavior_name: str):
        """Set behavior for an NPC"""
        if behavior_name not in self.behaviors:
            self.logger.warning(f"Behavior not found: {behavior_name}")
            return False
            
        npc.behavior = self.behaviors[behavior_name]
        self.npc_behaviors[npc.id] = behavior_name
        self.logger.debug(f"Set behavior {behavior_name} for NPC {npc.id}")
        return True
        
    def generate_dialog(self, npc: NPC, context: Dict[str, Any]) -> str:
        """Generate dialog for an NPC using MCP"""
        if not self.mcp_client:
            self.logger.warning("MCP client not initialized")
            return "..."
            
        prompt = f"""
        Character: {npc.type}
        Context: {json.dumps(context)}
        
        Generate a natural dialog response for this character based on the context.
        """
        
        return self.mcp_client.generate_text(prompt)
        
    def make_decision(self, npc: NPC, options: List[str], context: Dict[str, Any]) -> str:
        """Make a decision for an NPC using MCP"""
        if not self.mcp_client:
            self.logger.warning("MCP client not initialized")
            return options[0] if options else ""
            
        prompt = f"""
        Character: {npc.type}
        Context: {json.dumps(context)}
        Options: {', '.join(options)}
        
        Choose the most appropriate option for this character based on the context.
        """
        
        response = self.mcp_client.generate_text(prompt)
        
        # Find the option that best matches the response
        best_match = options[0] if options else ""
        for option in options:
            if option.lower() in response.lower():
                best_match = option
                break
                
        return best_match