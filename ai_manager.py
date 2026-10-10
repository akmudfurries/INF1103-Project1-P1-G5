#   Setup (Once):
#   pip install google-genai
#   setx GEMINI_API_KEY "your-key"   (free key from aistudio.google.com)

import json
import time
from config import ALLOWED_ANSWERS, MAX_RETRIES

def ai_error(error): # Turns Gemini error into text
    text = str(error).lower()
    if "api key" in text:
        return "AI is not set up. Check your API key."
    if "503" in text or "unavailable" in text:
        return "Gemini is busy. Try again later."
    if "429" in text:
        return "AI usage limit reached. Try again later."
    if "timed out" in text or "timeout" in text:
        return "Gemini took too long to respond."
    return "Could not reach AI."

def ai_prompt(item: dict):
    prompt = "Read these inventory notes and answer with only a JSON object.\n"
    prompt = prompt + "Use exactly these keys and only these answers:\n"
    for question in ALLOWED_ANSWERS:
        prompt = prompt + " - " + question + ": one of " + ", ".join(ALLOWED_ANSWERS[question]) + "\n"
    prompt = prompt + " - reason: one short sentence explaining your answers\n\n"
    prompt = prompt + "Item: " + item["item_name"] + "\n"
    prompt = prompt + "Notes: " + item["operational_notes"] + "\n"
    return prompt

#Read these inventory notes and answer with ONLY a JSON object.
#Use exactly these keys and only these answers:
# - demand_level: one of low, medium, high
# - demand_trend: one of stable, increasing, decreasing
# - supply_risk: one of low, medium, high
# - operational_importance: one of low, medium, high
# - reason: one short sentence explaining your answers
#Item: Printer Ribbon
#Notes: Usage has gone up a lot and the supplier was late twice.

def ask_gemini(prompt: str): #Send the prompt to GEMINI.
    from google import genai
    from google.genai import types
    client = genai.Client(
        http_options=types.HttpOptions(
            timeout=30000, # 30 sec time limit
            retry_options=types.HttpRetryOptions(attempts=2) # Dont Retry, Push to Ai Analaysis 
            ),
        )   # Reads API key, 
    response = client.models.generate_content(
        # model="gemini-3.8-flash",
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )    )
    return response.text

def extract_ai_response(ai_reply: str): # Turns Answer into a Dict
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

def check_ai_response(answer: dict):
    for question in ALLOWED_ANSWERS: 

        if question not in answer: # Checks the answer
            return False, "missing " + question
        ai_response = answer[question]
        if type(ai_response) != str: # Check if got numbers 
            return False, question + " is not text"
        if ai_response.lower() not in ALLOWED_ANSWERS[question]: # Check if its the allowed value
            return False, question + " has an invalid answer: " + ai_response
        answer[question] = ai_response.lower() # Save as lowercase
        
    reason = answer.get("reason") 
    if not isinstance(reason, str) or not reason.strip(): # Not text or Empty return false
        return False, "missing reason"

    return True, "no error"

def get_ai_analysis(item: dict, ask_function=ask_gemini): # Runs every step
    prompt = ai_prompt(item)
    issue = ""
    for cycle in range(MAX_RETRIES + 1):
        try:
            ai_reply = ask_function(prompt)
        except Exception as error:
            issue = ai_error(error)

            if "503" in str(error) or "unavailable" in str(error).lower():
                if cycle < MAX_RETRIES:
                    time.sleep(2 * (cycle + 1))

            continue
        answer = extract_ai_response(ai_reply)
        if answer is None:
            issue = "AI reply was not valid JSON"
            continue
        valid, issue = check_ai_response(answer)
        if valid:
            return answer, "" # No Error
    return None, "AI failed after retries: " + issue

