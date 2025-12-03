from src.integrations.gemini import Gemini
from src.integrations.openai import OpenAI
from src.utils.func_retry import retry


class AlmanaqueAI:
    def __init__(self):
        self.openai = OpenAI()
        self.gemini = Gemini()

    def process_image(self, image: str):
        response = None
        try:
            response = retry(self.gemini.process_image, image)
        except Exception as e:
            print(f"Error processing image with Gemini: {e}")
            try:
                response = retry(self.openai.process_image, image)
            except Exception as e:
                print(f"Error processing image with OpenAI: {e}")
                raise Exception(f"Error processing image: {e}")
        return response

    def get_embedding(self, description: str):
        response = None
        try:
            response = retry(self.openai.get_embedding, description)
        except Exception as e:
            print(f"Error getting embedding with OpenAI: {e}")
            try:
                response = retry(self.gemini.get_embedding, description)
            except Exception as e:
                print(f"Error getting embedding with Gemini: {e}")
                raise Exception(f"Error getting embedding: {e}")
        return response
