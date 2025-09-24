import json
import os
from typing import Any, Literal

from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from huggingface_hub import login
from transformers import AutoTokenizer

load_dotenv()
if os.getenv("HF_TOKEN") is None:
    raise ValueError("HF_TOKEN not found in the environment variables")
login(token=os.getenv("HF_TOKEN"))


class PDFParser:
    def __init__(
        self, pdf_path: str, output_path: str, output_type: Literal["json", "markdown"]
    ):
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.output_type = output_type
        self.tokenizer = AutoTokenizer.from_pretrained(
            os.getenv("BI_ENCODER_MODEL_NAME"), cache_dir=os.getenv("CACHE_DIR")
        )

    def parse(self):
        """
        parse the pdf file
        :return:
        """
        converter = DocumentConverter()
        doc = converter.convert(self.pdf_path)
        return doc

    def get_table_of_contents(self, doc: Any):
        """
        get the table of contents and page number from the parsed document
        :param doc:
        :return:
        """
        table_of_contents = {}
        parsed_dict = self.get_parsed_json(doc)
        texts = parsed_dict.get("texts", [])
        for text in texts:
            if text.get("label") == "section_header":
                prov = text.get("prov", [])
                if prov:
                    start_page = None
                    for p in prov:
                        start_page = p.get("page_no")
                        break
                    table_of_contents[text.get("text")] = {
                        "start_page": start_page,
                        "text_contents": [],
                    }
        return table_of_contents

    @staticmethod
    def get_parsed_json(doc: Any):
        """
        get the parsed json from the document
        :param doc:
        :return:
        """
        return doc.document.export_to_dict()

    @staticmethod
    def get_parsed_markdown(doc: Any):
        """
        get the parsed markdown from the document
        :param doc:
        :return:
        """
        return doc.document.export_to_markdown()

    def consolidate_text(self, doc: Any):
        """
        used to consolidate the all text inside a title/subtitle from the parsed document
        :param doc:
        :return:
        """
        parsed_dict = self.get_parsed_json(doc)
        table_of_contents = self.get_table_of_contents(doc)
        cur_page_header = None
        for text in parsed_dict.get("texts", []):
            if text.get("label", "") == "section_header":
                cur_page_header = text.get("text")
            if (
                cur_page_header is not None
                and text.get("label", "") != "section_header"
                and text.get("text", "") != ""
            ):
                table_of_contents[cur_page_header]["text_contents"].append(
                    text.get("text")
                )
        return table_of_contents

    def count_tokens(self, input_text: str):
        """
        used to count the number of tokens in the input text using the model's tokenizer
        :param input_text: sentence/paragraph
        :return:
        """
        encoded_input = self.tokenizer(input_text)
        input_ids = encoded_input["input_ids"]
        token_count = len(input_ids)
        return token_count

    def form_tokenizer_specific_content(self, parsed_content: dict):
        """
        used to adjust the parsed content to fit the context window of the model
        :param parsed_content:
        :return:
        """
        adjusted_content = {}
        for title, content in parsed_content.items():
            text_contents = content.get("text_contents", [])
            if len(text_contents) == 1:
                adjusted_content[title] = content
            else:
                accumulated_text = ""
                accumulated_token_count = 0
                accumulated_text_contents = []
                spill_over_flag = False
                for text in text_contents:
                    token_count = self.count_tokens(text)
                    if accumulated_token_count + token_count > int(
                        os.getenv("CONTEXT_WINDOW")
                    ):
                        accumulated_text_contents.append(accumulated_text)
                        accumulated_text = text
                        accumulated_token_count = token_count
                        spill_over_flag = True
                    else:
                        if accumulated_text == "":
                            accumulated_text += text
                        else:
                            accumulated_text += ". " + text
                        accumulated_token_count += token_count
                        spill_over_flag = False
                if spill_over_flag:
                    accumulated_text_contents.append(accumulated_text)
                else:
                    accumulated_text_contents.append(accumulated_text)
                adjusted_content[title] = {
                    "start_page": content.get("start_page"),
                    "text_contents": accumulated_text_contents,
                }
        return adjusted_content

    def save(self):
        """
        save the parsed document to a file(json, markdown) in the output path
        :return:
        """
        doc = self.parse()
        if self.output_type == "json":
            with open(
                f"{self.output_path}/table_of_contents.json", "w", encoding="utf-8"
            ) as f:
                json.dump(
                    self.get_table_of_contents(doc), f, ensure_ascii=False, indent=4
                )
            with open(
                f"{self.output_path}/parsed_output.json", "w", encoding="utf-8"
            ) as f:
                json.dump(self.get_parsed_json(doc), f, ensure_ascii=False, indent=4)
            with open(
                f"{self.output_path}/consolidated_parsed_output.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(self.consolidate_text(doc), f, ensure_ascii=False, indent=4)

            with open(f"{self.output_path}/consolidated_parsed_output.json", "r") as f:
                parsed_content = json.load(f)
            with open(
                f"{self.output_path}/tokenizer_adjusted_parsed_output.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    self.form_tokenizer_specific_content(parsed_content=parsed_content),
                    f,
                    ensure_ascii=False,
                    indent=4,
                )

        elif self.output_type == "markdown":
            raise NotImplemented("Markdown yet to be implemented")
        else:
            raise ValueError("Invalid output type")
