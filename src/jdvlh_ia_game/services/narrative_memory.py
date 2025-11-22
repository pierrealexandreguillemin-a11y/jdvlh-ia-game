"""
Advanced Narrative Memory System for JDVLH IA Game
Improves narrative coherence through:
- Entity tracking (characters, items, locations)
- Relationship management
- Event timeline
- Smart context summarization
"""

import re
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Entity:
    """Represents a narrative entity (character, item, location)"""
    name: str
    type: str  # 'character', 'item', 'location'
    first_mentioned: int  # Turn number
    last_mentioned: int
    attributes: Dict[str, Any] = field(default_factory=dict)
    relations: List[str] = field(default_factory=list)
    mentions_count: int = 0


@dataclass
class NarrativeEvent:
    """Represents an important event in the story"""
    turn: int
    description: str
    entities_involved: List[str]
    location: str
    importance: int  # 1-5, 5 = critical
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class NarrativeMemory:
    """
    Enhanced memory system for maintaining narrative coherence
    """

    def __init__(self, max_turns: int = 50):
        self.max_turns = max_turns
        self.current_turn = 0

        # Entity tracking
        self.entities: Dict[str, Entity] = {}  # name -> Entity
        self.locations_visited: Set[str] = set()
        self.current_location: str = "la Comté"

        # Event tracking
        self.events: List[NarrativeEvent] = []
        self.important_facts: List[str] = []

        # Relationships
        self.relationships: Dict[str, List[str]] = defaultdict(list)  # entity -> related entities

        # Quest/Goal tracking
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []

        # Named entities patterns (LOTR/DnD themed)
        self.character_patterns = [
            r'\b(hobbit|elfe|nain|orc|gobelin|troll|magicien|guerrier|ranger)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # Proper names
        ]

        self.item_patterns = [
            r'\b(épée|bouclier|anneau|dague|arc|potion|grimoire|trésor|coffre|armure)\b',
            r'\b(objet|artefact|relique)\b',
        ]

        self.location_keywords = {
            "la Comté", "Fondcombe", "les Mines de la Moria",
            "la forêt de Fangorn", "Minas Tirith", "le Mont Destin",
            "les plaines du Rohan", "Isengard", "Helm's Deep",
            "la forêt de Lothlórien", "la rivière Anduin", "la montagne solitaire",
            "taverne", "forêt", "montagne", "rivière", "grotte", "château"
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities (characters, items, locations) from text"""
        text_lower = text.lower()
        extracted = {
            "characters": [],
            "items": [],
            "locations": []
        }

        # Extract characters
        for pattern in self.character_patterns:
            matches = re.findall(pattern, text_lower)
            extracted["characters"].extend(matches)

        # Extract items
        for pattern in self.item_patterns:
            matches = re.findall(pattern, text_lower)
            extracted["items"].extend(matches)

        # Extract locations
        for location in self.location_keywords:
            if location.lower() in text_lower:
                extracted["locations"].append(location)

        # Deduplicate
        for key in extracted:
            extracted[key] = list(set(extracted[key]))

        return extracted

    def update_entities(self, narrative: str, choice: str = ""):
        """Update entity tracking from narrative and player choice"""
        combined_text = f"{narrative} {choice}"
        extracted = self.extract_entities(combined_text)

        # Update or create entities
        for char in extracted["characters"]:
            if char not in self.entities:
                self.entities[char] = Entity(
                    name=char,
                    type="character",
                    first_mentioned=self.current_turn,
                    last_mentioned=self.current_turn,
                    mentions_count=1
                )
            else:
                self.entities[char].last_mentioned = self.current_turn
                self.entities[char].mentions_count += 1

        for item in extracted["items"]:
            if item not in self.entities:
                self.entities[item] = Entity(
                    name=item,
                    type="item",
                    first_mentioned=self.current_turn,
                    last_mentioned=self.current_turn,
                    mentions_count=1
                )
            else:
                self.entities[item].last_mentioned = self.current_turn
                self.entities[item].mentions_count += 1

        for location in extracted["locations"]:
            self.locations_visited.add(location)
            if location not in self.entities:
                self.entities[location] = Entity(
                    name=location,
                    type="location",
                    first_mentioned=self.current_turn,
                    last_mentioned=self.current_turn,
                    mentions_count=1
                )
            else:
                self.entities[location].last_mentioned = self.current_turn
                self.entities[location].mentions_count += 1

    def add_event(self, description: str, location: str, entities: List[str], importance: int = 3):
        """Add an important event to memory"""
        event = NarrativeEvent(
            turn=self.current_turn,
            description=description,
            entities_involved=entities,
            location=location,
            importance=importance
        )
        self.events.append(event)

        # Keep only important events if list gets too long
        if len(self.events) > 20:
            self.events = sorted(self.events, key=lambda e: e.importance, reverse=True)[:15]

    def detect_important_events(self, narrative: str) -> Optional[NarrativeEvent]:
        """Detect if narrative contains an important event"""
        importance_keywords = {
            5: ["dragon", "bataille", "mort", "victoire", "défaite", "découvre le trésor"],
            4: ["combat", "rencontre", "trouve", "perd", "gagne"],
            3: ["explore", "voyage", "parle", "décide"],
        }

        narrative_lower = narrative.lower()
        for importance, keywords in importance_keywords.items():
            if any(kw in narrative_lower for kw in keywords):
                entities = self.extract_entities(narrative)
                all_entities = entities["characters"] + entities["items"]

                return NarrativeEvent(
                    turn=self.current_turn,
                    description=narrative[:100],  # First 100 chars
                    entities_involved=all_entities[:5],
                    location=self.current_location,
                    importance=importance
                )

        return None

    def get_recent_context(self, num_events: int = 5) -> str:
        """Get recent important events as context"""
        if not self.events:
            return ""

        recent_events = sorted(self.events, key=lambda e: e.turn, reverse=True)[:num_events]
        context_lines = ["Événements récents importants:"]

        for event in recent_events:
            context_lines.append(f"- {event.description}")

        return "\n".join(context_lines)

    def get_active_entities(self, recency_threshold: int = 5) -> List[Entity]:
        """Get entities mentioned in recent turns"""
        active = []
        for entity in self.entities.values():
            if self.current_turn - entity.last_mentioned <= recency_threshold:
                active.append(entity)

        return sorted(active, key=lambda e: e.mentions_count, reverse=True)

    def get_context_summary(self) -> str:
        """Generate a smart context summary for the LLM"""
        lines = []

        # Current location
        lines.append(f"Lieu actuel: {self.current_location}")

        # Active entities
        active_entities = self.get_active_entities()
        if active_entities:
            chars = [e.name for e in active_entities if e.type == "character"][:3]
            items = [e.name for e in active_entities if e.type == "item"][:3]

            if chars:
                lines.append(f"Personnages présents: {', '.join(chars)}")
            if items:
                lines.append(f"Objets importants: {', '.join(items)}")

        # Recent events
        if self.events:
            recent = sorted(self.events, key=lambda e: e.turn, reverse=True)[:3]
            lines.append("Événements récents:")
            for event in recent:
                lines.append(f"  - {event.description[:80]}")

        # Active quests
        if self.active_quests:
            lines.append(f"Quêtes actives: {', '.join(self.active_quests[:2])}")

        return "\n".join(lines)

    def get_locations_summary(self) -> str:
        """Get summary of visited locations"""
        if not self.locations_visited:
            return "Aucun lieu visité pour l'instant."

        return f"Lieux visités: {', '.join(list(self.locations_visited)[:5])}"

    def update_location(self, new_location: str):
        """Update current location"""
        if new_location != self.current_location:
            self.current_location = new_location
            self.locations_visited.add(new_location)

    def add_quest(self, quest_description: str):
        """Add a new quest to active quests"""
        if quest_description not in self.active_quests:
            self.active_quests.append(quest_description)

    def complete_quest(self, quest_description: str):
        """Mark quest as completed"""
        if quest_description in self.active_quests:
            self.active_quests.remove(quest_description)
            self.completed_quests.append(quest_description)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "current_turn": self.current_turn,
            "total_entities": len(self.entities),
            "characters": sum(1 for e in self.entities.values() if e.type == "character"),
            "items": sum(1 for e in self.entities.values() if e.type == "item"),
            "locations_visited": len(self.locations_visited),
            "total_events": len(self.events),
            "active_quests": len(self.active_quests),
            "completed_quests": len(self.completed_quests)
        }

    def advance_turn(self):
        """Advance to next turn"""
        self.current_turn += 1

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to dict for storage"""
        return {
            "current_turn": self.current_turn,
            "current_location": self.current_location,
            "locations_visited": list(self.locations_visited),
            "entities": {
                name: {
                    "name": e.name,
                    "type": e.type,
                    "first_mentioned": e.first_mentioned,
                    "last_mentioned": e.last_mentioned,
                    "mentions_count": e.mentions_count,
                    "attributes": e.attributes,
                    "relations": e.relations
                }
                for name, e in self.entities.items()
            },
            "events": [
                {
                    "turn": ev.turn,
                    "description": ev.description,
                    "entities_involved": ev.entities_involved,
                    "location": ev.location,
                    "importance": ev.importance,
                    "timestamp": ev.timestamp
                }
                for ev in self.events
            ],
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeMemory':
        """Deserialize memory from dict"""
        memory = cls()
        memory.current_turn = data.get("current_turn", 0)
        memory.current_location = data.get("current_location", "la Comté")
        memory.locations_visited = set(data.get("locations_visited", []))

        # Restore entities
        for name, entity_data in data.get("entities", {}).items():
            memory.entities[name] = Entity(
                name=entity_data["name"],
                type=entity_data["type"],
                first_mentioned=entity_data["first_mentioned"],
                last_mentioned=entity_data["last_mentioned"],
                mentions_count=entity_data.get("mentions_count", 1),
                attributes=entity_data.get("attributes", {}),
                relations=entity_data.get("relations", [])
            )

        # Restore events
        for event_data in data.get("events", []):
            memory.events.append(NarrativeEvent(
                turn=event_data["turn"],
                description=event_data["description"],
                entities_involved=event_data["entities_involved"],
                location=event_data["location"],
                importance=event_data["importance"],
                timestamp=event_data.get("timestamp", "")
            ))

        memory.active_quests = data.get("active_quests", [])
        memory.completed_quests = data.get("completed_quests", [])

        return memory


class SmartHistoryManager:
    """
    Manages narrative history with intelligent summarization
    """

    def __init__(self, max_raw_history: int = 30, max_context_tokens: int = 1000):
        self.max_raw_history = max_raw_history
        self.max_context_tokens = max_context_tokens
        self.raw_history: List[str] = []

    def add_interaction(self, player_action: str, narrative_response: str):
        """Add a player-narrative interaction"""
        self.raw_history.append(f"Joueur: {player_action}")
        self.raw_history.append(f"MJ: {narrative_response}")

        # Truncate if too long
        if len(self.raw_history) > self.max_raw_history:
            self.raw_history = self.raw_history[-self.max_raw_history:]

    def get_recent_history(self, num_interactions: int = 10) -> List[str]:
        """Get recent history entries"""
        return self.raw_history[-num_interactions * 2:]

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4

    def get_smart_context(self, memory: NarrativeMemory) -> List[str]:
        """Build smart context combining recent history and memory"""
        context = []

        # Add memory summary
        summary = memory.get_context_summary()
        if summary:
            context.append(summary)
            context.append("")

        # Add recent history
        recent = self.get_recent_history(num_interactions=5)
        if recent:
            context.append("Derniers échanges:")
            context.extend(recent)

        # Check token budget
        full_context = "\n".join(context)
        if self.estimate_tokens(full_context) > self.max_context_tokens:
            # Reduce to essentials
            context = [summary] if summary else []
            context.extend(self.get_recent_history(num_interactions=3))

        return context
