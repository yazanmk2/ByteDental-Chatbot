"""
ByteDent Conversational Handler
================================
Handles greetings, small talk, and conversational interactions
that don't require RAG retrieval.
"""

import random
import re
from typing import Optional, Dict, List
from datetime import datetime


class ConversationalHandler:
    """Handle conversational queries like greetings and small talk"""

    def __init__(self):
        # Greeting patterns
        self.greeting_patterns = [
            r'\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b',
            r'^(hi|hello|hey)[\s!.]*$',
        ]

        # How are you patterns
        self.how_are_you_patterns = [
            r'how (are|r) (you|u)',
            r'how\'s it going',
            r'how is it going',
            r'what\'s up',
            r'whats up',
            r'how do you do',
        ]

        # Gratitude patterns
        self.thanks_patterns = [
            r'\b(thank you|thanks|thank u|thx|appreciate)\b',
            r'\b(grateful|gratitude)\b',
        ]

        # Goodbye patterns
        self.goodbye_patterns = [
            r'\b(bye|goodbye|see you|farewell|take care)\b',
            r'\b(have a (good|great|nice) day)\b',
        ]

        # Small talk patterns
        self.small_talk_patterns = {
            'name': r'(what is|what\'s|whats) (your|ur) name',
            'age': r'(how old are you|what\'s your age|whats your age)',
            'creator': r'who (created|made|built|developed) you',
            'purpose': r'(what do you do|what can you do|what are you for|what\'s your purpose)',
            'capabilities': r'(what can you help with|how can you help|what are your capabilities)',
        }

    def is_conversational(self, query: str) -> bool:
        """Check if query is conversational (not informational)"""
        query_lower = query.lower().strip()

        # Check all patterns
        all_patterns = (
            self.greeting_patterns +
            self.how_are_you_patterns +
            self.thanks_patterns +
            self.goodbye_patterns +
            list(self.small_talk_patterns.values())
        )

        for pattern in all_patterns:
            if re.search(pattern, query_lower):
                return True

        return False

    def handle(self, query: str) -> Optional[Dict]:
        """
        Handle conversational query and return response.
        Returns None if not a conversational query.
        """
        query_lower = query.lower().strip()

        # Check for greeting
        if self._matches_any(query_lower, self.greeting_patterns):
            return self._create_response(
                self._random_greeting(),
                "conversational"
            )

        # Check for how are you
        if self._matches_any(query_lower, self.how_are_you_patterns):
            return self._create_response(
                self._random_how_are_you_response(),
                "conversational"
            )

        # Check for thanks
        if self._matches_any(query_lower, self.thanks_patterns):
            return self._create_response(
                self._random_thanks_response(),
                "conversational"
            )

        # Check for goodbye
        if self._matches_any(query_lower, self.goodbye_patterns):
            return self._create_response(
                self._random_goodbye_response(),
                "conversational"
            )

        # Check for small talk
        for talk_type, pattern in self.small_talk_patterns.items():
            if re.search(pattern, query_lower):
                return self._create_response(
                    self._handle_small_talk(talk_type),
                    "conversational"
                )

        return None

    def _matches_any(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the patterns"""
        return any(re.search(pattern, text) for pattern in patterns)

    def _create_response(self, message: str, response_type: str = "answer") -> Dict:
        """Create a formatted conversational response"""
        return {
            "type": "answer",
            "message": message,
            "citations": [],
            "handoff_reason": None,
            "retrieval": {
                "top_similarity_score": None,
                "chunks_retrieved": 0,
                "retrieval_time_ms": 0
            }
        }

    def _random_greeting(self) -> str:
        """Generate a random greeting response"""
        greetings = [
            "Hello! I'm the ByteDent AI assistant. How can I help you with dental imaging or dental health questions today?",
            "Hi there! Welcome to ByteDent. I'm here to answer your questions about dental imaging, CBCT scans, and dental procedures. What would you like to know?",
            "Greetings! I'm your ByteDent dental AI assistant. Feel free to ask me anything about dental imaging, treatments, or our ByteDent platform!",
            "Hey! Nice to meet you. I'm here to help with questions about dental imaging, dental health, and the ByteDent platform. What can I help you with?",
        ]

        # Add time-based greeting
        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = "Good morning! "
        elif 12 <= hour < 18:
            time_greeting = "Good afternoon! "
        else:
            time_greeting = "Good evening! "

        base_greeting = random.choice(greetings)
        return time_greeting + base_greeting

    def _random_how_are_you_response(self) -> str:
        """Generate a random 'how are you' response"""
        responses = [
            "I'm doing great, thank you for asking! I'm ready to help you with any questions about dental imaging or dental health. How can I assist you today?",
            "I'm functioning perfectly and ready to help! What dental questions do you have for me?",
            "I'm excellent, thanks! As an AI assistant, I'm always here and ready to provide information about dental imaging and the ByteDent platform. What would you like to know?",
            "I'm doing well! More importantly, how can I help you today with your dental imaging or dental health questions?",
        ]
        return random.choice(responses)

    def _random_thanks_response(self) -> str:
        """Generate a random thank you response"""
        responses = [
            "You're very welcome! Feel free to ask if you have any more questions about dental imaging or dental health.",
            "Happy to help! Don't hesitate to reach out if you need anything else.",
            "My pleasure! I'm always here if you have more questions about ByteDent or dental topics.",
            "You're welcome! Is there anything else you'd like to know about dental imaging or the ByteDent platform?",
            "Glad I could help! Feel free to ask if you have any other questions.",
        ]
        return random.choice(responses)

    def _random_goodbye_response(self) -> str:
        """Generate a random goodbye response"""
        responses = [
            "Goodbye! Take care, and feel free to come back anytime you have dental imaging questions.",
            "See you later! Stay healthy, and don't hesitate to reach out if you need help with ByteDent.",
            "Have a great day! Remember, I'm here whenever you need information about dental imaging or dental health.",
            "Take care! Come back anytime you have questions about dental imaging or the ByteDent platform.",
            "Farewell! Wishing you the best dental health. See you next time!",
        ]
        return random.choice(responses)

    def _handle_small_talk(self, talk_type: str) -> str:
        """Handle specific small talk topics"""
        responses = {
            'name': "I'm the ByteDent AI Assistant! I'm an artificial intelligence designed to help answer questions about dental imaging, CBCT scans, dental procedures, and the ByteDent platform. You can just call me ByteDent!",

            'age': "I'm a newly developed AI assistant! The ByteDent chatbot was created in 2026 by our talented development team. While I'm relatively new, I'm built on advanced AI technology and dental knowledge to provide you with accurate information.",

            'creator': "I was created by the ByteDent development team! The team includes Yazan Maksoud (Product Owner & Project Manager), Raneem Rabah (Mobile App Developer & AI Engineer), Ahmad Bashir (AI Engineer & Research Lead), and Rama Shrebati (Backend Developer). Ahmad led much of the AI research and technical development, while the entire team collaborated to bring me to life!",

            'purpose': "My purpose is to assist with questions about dental imaging, dental procedures, and the ByteDent platform! I can explain:\n\n• What CBCT and panoramic X-rays are\n• Dental conditions and pathologies\n• Treatment procedures like cavity treatment and root canals\n• How to use the ByteDent app for uploading and analyzing dental images\n• Information about our AI analysis capabilities\n\nI'm here to provide educational information and help you understand dental imaging better!",

            'capabilities': "I can help you with many dental-related topics! Here's what I can do:\n\n✓ Explain dental imaging (CBCT, panoramic X-rays)\n✓ Answer questions about dental conditions and treatments\n✓ Guide you through the ByteDent app workflow\n✓ Provide information about our AI analysis features\n✓ Explain dental terminology and concepts\n✓ Tell you about the development team\n\nFor specific medical advice, pricing, or personal diagnoses, I'll connect you with a human specialist. What would you like to know?",
        }

        return responses.get(talk_type, "I'm not sure how to answer that, but I'm happy to help with dental imaging questions!")


# Global instance
_conversational_handler = None


def get_conversational_handler() -> ConversationalHandler:
    """Get the global conversational handler instance"""
    global _conversational_handler
    if _conversational_handler is None:
        _conversational_handler = ConversationalHandler()
    return _conversational_handler
