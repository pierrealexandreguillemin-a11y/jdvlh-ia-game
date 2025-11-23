"""
Intelligent Model Router for JDVLH IA Game
Inspired by ollama-gateway and ollama-orchestrator

Automatically selects the best Ollama model based on:
- Prompt context (location, dialogue, action)
- Task type (narrative, description, choice)
- Model availability and performance
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ollama


class TaskType(Enum):
    """Types of narrative tasks"""

    LOCATION_DESCRIPTION = "location_description"  # Long, detailed
    QUICK_CHOICE = "quick_choice"  # Short, fast
    DIALOGUE = "dialogue"  # Medium, conversational
    EPIC_ACTION = "epic_action"  # Dramatic, creative
    GENERAL = "general"  # Fallback


@dataclass
class ModelConfig:
    """Configuration for an Ollama model"""

    name: str
    specialties: List[str]
    priority: int  # 1 = highest
    max_tokens: int
    temperature: float
    speed_rating: int  # 1-5, 5 = fastest


class ModelRouter:
    """
    Intelligent routing of prompts to optimal Ollama models
    """

    def __init__(self):
        self.available_models = self._detect_local_models()
        self.routing_rules = self._init_routing_rules()
        self.fallback_model = "mistral"
        self.stats = {"total_requests": 0, "by_model": {}, "by_task": {}}

    def _detect_local_models(self) -> Dict[str, ModelConfig]:
        """Detect available local Ollama models"""
        try:
            models_list = ollama.list()
            detected = {}

            for model in models_list.get("models", []):
                name = model["name"]
                base_name = name.split(":")[0]

                # Configure based on model name patterns
                config = self._configure_model(base_name, name)
                if config:
                    detected[base_name] = config

            print(
                f"[ModelRouter] Detected {len(detected)} local models: {list(detected.keys())}"
            )
            return detected

        except Exception as e:
            print(f"[ModelRouter] Error detecting models: {e}")
            # Fallback to default Mistral
            return {
                "mistral": ModelConfig(
                    name="mistral",
                    specialties=["general", "narrative"],
                    priority=1,
                    max_tokens=150,
                    temperature=0.7,
                    speed_rating=3,
                )
            }

    def _configure_model(self, base_name: str, full_name: str) -> Optional[ModelConfig]:
        """Configure a model based on its name"""

        # Coding models
        if any(x in base_name.lower() for x in ["code", "coder", "deepseek-coder"]):
            return ModelConfig(
                name=full_name,
                specialties=["code", "programming", "debug"],
                priority=1,
                max_tokens=400,
                temperature=0.6,
                speed_rating=2,
            )

        # Fast models
        if "llama3.2" in base_name.lower() or "phi" in base_name.lower():
            return ModelConfig(
                name=full_name,
                specialties=["quick", "fast", "short"],
                priority=3,
                max_tokens=150,
                temperature=0.7,
                speed_rating=5,
            )

        # Creative models
        if "gemma" in base_name.lower():
            return ModelConfig(
                name=full_name,
                specialties=["creative", "story", "epic", "dramatic"],
                priority=2,
                max_tokens=150,
                temperature=0.8,
                speed_rating=3,
            )

        # Multilingual
        if any(x in base_name.lower() for x in ["qwen", "aya"]):
            return ModelConfig(
                name=full_name,
                specialties=["multilingual", "translate", "french"],
                priority=2,
                max_tokens=200,
                temperature=0.7,
                speed_rating=3,
            )

        # Chess models
        if "chess" in base_name.lower():
            return ModelConfig(
                name=full_name,
                specialties=["chess", "strategy", "game"],
                priority=1,
                max_tokens=200,
                temperature=0.6,
                speed_rating=3,
            )

        # General purpose (Mistral, etc.)
        if any(x in base_name.lower() for x in ["mistral", "llama", "general"]):
            return ModelConfig(
                name=full_name,
                specialties=["general", "narrative", "conversation"],
                priority=1,
                max_tokens=150,
                temperature=0.7,
                speed_rating=3,
            )

        return None

    def _init_routing_rules(self) -> Dict[TaskType, Dict]:
        """Initialize routing rules for each task type"""
        return {
            TaskType.LOCATION_DESCRIPTION: {
                "keywords": [
                    "décris",
                    "lieu",
                    "paysage",
                    "atmosphère",
                    "endroit",
                    "région",
                ],
                "preferred_specialties": ["narrative", "creative", "general"],
                "tokens": 150,
                "temperature": 0.75,
                "priority_boost": {
                    "gemma": 1,
                    "mistral": 0,
                },  # Prefer creative for locations
            },
            TaskType.QUICK_CHOICE: {
                "keywords": ["choisit", "options", "que fais-tu", "choix", "décide"],
                "preferred_specialties": ["quick", "fast", "short"],
                "tokens": 100,
                "temperature": 0.7,
                "priority_boost": {
                    "llama3.2": 2,
                    "phi": 2,
                },  # Strongly prefer fast models
            },
            TaskType.DIALOGUE: {
                "keywords": [
                    "dit",
                    "parle",
                    "dialogue",
                    "répond",
                    "demande",
                    "conversation",
                ],
                "preferred_specialties": ["conversation", "general", "narrative"],
                "tokens": 150,
                "temperature": 0.7,
                "priority_boost": {"mistral": 1, "qwen": 0},
            },
            TaskType.EPIC_ACTION: {
                "keywords": [
                    "combat",
                    "attaque",
                    "danger",
                    "bataille",
                    "aventure",
                    "action",
                ],
                "preferred_specialties": ["creative", "dramatic", "epic"],
                "tokens": 150,
                "temperature": 0.8,
                "priority_boost": {"gemma": 2},  # Strongly prefer creative for drama
            },
            TaskType.GENERAL: {
                "keywords": [],
                "preferred_specialties": ["general", "narrative"],
                "tokens": 150,
                "temperature": 0.7,
                "priority_boost": {},
            },
        }

    def detect_task_type(self, prompt: str, context: str = "") -> TaskType:
        """Detect the type of narrative task from prompt"""
        combined = (prompt + " " + context).lower()

        # Check each task type
        for task_type, rules in self.routing_rules.items():
            if task_type == TaskType.GENERAL:
                continue

            # Check if any keywords match
            if any(keyword in combined for keyword in rules["keywords"]):
                return task_type

        return TaskType.GENERAL

    def select_model(
        self, prompt: str, context: str = "", task_type: Optional[TaskType] = None
    ) -> Tuple[str, Dict]:
        """
        Select the best model for a given prompt

        Returns:
            Tuple of (model_name, generation_options)
        """

        if not task_type:
            task_type = self.detect_task_type(prompt, context)

        rules = self.routing_rules[task_type]

        # Score each available model
        scores = {}
        for model_name, config in self.available_models.items():
            score = 0

            # Base priority (lower number = higher priority)
            score += (4 - config.priority) * 10

            # Specialty match
            for specialty in config.specialties:
                if specialty in rules["preferred_specialties"]:
                    score += 20

            # Priority boost for specific models
            for boost_model, boost_points in rules["priority_boost"].items():
                if boost_model in model_name.lower():
                    score += boost_points * 15

            # Speed bonus for quick tasks
            if task_type == TaskType.QUICK_CHOICE:
                score += config.speed_rating * 5

            scores[model_name] = score

        # Select model with highest score
        if scores:
            best_model = max(scores.items(), key=lambda x: x[1])[0]
            selected_config = self.available_models[best_model]
        else:
            # Fallback if no models available
            best_model = self.fallback_model
            selected_config = ModelConfig(
                name=self.fallback_model,
                specialties=["general"],
                priority=1,
                max_tokens=rules["tokens"],
                temperature=rules["temperature"],
                speed_rating=3,
            )

        # Prepare generation options
        options = {
            "temperature": rules.get("temperature", selected_config.temperature),
            "num_predict": rules.get("tokens", selected_config.max_tokens),
        }

        # Update stats
        self.stats["total_requests"] += 1
        self.stats["by_model"][best_model] = (
            self.stats["by_model"].get(best_model, 0) + 1
        )
        self.stats["by_task"][task_type.value] = (
            self.stats["by_task"].get(task_type.value, 0) + 1
        )

        print(
            f"[ModelRouter] Task: {task_type.value}, Selected: {best_model}, Options: {options}"
        )

        return best_model, options

    def get_model_for_task(self, task_type: TaskType) -> Tuple[str, Dict]:
        """Get the preferred model for a specific task type"""
        return self.select_model("", "", task_type)

    def get_stats(self) -> Dict:
        """Get routing statistics"""
        return {
            "total_requests": self.stats["total_requests"],
            "by_model": self.stats["by_model"],
            "by_task": self.stats["by_task"],
            "available_models": list(self.available_models.keys()),
            "fallback_model": self.fallback_model,
        }

    def test_routing(self, prompt: str) -> Dict:
        """Test routing for a prompt (for debugging)"""
        task_type = self.detect_task_type(prompt)
        model, options = self.select_model(prompt, task_type=task_type)

        return {
            "prompt": prompt,
            "task_type": task_type.value,
            "selected_model": model,
            "options": options,
            "reason": f"Best for {task_type.value}",
        }


# Singleton instance
_router_instance = None


def get_router() -> ModelRouter:
    """Get or create the global ModelRouter instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance
