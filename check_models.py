
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

try:
    client = Groq()
    models = client.models.list()

    print("\nAvailable models:")
    for model in models.data:
        print(model.id)

except Exception as e:
    print("Error:", type(e).__name__, str(e))
