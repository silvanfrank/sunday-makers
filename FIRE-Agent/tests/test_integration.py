"""
Integration Tests for FIRE Agent.
Focus: "Wiring" - ensuring data flows correctly between components.
"""
import unittest
from execution.data_mapper import build_roadmap_context

class TestIntegration(unittest.TestCase):
    
    def test_build_roadmap_context_basic(self):
        """Test that data mapper correctly wraps projection data."""
        # Mock projection data (calculator output)
        mock_data = {
            "status": "success",
            "current_age": 40,
            "fire_number": 1000000
        }
        
        # Run mapper
        result = build_roadmap_context(mock_data)
        
        # Verify output structure for generate_fire_roadmap
        # Expected: {'data': mock_data}
        self.assertIn('data', result)
        self.assertEqual(result['data'], mock_data)
        self.assertEqual(result['data']['current_age'], 40)

if __name__ == '__main__':
    unittest.main()
