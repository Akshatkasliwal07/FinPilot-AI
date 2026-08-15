class MockLLM:

    def invoke(self, prompt):

        return """
        {
          "analysis": "Mock AI response for testing workflow",
          "confidence": 0.85,
          "status": "testing"
        }
        """