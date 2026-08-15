class MockLLM:

    def invoke(self, prompt):

        return """
        {
          "success": true,
          "message": "Mock AI response",
          "data": {
              "analysis": "This is a testing response.",
              "confidence": 0.85
          }
        }
        """