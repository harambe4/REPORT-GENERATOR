import os
import pdfplumber
from docx import Document
from openai import OpenAI
import yaml

current_path = os.path.dirname(os.path.abspath(__file__))


def transcribe_audio(audio) -> str:
    # Transcribe audio file using OpenAI Whisper
    client = OpenAI()

    transcription = client.audio.transcriptions.create(model="whisper-1", file=audio)

    return transcription.text


def extract_text_from_docx(docx) -> str:
    # Load Word document from file name

    doc = Document(docx)
    paragraphs = [p.text for p in doc.paragraphs]
    # Extract paragraphs
    paragraphs = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # Extract tables
    tables_text = []
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells)
            tables_text.append(row_text)

    tables_text = "\n".join(tables_text)

    # Combine content
    result_text = (
        f"{paragraphs}\n\nTables:\n{tables_text}" if tables_text else paragraphs
    )

    return result_text


def extract_text_from_pdf(file) -> str:
    # Load PDF file from file path
    reader = pdfplumber.open(file)
    data = "\n".join(
        [page.extract_text() for page in reader.pages if page.extract_text()]
    )
    return data


def extract_prompts(yaml_dir, model_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, yaml_dir), "r") as file:
        prompts = yaml.safe_load(file)
        return prompts[f"report_generation_{model_name}"]


def fill_prompt_template(prompt_template, replacements):
    filled_prompt = prompt_template
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"  # Convert key to {{KEY}} format
        filled_prompt = filled_prompt.replace(placeholder, value)
    return filled_prompt
