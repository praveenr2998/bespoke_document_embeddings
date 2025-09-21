from parser.docling_parser import PDFParser

if __name__ == "__main__":
    pdf_parser = PDFParser(pdf_path="parser/data/AWQ.pdf", output_path="parser/output/", output_type="json")
    pdf_parser.save()