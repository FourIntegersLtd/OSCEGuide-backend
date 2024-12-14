import os
from dotenv import load_dotenv
from openai import OpenAI
import instructor
from anthropic import Anthropic


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

instructor_open_ai_client = instructor.from_openai(openai_client)
instructor_anthropic_ai_client = instructor.from_anthropic(anthropic_client)

