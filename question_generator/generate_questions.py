import json
import re

from tqdm import tqdm

from question_generator.llm_utils import get_llm_response


class GenerateQuestions:
    def __init__(self, parsed_content: dict):
        self.parsed_content = parsed_content

    @staticmethod
    def extract_dict_from_text(text_with_json: str):
        """
        Extracts a dictionary from a string containing JSON data.

        This function takes a string as input, attempts to parse it as JSON,
        and returns the resulting Python dictionary. It can handle JSON wrapped
        in markdown code blocks.

        Args:
            text_with_json: A string containing a well-formed JSON object,
                           optionally wrapped in markdown code blocks.

        Returns:
            A Python dictionary if parsing is successful.
            None if the string is not valid JSON.
        """
        try:
            # First, try to extract JSON from markdown code blocks
            json_match = re.search(
                r"```(?:json)?\s*\n(.*?)\n```", text_with_json, re.DOTALL
            )
            if json_match:
                json_text = json_match.group(1).strip()
            else:
                # If no code blocks found, use the original text
                json_text = text_with_json.strip()

            # Use json.loads() to parse the JSON string into a Python object
            dictionary = json.loads(json_text)
            if isinstance(dictionary, dict):
                return dictionary
            return None
        except json.JSONDecodeError as e:
            # Handle cases where the string is not valid JSON
            print(f"An error occurred while decoding JSON: {e}")
            return None

    def generate_questions(self):
        """
        Generate questions for each text content in the parsed content.
        :return:
        """
        parsed_content_with_questions = {}
        for title, content in tqdm(
            self.parsed_content.items(), desc="Generating questions"
        ):
            parsed_content_with_questions[title] = {
                "start_page": content.get("start_page"),
                "text_with_questions": [],
            }
            text_contents = content.get("text_contents", [])
            for text_content in text_contents:
                raw_llm_response = get_llm_response(content=text_content)
                structured_llm_response = self.extract_dict_from_text(
                    text_with_json=raw_llm_response
                )
                if structured_llm_response is not None:
                    questions = structured_llm_response.get("questions", [])
                    if questions:
                        parsed_content_with_questions[title][
                            "text_with_questions"
                        ].append({"text_content": text_content, "questions": questions})
                    else:
                        parsed_content_with_questions[title][
                            "text_with_questions"
                        ].append({"text_content": text_content})
                else:
                    parsed_content_with_questions[title]["text_with_questions"].append(
                        {"text_content": text_content}
                    )
        return parsed_content_with_questions

    def retry_failed_question_generation(self, parsed_content_with_questions: dict):
        """
        Retry failed question generation for each text content in the parsed content.
        :param parsed_content_with_questions: parsed content with LLM generated questions
        :return:
        """
        for title, content in tqdm(
            parsed_content_with_questions.items(),
            desc="Retrying failed question generation",
        ):
            text_with_questions = content.get("text_with_questions", [])
            for idx in len(text_with_questions):
                if not text_with_questions[idx].get("questions"):
                    text_content = text_with_questions[idx].get("text_content")
                    raw_llm_response = get_llm_response(content=text_content)
                    structured_llm_response = self.extract_dict_from_text(
                        text_with_json=raw_llm_response
                    )
                    if structured_llm_response is not None:
                        questions = structured_llm_response.get("questions", [])
                        if questions:
                            parsed_content_with_questions[title]["text_with_questions"][
                                idx
                            ]["questions"] = questions
        return parsed_content_with_questions

    @staticmethod
    def check_question_generation_completion(parsed_content_with_questions: dict):
        """
        used to check if all questions are generated for each text content in the parsed content.
        :param parsed_content_with_questions:
        :return:
        """
        for title, content in parsed_content_with_questions.items():
            text_with_questions = content.get("text_with_questions", [])
            for text_content in text_with_questions:
                if not text_content.get("questions"):
                    return False
        return True

    def orchestrate_questions_generation(self):
        """
        Orchestrates the questions generation process.
        :return:
        """
        parsed_content_with_questions = self.generate_questions()
        retry_count = 0
        while retry_count < 3:
            if self.check_question_generation_completion(parsed_content_with_questions):
                break
            parsed_content_with_questions = self.retry_failed_question_generation(
                parsed_content_with_questions
            )
            retry_count += 1
        return parsed_content_with_questions
