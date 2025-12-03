import base64
import json
import os

from google import genai
from google.genai import types


class Gemini:
    """
    A class to integrate with the Gemini API (Google) to process images and extract metadata, as well as generate text embeddings.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("The Gemini API key was not provided or found in the GEMINI_API_KEY environment variable.")

        self.client = genai.Client(api_key=self.api_key)
        self.vision_model_name = "gemini-2.5-flash"
        self.embedding_model_name = "gemini-embedding-001"

    def process_image(self, image_base64: str) -> dict[str, any]:
        """
        Process an image (in base64) and return:
        {
          "title": "...",
          "description": "...",
          "keywords": ["...", "...", ...]
        }

        :param image_base64: base64 string of the image. It could just be the base64
                             or a complete data URL (data:image/...;base64,...)
        """

        if image_base64.startswith("data:"):
            image_base64 = image_base64.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(image_base64)

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            )

            prompt = (
                "Analyze the image (meme). "
                "Identify which meme it is (if it is a famous one), describe what is happening visually "
                "and generate tags for search. "
                "Answer only in JSON, with the fields: "
                "`title` (a short, catchy title in Portuguese), "
                "`description` (a concise description of what happens in the meme, in Portuguese), and "
                "`keywords` (a list of 5 to 10 keywords in Portuguese, including emotions, objects, famous names, and one vibe tag such as "
                '"Engraçado", "Irônico", "Triste", "Fofo", etc.). '
            )

            config = types.GenerateContentConfig(response_mime_type="application/json")

            response = self.client.models.generate_content(
                model=self.vision_model_name,
                contents=[image_part, prompt],
                config=config,
            )

            response_text = response.text
            json_data = json.loads(response_text)

            if not all(k in json_data for k in ("title", "description", "keywords")):
                raise ValueError("The API response does not contain the expected keys (title, description, keywords).")

            return json_data

        except json.JSONDecodeError:
            print(f"Error decoding JSON response from API. Response received: {response_text}")
            raise ValueError("The API response is not valid JSON.")
        except Exception as e:
            print(f"An error occurred while processing the image with Gemini: {e}")
            raise ValueError("Error processing image with Gemini")

    def get_embedding(self, text: str) -> list[float]:
        """
        Generates an embedding for the text using the Gemini embedding model.
        Returns a list of floats.
        """
        try:
            result = self.client.models.embed_content(
                model=self.embedding_model_name,
                contents=text,
            )

            embedding_obj = result.embeddings[0] if result.embeddings else dict()
            return list(embedding_obj.values)
        except Exception as e:
            print(f"Error generating embedding with Gemini: {e}")
            raise ValueError("Error generating embedding with Gemini")
