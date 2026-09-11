from openai import OpenAI

from config import Config
from services.format_rules import clean_ai_text, with_format_rules


class OpenAIService:

    def __init__(self):

        self.client = None

        self.model = Config.OPENAI_MODEL

        if Config.OPENAI_API_KEY:

            self.client = OpenAI(

                api_key=Config.OPENAI_API_KEY

            )

    # --------------------------------------------------

    def available(self):

        return self.client is not None

    # --------------------------------------------------

    def generate(

        self,

        system_prompt,

        user_prompt

    ):

        if not self.available():

            return {

                "success": False,

                "error": "OPENAI_API_KEY no configurada."

            }

        try:

            response = self.client.responses.create(

                model=self.model,

                input=[

                    {

                        "role": "system",

                        "content": with_format_rules(system_prompt)

                    },

                    {

                        "role": "user",

                        "content": user_prompt

                    }

                ]

            )

            return {

                "success": True,

                "content": clean_ai_text(response.output_text)

            }

        except Exception as e:

            return {

                "success": False,

                "error": str(e)

            }