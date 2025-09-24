from openai import OpenAI

from question_generator.prompts import system_prompt, user_prompt

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="praveen@123",
)


def get_llm_response(content: str):
    """
    used to generate 5 questions based on the given content
    """
    completion = client.chat.completions.create(
        model="meta-llama/Llama-3.2-3B-Instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt.format(content=content)},
        ],
        temperature=0,
    )

    return completion.choices[0].message.content
