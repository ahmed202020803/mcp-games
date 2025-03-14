"""
Advanced AI System with Enhanced MCP Integration
"""

import json
import logging
import random
import time
from typing import Dict, List, Any, Optional, Tuple, Callable
import requests
from dataclasses import dataclass, field

from ..engine.physics import Vector3

@dataclass
class Memory:
    """Memory structure for AI agents"""
    content: str
    timestamp: float = field(default_factory=time.time)
    importance: float = 1.0
    category: str = "general"
    
    def age(self) -> float:
        """Get the age of this memory in seconds"""
        return time.time() - self.timestamp


class MemorySystem:
    """Memory system for AI agents"""
    
    def __init__(self, capacity: int = 100):
        self.memories: List[Memory] = []
        self.capacity = capacity
        self.logger = logging.getLogger("mcp_games.ai.memory")
    
    def add_memory(self, content: str, importance: float = 1.0, category: str = "general"):
        """Add a new memory"""
        memory = Memory(content=content, importance=importance, category=category)
        self.memories.append(memory)
        
        # If over capacity, remove least important memories
        if len(self.memories) > self.capacity:
            # Sort by importance (lowest first)
            self.memories.sort(key=lambda m: m.importance)
            # Remove least important
            self.memories = self.memories[1:]
            
        self.logger.debug(f"Added memory: {content[:30]}... (importance: {importance})")
    
    def get_memories(self, category: Optional[str] = None, limit: int = 10) -> List[Memory]:
        """Get memories, optionally filtered by category"""
        if category:
            filtered = [m for m in self.memories if m.category == category]
        else:
            filtered = self.memories.copy()
            
        # Sort by importance (highest first)
        filtered.sort(key=lambda m: m.importance, reverse=True)
        
        return filtered[:limit]
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Memory]:
        """Get memories relevant to a query using simple keyword matching"""
        # In a real implementation, this would use embeddings and vector similarity
        # For this example, we'll use simple keyword matching
        keywords = query.lower().split()
        
        # Score memories based on keyword matches
        scored_memories = []
        for memory in self.memories:
            score = 0
            memory_text = memory.content.lower()
            
            for keyword in keywords:
                if keyword in memory_text:
                    score += 1
            
            # Adjust score by importance
            score *= memory.importance
            
            # Adjust score by recency (newer memories get higher scores)
            age_factor = max(0.5, 1.0 - (memory.age() / (24 * 60 * 60)))  # Decay over 24 hours
            score *= age_factor
            
            if score > 0:
                scored_memories.append((memory, score))
        
        # Sort by score (highest first)
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Return top memories
        return [m[0] for m in scored_memories[:limit]]
    
    def forget_old_memories(self, max_age_seconds: float = 3600 * 24 * 7):
        """Forget memories older than the specified age"""
        current_time = time.time()
        self.memories = [m for m in self.memories if (current_time - m.timestamp) <= max_age_seconds]
        
    def summarize_memories(self, category: Optional[str] = None) -> str:
        """Summarize memories, optionally filtered by category"""
        memories = self.get_memories(category)
        if not memories:
            return "No memories available."
            
        summary = "Memory Summary:\n"
        for i, memory in enumerate(memories):
            summary += f"{i+1}. {memory.content} (Importance: {memory.importance:.1f})\n"
            
        return summary


class AdvancedMCPClient:
    """Enhanced client for Model Context Protocol API"""
    
    def __init__(self, api_key: str, endpoint: str = "https://api.example.com/mcp"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.logger = logging.getLogger("mcp_games.ai.mcp")
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history = 20
        
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
    
    def generate_text(self, prompt: str, max_tokens: int = 100, 
                      temperature: float = 0.7, include_history: bool = True) -> str:
        """Generate text via MCP with conversation history"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build messages including history if requested
        messages = []
        if include_history and self.conversation_history:
            messages.extend(self.conversation_history)
        
        # Add the current prompt
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/generate",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("text", "")
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": generated_text})
            
            # Trim history if needed
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]
                
            return generated_text
        except Exception as e:
            self.logger.error(f"MCP text generation failed: {str(e)}")
            return ""
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text via MCP"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/embeddings",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("embedding", [])
        except Exception as e:
            self.logger.error(f"MCP embedding generation failed: {str(e)}")
            return []


class EmotionSystem:
    """Emotion system for AI agents"""
    
    def __init__(self):
        self.emotions = {
            "happiness": 0.5,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "trust": 0.5
        }
        self.personality_traits = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
        self.mood_decay_rate = 0.01  # How quickly emotions return to baseline
        self.logger = logging.getLogger("mcp_games.ai.emotion")
    
    def update_emotion(self, emotion: str, value: float):
        """Update an emotion value"""
        if emotion in self.emotions:
            # Clamp value between 0 and 1
            self.emotions[emotion] = max(0.0, min(1.0, value))
            self.logger.debug(f"Updated emotion {emotion} to {self.emotions[emotion]:.2f}")
    
    def adjust_emotion(self, emotion: str, delta: float):
        """Adjust an emotion by a delta value"""
        if emotion in self.emotions:
            current = self.emotions[emotion]
            self.update_emotion(emotion, current + delta)
    
    def set_personality(self, trait: str, value: float):
        """Set a personality trait value"""
        if trait in self.personality_traits:
            # Clamp value between 0 and 1
            self.personality_traits[trait] = max(0.0, min(1.0, value))
    
    def get_dominant_emotion(self) -> Tuple[str, float]:
        """Get the most dominant emotion"""
        dominant = max(self.emotions.items(), key=lambda x: x[1])
        return dominant
    
    def get_emotional_state(self) -> Dict[str, float]:
        """Get the current emotional state"""
        return self.emotions.copy()
    
    def update(self, delta_time: float):
        """Update emotions over time (decay toward baseline)"""
        for emotion in self.emotions:
            # Skip happiness and trust (they have different baselines)
            if emotion in ["happiness", "trust"]:
                baseline = 0.5
            else:
                baseline = 0.0
                
            # Move toward baseline
            current = self.emotions[emotion]
            if current > baseline:
                self.emotions[emotion] = max(baseline, current - self.mood_decay_rate * delta_time)
            elif current < baseline:
                self.emotions[emotion] = min(baseline, current + self.mood_decay_rate * delta_time)
    
    def get_mood_description(self) -> str:
        """Get a text description of the current mood"""
        dominant, value = self.get_dominant_emotion()
        
        if value < 0.3:
            intensity = "slightly"
        elif value < 0.6:
            intensity = "moderately"
        else:
            intensity = "very"
            
        return f"{intensity} {dominant}"


class AdvancedAIController:
    """Advanced controller for AI-driven game objects"""
    
    def __init__(self, engine: Any, mcp_api_key: Optional[str] = None):
        self.engine = engine
        self.behaviors: Dict[str, Any] = {}
        self.npc_behaviors: Dict[str, str] = {}  # Maps NPC ID to behavior name
        self.logger = logging.getLogger("mcp_games.ai.advanced_controller")
        
        # Memory systems for each NPC
        self.memories: Dict[str, MemorySystem] = {}
        
        # Emotion systems for each NPC
        self.emotions: Dict[str, EmotionSystem] = {}
        
        # Initialize MCP client if API key is provided
        self.mcp_client = None
        if mcp_api_key:
            self.mcp_client = AdvancedMCPClient(mcp_api_key)
            self.logger.info("Advanced MCP client initialized")
    
    def register_behavior(self, name: str, behavior: Any):
        """Register a behavior"""
        self.behaviors[name] = behavior
        self.logger.debug(f"Registered behavior: {name}")
    
    def set_behavior(self, npc: Any, behavior_name: str):
        """Set behavior for an NPC"""
        if behavior_name not in self.behaviors:
            self.logger.warning(f"Behavior not found: {behavior_name}")
            return False
            
        npc.behavior = self.behaviors[behavior_name]
        self.npc_behaviors[npc.id] = behavior_name
        self.logger.debug(f"Set behavior {behavior_name} for NPC {npc.id}")
        return True
    
    def get_or_create_memory(self, npc_id: str) -> MemorySystem:
        """Get or create a memory system for an NPC"""
        if npc_id not in self.memories:
            self.memories[npc_id] = MemorySystem()
        return self.memories[npc_id]
    
    def get_or_create_emotion(self, npc_id: str) -> EmotionSystem:
        """Get or create an emotion system for an NPC"""
        if npc_id not in self.emotions:
            self.emotions[npc_id] = EmotionSystem()
        return self.emotions[npc_id]
    
    def add_memory(self, npc_id: str, content: str, importance: float = 1.0, category: str = "general"):
        """Add a memory for an NPC"""
        memory_system = self.get_or_create_memory(npc_id)
        memory_system.add_memory(content, importance, category)
    
    def get_memories(self, npc_id: str, category: Optional[str] = None, limit: int = 10) -> List[Memory]:
        """Get memories for an NPC"""
        memory_system = self.get_or_create_memory(npc_id)
        return memory_system.get_memories(category, limit)
    
    def update_emotion(self, npc_id: str, emotion: str, value: float):
        """Update an emotion for an NPC"""
        emotion_system = self.get_or_create_emotion(npc_id)
        emotion_system.update_emotion(emotion, value)
    
    def adjust_emotion(self, npc_id: str, emotion: str, delta: float):
        """Adjust an emotion for an NPC"""
        emotion_system = self.get_or_create_emotion(npc_id)
        emotion_system.adjust_emotion(emotion, delta)
    
    def get_mood(self, npc_id: str) -> str:
        """Get the mood description for an NPC"""
        emotion_system = self.get_or_create_emotion(npc_id)
        return emotion_system.get_mood_description()
    
    def generate_dialog(self, npc: Any, context: Dict[str, Any]) -> str:
        """Generate dialog for an NPC using MCP with memory and emotions"""
        if not self.mcp_client:
            self.logger.warning("MCP client not initialized")
            return "..."
        
        # Get memories and emotions
        memory_system = self.get_or_create_memory(npc.id)
        emotion_system = self.get_or_create_emotion(npc.id)
        
        # Get relevant memories
        relevant_memories = memory_system.get_relevant_memories(
            query=json.dumps(context), 
            limit=3
        )
        
        # Format memories as text
        memories_text = ""
        for memory in relevant_memories:
            memories_text += f"- {memory.content}\n"
        
        # Get emotional state
        mood = emotion_system.get_mood_description()
        
        prompt = f"""
        Character: {npc.type}
        Current Mood: {mood}
        
        Memories:
        {memories_text}
        
        Context: {json.dumps(context)}
        
        Generate a natural dialog response for this character based on their memories, current mood, and the context.
        The response should reflect the character's personality and emotional state.
        """
        
        response = self.mcp_client.generate_text(prompt, max_tokens=150)
        
        # Add this interaction to memory
        memory_system.add_memory(
            f"Said: '{response}' in response to {context.get('situation', 'a conversation')}",
            importance=0.7,
            category="dialog"
        )
        
        return response
    
    def make_decision(self, npc: Any, options: List[str], context: Dict[str, Any]) -> str:
        """Make a decision for an NPC using MCP with memory and emotions"""
        if not self.mcp_client:
            self.logger.warning("MCP client not initialized")
            return options[0] if options else ""
        
        # Get memories and emotions
        memory_system = self.get_or_create_memory(npc.id)
        emotion_system = self.get_or_create_emotion(npc.id)
        
        # Get relevant memories
        relevant_memories = memory_system.get_relevant_memories(
            query=json.dumps(context), 
            limit=3
        )
        
        # Format memories as text
        memories_text = ""
        for memory in relevant_memories:
            memories_text += f"- {memory.content}\n"
        
        # Get emotional state
        emotions = emotion_system.get_emotional_state()
        emotions_text = ", ".join([f"{k}: {v:.2f}" for k, v in emotions.items()])
        
        prompt = f"""
        Character: {npc.type}
        Emotional State: {emotions_text}
        
        Memories:
        {memories_text}
        
        Context: {json.dumps(context)}
        Options: {', '.join(options)}
        
        Choose the most appropriate option for this character based on their memories, emotional state, and the context.
        Respond with ONLY the chosen option text, exactly as written in the options list.
        """
        
        response = self.mcp_client.generate_text(prompt, max_tokens=50)
        
        # Find the option that best matches the response
        best_match = options[0] if options else ""
        best_match_score = 0
        
        for option in options:
            # Simple string matching for this example
            if option.lower() in response.lower():
                # If exact match, return immediately
                if option.lower() == response.lower().strip():
                    best_match = option
                    break
                
                # Otherwise, score by length of match
                score = len(option)
                if score > best_match_score:
                    best_match = option
                    best_match_score = score
        
        # Add this decision to memory
        memory_system.add_memory(
            f"Decided to '{best_match}' when faced with options: {', '.join(options)}",
            importance=0.8,
            category="decision"
        )
        
        return best_match
    
    def update(self, delta_time: float):
        """Update all AI systems"""
        # Update emotion systems
        for npc_id, emotion_system in self.emotions.items():
            emotion_system.update(delta_time)