import os

from dotenv import load_dotenv

from google import genai
from google.genai import types


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def ask_gemini(prompt):

    try:

        # Fast model for simple hospital department classification
        response = client.models.generate_content(

            model="gemini-3.5-flash-lite",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.1,

                max_output_tokens=80

            )

        )

        return response.text


    except Exception as e:

        print("Gemini Flash-Lite error:", e)


        # Fallback model
        response = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.1,

                max_output_tokens=80

            )

        )

        return response.text