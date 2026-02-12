import unittest
import sys
from pathlib import Path

# Add parent dir to sys.path so we can import 'execution'
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_tests():
    test_dir = Path(__file__).parent
    print(f"🔍 Running tests in {test_dir}")
    
    # Use standard discovery which respects setUp/tearDown
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        print("\n❌ Tests Failed")
        sys.exit(1)
    else:
        print("\n✅ All Tests Passed")
        sys.exit(0)

if __name__ == "__main__":
    run_tests()
