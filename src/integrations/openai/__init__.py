import json
import os

import openai


class OpenAI:
    """
    Uma classe para integrar com a API da OpenAI para processar imagens e extrair metadados.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Chave da API da OpenAI não fornecida ou encontrada na variável de ambiente OPENAI_API_KEY."
            )
        self.client = openai.OpenAI(api_key=self.api_key)

    def process_image(self, base64_image: str) -> dict[str, any]:
        try:
            prompt_messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Analyze the image (meme). "
                                "Identify which meme it is (if it is a famous one), describe what is happening visually "
                                "and generate tags for search. "
                                "Answer only in JSON, with the fields: "
                                "`title` (a short, catchy title in Portuguese), "
                                "`description` (a concise description of what happens in the meme, in Portuguese), and "
                                "`keywords` (a list of 5 to 10 keywords in Portuguese, including emotions, objects, famous names, and one vibe tag such as "
                                '"Engraçado", "Irônico", "Triste", "Fofo", etc.).'
                            ),
                        },
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    ],
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o",  # Modelo mais recente com capacidade de visão
                messages=prompt_messages,
                max_tokens=300,
                response_format={"type": "json_object"},  # Solicita a saída em formato JSON
            )

            response_content = response.choices[0].message.content

            # O response_format="json_object" garante que o conteúdo seja uma string JSON válida
            json_data = json.loads(response_content)

            # Validação básica da estrutura do JSON retornado
            if not all(key in json_data for key in ["title", "description", "keywords"]):
                raise ValueError("A resposta da API não contém as chaves esperadas (title, description, keywords).")

            return json_data

        except FileNotFoundError as fnf_error:
            print(f"Erro de arquivo: {fnf_error}")
            raise
        except openai.APIError as api_error:
            print(f"Erro na API da OpenAI: {api_error}")
            raise
        except json.JSONDecodeError:
            print(f"Erro ao decodificar a resposta JSON da API. Resposta recebida: {response_content}")
            raise ValueError("A resposta da API não é um JSON válido.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            raise

    def get_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
