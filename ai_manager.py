# AI Manager: asks Gemini to read an item's notes and returns validated answers.
#
# Setup (once per computer):
#   pip install google-genai
#   setx GEMINI_API_KEY "your-key"   (free key from aistudio.google.com)

#sample input item = {"TBC_item_name": "Printer Ribbon",
#        "TBC_operational_notes": "Usage has gone up a lot and the supplier was late twice."}

#sample output: ({'demand_level': 'high', 'demand_trend': 'increasing',
#'supplier_issue': 'significant', 'operational_importance': 'medium',
#'reason': 'Demand has grown rapidly and multiple late deliveries indicate a significant supplier problem.'}, '')


import json
from config import ALLOWED_ANSWERS, MAX_RETRIES


def ai_prompt(item: dict):
    prompt = "Read these inventory notes and answer with ONLY a JSON object.\n"
    prompt = prompt + "Use exactly these keys and only these answers:\n"
    for question in ALLOWED_ANSWERS:
        prompt = prompt + "- " + question + ": one of " + ", ".join(ALLOWED_ANSWERS[question]) + "\n"
    prompt = prompt + "- reason: one short sentence explaining your answers\n\n"
    prompt = prompt + "Item: " + item["item_name"] + "\n"
    prompt = prompt + "Notes: " + item["operational_notes"] + "\n"
    return prompt


#Read these inventory notes and answer with ONLY a JSON object.
#Use exactly these keys and only these answers:
#- demand_level: one of low, medium, high
#- demand_trend: one of decreasing, stable, increasing
#- supplier_issue: one of none, potential, significant
#- operational_importance: one of low, medium, high
#- reason: one short sentence explaining your answers
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

def extract_ai_response(ai_reply: str):
    text = ai_reply.replace("```json", "") #remove the json code block markers if present
    text = text.replace("```", "")
    text = text.strip()
    try:
        answer = json.loads(text) # Change AI text to dictionary
    except json.JSONDecodeError:
        return None         
    if type(answer) != dict:
        return None
    return answer

def check_ai_response(answer: dict): #key:value pair
    for question in ALLOWED_ANSWERS: #checks the Key if its define in the answer

        if question not in answer: #The AI response missing the qns 
            return False, "missing " + question
        ai_response = answer[question]
        if type(ai_response) != str: #check if got numbers 
            return False, question + " is not text"
        if ai_response.lower() not in ALLOWED_ANSWERS[question]: #check if the answer is in the values of the key
            return False, question + " has an invalid answer: " + ai_response
        
    if "reason" not in answer or str(answer["reason"]).strip() == "":
        return False, "missing reason"

    return True, "no error"

def get_ai_analysis(item: dict, ask_function=ask_gemini): #runs every by steps and retries if fail.
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
        ok, issue = check_ai_response(answer)
        if ok:
            return answer, ""
    return None, "AI failed after retries: " + issue

