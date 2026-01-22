import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """
    Returns the initialized ChatGroq model.
    Reads GROQ_API_KEY from environment.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY not found in environment. Using mock/fallback if available.")
    
    # We use Llama 3.3 70B Versatile for high intelligence + good rate limits
    # Free tier: 30 RPM, 14,400 TPD
    return ChatGroq(
        temperature=0, 
        model_name="openai/gpt-oss-120b", 
        api_key=api_key
    )
