import json
from typing import Any, Literal

from docling.document_converter import DocumentConverter


class PDFParser:
    def __init__(
        self, pdf_path: str, output_path: str, output_type: Literal["json", "markdown"]
    ):
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.output_type = output_type

    def parse(self):
        """
        parse the pdf file
        :return:
        """
        converter = DocumentConverter()
        doc = converter.convert(self.pdf_path)
        return doc

    @staticmethod
    def get_table_of_contents(doc: Any):
        table_of_contents = []
        for heading in doc.document.headings:
            table_of_contents.append(heading)
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

    def save(self):
        """
        save the parsed document to a file(json, markdown) in the output path
        :return:
        """
        doc = self.parse()
        if self.output_type == "json":
            with open(
                f"{self.output_path}/parsed_output.json", "w", encoding="utf-8"
            ) as f:
                json.dump(doc.export_to_dict(), f, ensure_ascii=False, indent=4)
        elif self.output_type == "markdown":
            raise NotImplemented("Markdown yet to be implemented")
        else:
            raise ValueError("Invalid output type")
