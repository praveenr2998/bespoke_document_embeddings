import os
import json
import uuid
import chromadb
import torch
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.losses import MultipleNegativesRankingLoss
from datasets import Dataset
from tqdm import tqdm
from huggingface_hub import login

if os.getenv("HF_TOKEN") is None:
    raise ValueError("HF_TOKEN not found in the environment variables")
login(token=os.getenv("HF_TOKEN"))

class BiEncoderTrainer:
    def __init__(self):
        chroma_client = chromadb.PersistentClient(path="db")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.collection = chroma_client.get_or_create_collection(name="doc_embeddings")
        self.model = SentenceTransformer(os.getenv("BI_ENCODER_MODEL_NAME"), cache_folder=os.getenv("CACHE_DIR")).to(device=self.device)


    def embed_text(self, sentence: str):
        return self.model.encode(sentence)

    def upload_embeddings(self):
        parsed_content_with_questions = None
        with open("question_generator/output/parsed_content_with_questions.json", "r") as f:
            parsed_content_with_questions = json.load(f)

        if parsed_content_with_questions:
            for title, content in tqdm(parsed_content_with_questions.items(), desc="Uploading document embeddings"):
                text_with_questions = content.get("text_with_questions", [])
                for text_with_question in text_with_questions:
                    text_content = text_with_question.get("text_content")
                    if text_content:
                        self.collection.add(
                            documents=[text_content],
                            embeddings=self.embed_text(text_content),
                            metadatas=[{"title": title}],
                            ids=[str(uuid.uuid4())]
                        )

    def prepare_training_data(self):
        parsed_content_with_questions = None
        training_data = []
        with open("question_generator/output/parsed_content_with_questions.json", "r") as f:
            parsed_content_with_questions = json.load(f)

        for title, content in tqdm(parsed_content_with_questions.items(), desc="Preparing training data"):
            text_with_questions = content.get("text_with_questions", [])
            for text_with_question in text_with_questions:
                questions = text_with_question.get("questions", [])
                text_content = text_with_question.get("text_content")
                for question in questions:
                    query_results = self.collection.query(
                        query_embeddings=self.embed_text(question),
                        n_results=5
                    )
                    fetched_documents = query_results["documents"][0]
                    fetched_documents = [doc for doc in fetched_documents if doc != text_content]
                    fetched_documents = fetched_documents[::-1][-3:]
                    for document in fetched_documents:
                        if document != text_content:
                            training_data.append({"anchor": question, "positive": text_content, "negative": document})

        with open("model_trainer/training_data/training_data.json", "w") as f:
            json.dump(training_data, f)

    def train(self):
        training_data = None
        with open("model_trainer/training_data/training_data.json", "r") as f:
            training_data = json.load(f)

        if training_data:
            train_dataset = Dataset.from_list(training_data)
            loss = MultipleNegativesRankingLoss(self.model)

            args = SentenceTransformerTrainingArguments(
                # Required parameter:
                output_dir="models/finetuned_bi_encoder",
                # Optional training parameters:
                # prompts=self.model.prompts[task_name],  # use model's prompt to train
                num_train_epochs=5,
                per_device_train_batch_size=1,
                learning_rate=2e-5,
                warmup_ratio=0.1,
                # Optional tracking/debugging parameters:
                logging_steps=train_dataset.num_rows,
                report_to="none",
            )

            trainer = SentenceTransformerTrainer(
                model=self.model,
                args=args,
                train_dataset=train_dataset,
                loss=loss,
            )
            trainer.train()


obj = BiEncoderTrainer()
obj.upload_embeddings()
obj.prepare_training_data()
obj.train()
