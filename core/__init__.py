"""
Darukaa BioIntelligence Core Module.
Ecological knowledge retrieval, multi-metric reasoning, and conversational intelligence.
"""

from .knowledge_base import KnowledgeBase
from .spatial_resolver import SpatialResolver
from .reasoning_engine import ReasoningEngine
from .dialogue_manager import DialogueManager, ScientificSessionManager

__all__ = [
    "KnowledgeBase",
    "SpatialResolver",
    "ReasoningEngine",
    "DialogueManager",
    "ScientificSessionManager",
]
