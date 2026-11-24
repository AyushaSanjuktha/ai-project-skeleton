from google import genai
from google.genai import types
from pydantic import BaseModel

from ai_project_skeleton.config import get_settings


# Define the expected JSON structure
class AIResponse(BaseModel):
    topic: str
    summary: str
    key_points: list[str]


def main():
    # Load API key securely from .env
    settings = get_settings()

    if not settings.api_key:
        raise ValueError("Gemini API key is missing!")

    client = genai.Client(api_key=settings.api_key.get_secret_value())

    # Call Gemini API
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Explain Python programming in simple English.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AIResponse,
        ),
    )

    # Validate Gemini's JSON response using Pydantic
    result = AIResponse.model_validate_json(response.text)

    # Display validated JSON
    print("\nValidated JSON Output:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
