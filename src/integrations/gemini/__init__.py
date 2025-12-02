import base64
import json
import os

from google import genai
from google.genai import types


class Gemini:
    """
    Uma classe para integrar com a API do Gemini (Google) para processar imagens
    e extrair metadados, além de gerar embeddings de texto.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Chave da API do Gemini não fornecida. "
                "Defina GEMINI_API_KEY nas variáveis de ambiente "
                "ou passe api_key explicitamente."
            )

        self.client = genai.Client(api_key=self.api_key)

        # Modelos padrão (ajuste se quiser outros)
        self.vision_model_name = "gemini-2.5-flash"
        self.embedding_model_name = "gemini-embedding-001"

    def process_image(self, image_base64: str) -> dict[str, any]:
        """
        Processa uma imagem (em base64) e retorna:
        {
          "title": "...",
          "description": "...",
          "keywords": ["...", "...", ...]
        }

        :param image_base64: string base64 da imagem. Pode ser só o base64
                             ou um data URL completo (data:image/...;base64,...)
        """
        # Permite receber uma data URL completa ou apenas o base64
        if image_base64.startswith("data:"):
            # Ex.: "data:image/jpeg;base64,AAAA..."
            image_base64 = image_base64.split(",", 1)[1]

        try:
            image_bytes = base64.b64decode(image_base64)

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",  # ajuste se receber PNG/WebP etc
            )

            prompt = (
                "Analise esta imagem e gere um título, uma descrição e uma lista de "
                "palavras-chave relevantes. "
                "Retorne a resposta estritamente no seguinte formato JSON, "
                "sem nenhum texto adicional antes ou depois: "
                '{"title": "seu_titulo", "description": "sua_descricao", '
                '"keywords": ["palavra1", "palavra2", "palavra3"]}'
            )

            # Configurando para receber JSON puro
            config = types.GenerateContentConfig(response_mime_type="application/json")

            response = self.client.models.generate_content(
                model=self.vision_model_name,
                contents=[image_part, prompt],
                config=config,
            )

            response_text = response.text  # Deve ser um JSON puro
            json_data = json.loads(response_text)

            # Validação básica
            if not all(k in json_data for k in ("title", "description", "keywords")):
                raise ValueError("A resposta da API não contém as chaves esperadas (title, description, keywords).")

            return json_data

        except json.JSONDecodeError:
            print(f"Erro ao decodificar a resposta JSON da API. Resposta recebida: {response_text}")
            raise ValueError("A resposta da API não é um JSON válido.")
        except Exception as e:
            print(f"Ocorreu um erro ao processar a imagem com o Gemini: {e}")
            raise ValueError("Erro ao processar a imagem com o Gemini")

    def get_embedding(self, text: str) -> list[float]:
        """
        Gera um embedding para o texto usando o modelo de embedding do Gemini.
        Retorna uma lista de floats.
        """
        try:
            result = self.client.models.embed_content(
                model=self.embedding_model_name,
                contents=text,
            )

            # result.embeddings é uma lista; pegamos o primeiro objeto
            embedding_obj = result.embeddings[0] if result.embeddings else dict()
            return list(embedding_obj.values)
        except Exception as e:
            print(f"Erro ao gerar embedding com o Gemini: {e}")
            raise ValueError("Erro ao gerar embedding com o Gemini")
