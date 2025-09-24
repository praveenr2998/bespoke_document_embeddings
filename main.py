import json
from parser.docling_parser import PDFParser

from question_generator.generate_questions import GenerateQuestions

if __name__ == "__main__":
    pdf_parser = PDFParser(pdf_path="parser/data/AWQ.pdf", output_path="parser/output/", output_type="json")
    pdf_parser.save()

    with open("parser/output/tokenizer_adjusted_parsed_output.json", "r") as f:
        parsed_content = json.load(f)
    generate_questions = GenerateQuestions(parsed_content=parsed_content)
    parsed_content_with_questions = generate_questions.generate_questions()
    with open(
        "question_generator/output/parsed_content_with_questions.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            parsed_content_with_questions,
            f,
            ensure_ascii=False,
            indent=4,
        )
