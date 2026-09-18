"""
Unit Tests for Conversational Dialogue Manager and Memory.
"""

import unittest
from core.dialogue_manager import DialogueManager

class TestDialogueManager(unittest.TestCase):
    def setUp(self):
        self.dm = DialogueManager()

    def test_incomplete_input_clarification(self):
        """
        Test that ambiguous/incomplete input triggers clarifying questions as demonstrated in the document:
        User: 'Biodiversity is declining on my land'
        System: Asks for soil organic carbon, rainfall pattern, land use.
        """
        turn1 = self.dm.process_turn("Biodiversity is declining on my land")
        self.assertEqual(turn1["status"], "awaiting_clarification")
        self.assertFalse(turn1["is_complete"])
        self.assertGreater(len(turn1["missing_parameters"]), 0)
        self.assertIn("could you please provide", turn1["response_text"])

    def test_multi_turn_conversation_with_memory(self):
        """
        Test that providing missing parameters in turn 2 resolves the incomplete state
        and completes the multi-metric analysis.
        """
        # Turn 1: Incomplete
        turn1 = self.dm.process_turn("Biodiversity is declining on my land")
        session_id = turn1["session_id"]
        self.assertEqual(turn1["status"], "awaiting_clarification")

        # Turn 2: Follow-up with missing parameters
        turn2 = self.dm.process_turn(
            "Rainfall is low, soil organic carbon is 0.3%, and we cultivate monoculture wheat in a semi-arid region.",
            session_id=session_id
        )

        self.assertEqual(turn2["status"], "completed")
        self.assertTrue(turn2["is_complete"])
        self.assertIsNotNone(turn2["analysis"])
        self.assertIn("Multi-Strata Agroforestry", turn2["response_text"])

if __name__ == "__main__":
    unittest.main()
