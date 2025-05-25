import base64
import os
import json
from google import genai
from google.genai import types


def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)


class LLM:
    def __init__(self, config_path="config.json"):
        with open(config_path) as f:
            config = json.load(f)
        api_key = config["gemini_api_key"]
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt, verbose=False, jsonOnly=True):
        model = "gemini-2.0-flash"
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=0.001,
            top_p=0.95,
            top_k=20,
            max_output_tokens=8192,
            response_modalities=["text"],
            response_mime_type="application/json" if jsonOnly else None,
        )
        response = ""
        for chunk in self.client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if (
                not chunk.candidates
                or not chunk.candidates[0].content
                or not chunk.candidates[0].content.parts
            ):
                continue

            part = chunk.candidates[0].content.parts[0]
            if part.inline_data:
                file_name = "chunks"
                save_binary_file(file_name, part.inline_data.data)
                print(
                    f"File of mime type {part.inline_data.mime_type} saved to: {file_name}"
                )
            else:
                if verbose:
                    print(chunk.text)
                response += chunk.text

        return json.loads(response) if jsonOnly else response
