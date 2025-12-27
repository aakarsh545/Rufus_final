"""
Conversation Module
Manages chat history and communication with GPT-4
"""

import openai
import logging
from typing import List, Dict, Optional
from config import (
    OPENAI_API_KEY, CHAT_MODEL,
    MAX_CONVERSATION_TURNS, SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation with AI model"""

    def __init__(self, api_key: str = OPENAI_API_KEY):
        """
        Initialize conversation manager

        Args:
            api_key: OpenAI API key
        """
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set. Set it in environment or .env file.")

        openai.api_key = api_key
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def add_message(self, role: str, content: str) -> None:
        """
        Add message to conversation history

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        self.messages.append({"role": role, "content": content})

        # Keep conversation within limit
        if len(self.messages) > MAX_CONVERSATION_TURNS + 1:  # +1 for system prompt
            # Remove oldest user/assistant pair (after system prompt)
            if len(self.messages) >= 3:
                self.messages.pop(1)  # Remove oldest non-system message
                self.messages.pop(1)  # Remove its response

        logger.debug(f"Added {role} message. Total messages: {len(self.messages)}")

    def get_response(self, user_input: str) -> Optional[str]:
        """
        Get AI response to user input

        Args:
            user_input: User's message

        Returns:
            AI response, or None if failed
        """
        self.add_message("user", user_input)

        try:
            response = openai.chat.completions.create(
                model=CHAT_MODEL,
                messages=self.messages
            )

            assistant_message = response.choices[0].message.content
            self.add_message("assistant", assistant_message)

            logger.info(f"Assistant: {assistant_message}")
            return assistant_message

        except Exception as e:
            logger.error(f"Failed to get AI response: {e}")
            return None

    def clear_memory(self) -> None:
        """Clear conversation history (keep system prompt)"""
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        logger.info("Conversation memory cleared")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get current conversation history

        Returns:
            List of message dictionaries
        """
        return self.messages.copy()

    def set_system_prompt(self, prompt: str) -> None:
        """
        Update system prompt

        Args:
            prompt: New system prompt
        """
        self.messages[0] = {"role": "system", "content": prompt}
        logger.info("System prompt updated")
