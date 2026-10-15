
import os

from flask import Flask, render_template, request
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)

# Read the secret key from the .env file.
api_key = os.getenv("GROQ_API_KEY")

# Create the Groq client only when a key is configured.
client = Groq(api_key=api_key) if api_key else None


@app.route("/", methods=["GET", "POST"])
def home():
    generated_content = ""
    error_message = ""

    # Default form values
    topic = ""
    content_type = "Blog Post"
    tone = "Professional"
    length = "Medium"

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()
        content_type = request.form.get("content_type", "Blog Post")
        tone = request.form.get("tone", "Professional")
        length = request.form.get("length", "Medium")

        # Basic input validation
        allowed_types = [
            "Blog Post",
            "Social Media Caption",
            "Product Description"
        ]
        allowed_tones = [
            "Professional",
            "Friendly",
            "Creative",
            "Simple"
        ]
        allowed_lengths = ["Short", "Medium", "Long"]

        if not topic:
            error_message = "Please enter a topic."
        elif len(topic) > 500:
            error_message = "Please keep your topic under 500 characters."
        elif (
            content_type not in allowed_types
            or tone not in allowed_tones
            or length not in allowed_lengths
        ):
            error_message = "Please select valid options."
        elif client is None:
            error_message = (
                "Groq API key is missing. Add GROQ_API_KEY to your .env file."
            )
        else:
            prompt = f"""
Create content using these requirements:

Content type: {content_type}
Topic: {topic}
Tone: {tone}
Length: {length}

Write original, useful content that follows these requirements.
Return only the generated content, with clear formatting.
"""

            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful content-writing assistant. "
                                "Follow the user's content requirements."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_completion_tokens=1200
                )

                generated_content = (
                    response.choices[0].message.content or ""
                ).strip()

                if not generated_content:
                    error_message = "The AI returned an empty response."

             
            except Exception as e:
                app.logger.exception("Groq API request failed.")
                error_message = f"Error: {type(e).__name__}: {e}"


    return render_template(
        "index.html",
        topic=topic,
        content_type=content_type,
        tone=tone,
        length=length,
        generated_content=generated_content,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
