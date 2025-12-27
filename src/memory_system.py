"""
Memory System with Vector Database
Provides long-term memory using embeddings and vector similarity search
"""

import logging
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json
from config import (
    MEMORY_ENABLED, MEMORY_TYPE, MEMORY_CONVERSATIONS_DIR,
    EMBEDDING_MODEL, MAX_MEMORY_RETRIEVALS, MEMORY_SIMILARITY_THRESHOLD
)

logger = logging.getLogger(__name__)


class MemorySystem:
    """Long-term memory system using vector embeddings"""

    def __init__(self, enabled: bool = MEMORY_ENABLED):
        """
        Initialize memory system

        Args:
            enabled: Whether memory system is enabled
        """
        self.enabled = enabled
        self.conversation_history: List[Dict] = []

        if not self.enabled:
            logger.info("Memory system disabled")
            return

        # Initialize ChromaDB
        try:
            self.client = chromadb.PersistentClient(
                path=str(MEMORY_CONVERSATIONS_DIR),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="rufus_conversations",
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(f"Memory system initialized ({len(self.collection.get())} memories)")

        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            self.enabled = False

    def add_memory(
        self,
        user_input: str,
        bot_response: str,
        emotion: str = "neutral",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Store conversation in memory

        Args:
            user_input: User's message
            bot_response: Bot's response
            emotion: Detected emotion
            metadata: Additional metadata

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            timestamp = datetime.now().isoformat()

            # Store in ChromaDB
            document = f"User: {user_input}\nRufus: {bot_response}"

            self.collection.add(
                documents=[document],
                metadatas=[{
                    "timestamp": timestamp,
                    "emotion": emotion,
                    "user_input": user_input,
                    "bot_response": bot_response,
                    **(metadata or {})
                }],
                ids=[f"memory_{timestamp}"]
            )

            # Also store in local history
            self.conversation_history.append({
                "timestamp": timestamp,
                "user_input": user_input,
                "bot_response": bot_response,
                "emotion": emotion
            })

            logger.debug(f"Memory added: {timestamp}")
            return True

        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False

    def retrieve_relevant_memories(
        self,
        query: str,
        n_results: int = MAX_MEMORY_RETRIEVALS
    ) -> List[Dict]:
        """
        Retrieve relevant memories based on query

        Args:
            query: Search query
            n_results: Number of results to return

        Returns:
            List of relevant memory dictionaries
        """
        if not self.enabled:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else 0

                    # Convert distance to similarity score (cosine)
                    similarity = 1 - distance

                    if similarity >= MEMORY_SIMILARITY_THRESHOLD:
                        memories.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity
                        })

            logger.debug(f"Retrieved {len(memories)} memories")
            return memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []

    def get_recent_memories(self, n: int = 10) -> List[Dict]:
        """
        Get most recent memories

        Args:
            n: Number of recent memories

        Returns:
            List of recent memory dictionaries
        """
        if not self.enabled:
            return []

        try:
            results = self.collection.get(
                limit=n,
                order_by="timestamp"  # Requires ChromaDB 0.4+
            )

            memories = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    memories.append({
                        "content": doc,
                        "metadata": results['metadatas'][i]
                    })

            return memories

        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return []

    def search_by_emotion(self, emotion: str) -> List[Dict]:
        """
        Search memories by emotion

        Args:
            emotion: Emotion to search for

        Returns:
            List of memories with matching emotion
        """
        if not self.enabled:
            return []

        try:
            results = self.collection.get(
                where={"emotion": emotion}
            )

            memories = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    memories.append({
                        "content": doc,
                        "metadata": results['metadatas'][i]
                    })

            logger.debug(f"Found {len(memories)} {emotion} memories")
            return memories

        except Exception as e:
            logger.error(f"Failed to search by emotion: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Get memory system statistics

        Returns:
            Statistics dictionary
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            count = len(self.collection.get())
            recent = self.get_recent_memories(100)

            # Emotion distribution
            emotions = {}
            for memory in recent:
                emotion = memory['metadata'].get('emotion', 'neutral')
                emotions[emotion] = emotions.get(emotion, 0) + 1

            return {
                "enabled": True,
                "total_memories": count,
                "emotion_distribution": emotions,
                "recent_conversations": len(self.conversation_history)
            }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"enabled": True, "error": str(e)}

    def clear_all_memories(self) -> bool:
        """
        Clear all stored memories

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            self.client.delete_collection("rufus_conversations")
            self.collection = self.client.get_or_create_collection(
                name="rufus_conversations",
                metadata={"hnsw:space": "cosine"}
            )
            self.conversation_history = []

            logger.info("All memories cleared")
            return True

        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return False

    def export_conversations(self, filepath: Optional[str] = None) -> bool:
        """
        Export conversation history to JSON

        Args:
            filepath: Output file path

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        try:
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = MEMORY_CONVERSATIONS_DIR / f"rufus_conversations_{timestamp}.json"

            with open(filepath, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)

            logger.info(f"Conversations exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to export conversations: {e}")
            return False

    def get_context_for_response(self, query: str) -> str:
        """
        Get relevant context to enhance AI responses

        Args:
            query: Current user query

        Returns:
            Context string to add to system prompt
        """
        if not self.enabled:
            return ""

        memories = self.retrieve_relevant_memories(query, n_results=3)

        if not memories:
            return ""

        context = "\n\nRelevant past conversations:\n"
        for i, memory in enumerate(memories, 1):
            context += f"{i}. {memory['metadata']['user_input']}\n"

        return context
