import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq = Groq()

def classify_with_llm(log_msg):
    prompt = f'''Classify the log message into one of these categories:
    (1) Workflow Error, (2) Deprecation Warning.
    If you can't figure out a category, use "Unclassified".
    Only respond with the category name. No numbering or explanation.
    Log message: {log_msg}'''

    chat_completion = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    response = chat_completion.choices[0].message.content.strip()

    # Clean up: remove numbering like "(1) " or "(2) ", if any
    category = re.sub(r"^\(\d+\)\s*", "", response)
    
    # Ensure it's one of the known categories or mark as Unclassified
    valid_categories = ["Workflow Error", "Deprecation Warning", "Unclassified"]
    if category not in valid_categories:
        category = "Unclassified"

    return category, 0.9  # Approximate confidence

if __name__ == "__main__":
    print(classify_with_llm(
        "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active."))
    print(classify_with_llm(
        "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025"))
    print(classify_with_llm("System reboot initiated by user 12345."))