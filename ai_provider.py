from abc import ABC, abstractmethod

class AIProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str | None:
        pass

class GeminiAIProvider(AIProvider): #Communicate with Gemini

    def generate(self, prompt :str) -> str | None:
        from google import genai
        from google.genai import types

        with genai.Client(
            http_options=types.HttpOptions(
                timeout=30000, # 30 sec time limit
                retry_options=types.HttpRetryOptions(attempts=1), # Dont Retry, Push to Ai Analaysis 
                )
            ) as client:
                response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            disable=True
                 )
            )    
         )
        return response.text