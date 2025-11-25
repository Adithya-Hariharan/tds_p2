# main.py
import os
import sys
import io
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from groq import Groq

# --- CONFIGURATION ---

import os
from dotenv import load_dotenv # You might need to pip install python-dotenv

load_dotenv() # Load variables from .env

# Correct way (using the variable loaded from .env)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
# Initialize the App and AI
app = FastAPI()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

async def scrape_task(url: str) -> str:
    """Goes to the URL and grabs the visible text instructions."""
    print(f"Scraping {url}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(2000) # Wait for JS to load
        
        # Get the text
        content = await page.evaluate("document.body.innerText")
        await browser.close()
        return content

def solve_with_llm(task_text: str, email: str, secret: str):
    """Asks AI to write code to solve the task."""
    
    # We tell the AI to write a script that calculates the answer AND submits it.
    system_prompt = f"""
    You are an intelligent python bot.
    The user will give you text from a webpage containing a data task.
    
    YOUR GOAL:
    1. Understand the task.
    2. Write a Python script to calculate the answer.
    3. The script must output the answer inside a print statement.
    
    CRITICAL INFO:
    - The user email is: "{email}"
    - The secret key is: "{secret}"
    - If the task asks you to POST JSON to a URL, use the `requests` library to do it in your code.
    
    OUTPUT FORMAT:
    Return ONLY valid Python code inside ```python ``` blocks.
    """

    print("Asking AI to write code...")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the webpage text: \n{task_text}"}
        ],
        model="llama-3.3-70b-versatile", # Free, smart model on Groq
    )

    return chat_completion.choices[0].message.content

def execute_generated_code(code_str: str):
    """Extracts python code from AI response and runs it."""
    import re
    
    # Find code between ```python and ```
    match = re.search(r"```python(.*?)```", code_str, re.DOTALL)
    if not match:
        print("Error: AI did not return code blocks.")
        return "No code found"
    
    script = match.group(1).strip()
    
    print("--- GENERATED CODE START ---")
    print(script)
    print("--- GENERATED CODE END ---")
    
    # Execute the code safely-ish
    # We use subprocess to run it as a separate script to capture output easier
    try:
        # Write code to a temp file
        with open("temp_solution.py", "w") as f:
            f.write(script)
            
        # Run the file
        result = subprocess.run([sys.executable, "temp_solution.py"], capture_output=True, text=True)
        
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return result.stdout
    except Exception as e:
        return str(e)

@app.post("/quiz")
async def solve_quiz(request: QuizRequest):
    # 1. Scrape the URL
    task_text = await scrape_task(request.url)
    print(f"Instructions found: {task_text[:100]}...")
    
    # 2. Ask AI for Code
    llm_response = solve_with_llm(task_text, request.email, request.secret)
    
    # 3. Run the Code
    result = execute_generated_code(llm_response)
    
    return {"status": "done", "execution_result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)