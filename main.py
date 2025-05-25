import llm


gemini = llm.LLM()
response = gemini.generate("hello", verbose=True)
response = gemini.generate("i'm ago", verbose=True)