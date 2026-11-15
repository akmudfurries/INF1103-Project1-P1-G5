#   Setup (Once):
#   pip install google-genai
#   setx GEMINI_API_KEY "your-key"   (free key from aistudio.google.com)

import json
import time

from ai_provider import AIProvider
from config import ALLOWED_ANSWERS, MAX_RETRIES
from models import InventoryRecord, AIAssessment
        
class AIManager():

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def ai_error(self, error : Exception) -> str: # Turns Gemini error into text

        text = str(error).lower()        
        if "api key" in text or "api_key" in text or "missing key" in text:
            return "AI is not set up. Check your API key."
        if "503" in text or "unavailable" in text:
            return "Gemini is busy. Try again later."
        if "429" in text:
            return "AI usage limit reached. Try again later."
        if "timed out" in text or "timeout" in text:
            return "Gemini took too long to respond."
        return "Could not reach AI."

    def build_prompt(self, item : InventoryRecord) -> str:
        prompt = (
            "Read these inventory notes and answer with only a JSON object.\n"
            "Use exactly these keys and only these answers:\n"
        )
        for question in ALLOWED_ANSWERS:
            prompt = prompt + " - " + question + ": one of " + ", ".join(ALLOWED_ANSWERS[question]) + "\n"
        prompt += " - reason: one short sentence explaining your answers\n\n"
        prompt += "Item: " + item.item_name + "\n"
        prompt += "Notes: " + item.operational_notes + "\n"
        return prompt

    def extract_response(self, ai_reply: str | None) -> dict | None: # Turns Answer into a Dict
        if not isinstance(ai_reply, str) or not ai_reply.strip(): # No reply or empty reply
            return None
        
        text = ai_reply.replace("```json", "") # Replace JSON block
        text = text.replace("```", "")
        text = text.strip()

        try:
            answer = json.loads(text) # Change AI text to dictionary
        except (json.JSONDecodeError, RecursionError):
            return None   
              
        if type(answer) != dict:
            return None
        return answer

    def validate_response(self, answer: dict) -> tuple[bool, str | None]:
        for question in ALLOWED_ANSWERS: 

            if question not in answer: # Checks the answer
                return False, "missing " + question
            ai_response = answer[question]

            if type(ai_response) != str: # Check if got numbers 
                return False, question + " is not text"

            ai_response = ai_response.strip().lower()
            
            if ai_response not in ALLOWED_ANSWERS[question]: # Check if its the allowed value
                return False, question + " has an invalid answer: " + ai_response
            
            answer[question] = ai_response
            
        reason = answer.get("reason") 
        if not isinstance(reason, str) or not reason.strip(): # Not text or Empty return false
            return False, "missing reason"

        return True, None

    def assess(self, item: InventoryRecord): # Runs every step
        prompt = self.build_prompt(item)
        issue = ""

        for cycle in range(MAX_RETRIES + 1):
            try:
                ai_reply = self.provider.generate(prompt)

            except Exception as error:
                issue = self.ai_error(error)
                text = str(error).lower()

                # Stops the program from retrying when the problem is a bad or missing API key
                if "api key" in text or "api_key" in text or "missing key" in text:
                    return None, issue   # retrying will never help

                if "503" in str(error) or "unavailable" in str(error).lower():
                    if cycle < MAX_RETRIES:
                        time.sleep(2 * (cycle + 1))

                continue

            answer = self.extract_response(ai_reply)

            if answer is None:
                issue = "AI reply was not valid JSON"
                continue

            valid, validation_issue = self.validate_response(answer)

            if not valid:
                issue = validation_issue or "AI reply failed validation."
                continue

            # Convert the checked answer into an assessment object.
            assessment = AIAssessment(
                demand_level=answer["demand_level"],
                demand_trend=answer["demand_trend"],
                supply_risk=answer["supply_risk"],
                operational_importance=answer["operational_importance"],
                reason=answer["reason"],
            )

            return assessment, None

        return None, "AI failed after retries: " + issue






