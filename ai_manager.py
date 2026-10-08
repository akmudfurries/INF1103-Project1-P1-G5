#   Setup (Once):
#   pip install google-genai
#   setx GEMINI_API_KEY "your-key"   (free key from aistudio.google.com)

import json
from config import ALLOWED_ANSWERS, MAX_RETRIES


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
    client = genai.Client()   # reads GEMINI_API_KEY
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )
    return response.text

def extract_ai_response(ai_reply: str): # Turns Answer into a Dict
    text = ai_reply.replace("```json", "") #Replace JSON block
    text = text.replace("```", "")
    text = text.strip()
    try:
        answer = json.loads(text) # Change AI text to dictionary
    except json.JSONDecodeError:
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
        if ai_response.lower() not in ALLOWED_ANSWERS[question]: # Check if its the allowed Value
            return False, question + " has an invalid answer: " + ai_response
        
    if "reason" not in answer or str(answer["reason"]).strip() == "": # Missing reason
        return False, "missing reason"

    return True, "no error"

def get_ai_analysis(item: dict, ask_function=ask_gemini): # Runs every step
    prompt = ai_prompt(item)
    issue = ""
    for cycle in range(MAX_RETRIES + 1):
        try:
            ai_reply = ask_function(prompt)
        except Exception as error:
            issue = "could not reach AI: " + str(error)
            continue 
        answer = extract_ai_response(ai_reply)
        if answer is None:
            issue = "AI reply was not valid JSON"
            continue
        valid, issue = check_ai_response(answer)
        if valid:
            return answer, "" # No Error
    return None, "AI failed after retries: " + issue

