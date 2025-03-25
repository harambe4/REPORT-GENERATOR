import streamlit as st
import anthropic
from utils import (
    transcribe_audio,
    extract_text_from_docx,
    extract_text_from_pdf,
    fill_prompt_template,
    extract_prompts,
)

client = anthropic.Anthropic()


def process_notes(notes):
    if notes.name.endswith(".docx"):
        input_notes = extract_text_from_docx(notes)
    elif notes.name.endswith(".m4a"):
        input_notes = transcribe_audio(notes)
    return input_notes


def process_document(document):
    if document.name.endswith(".docx"):
        input_document = extract_text_from_docx(document)
    elif document.name.endswith(".pdf"):
        input_document = extract_text_from_pdf(document)
    return input_document


def main():
    st.title("Report Generator vDemo 1.0")
    st.write("Welcome to the report generator Demo!")
    notes = st.file_uploader(
        "## **Upload Notes in Word or Audio format**", type=["m4a", "wav", "docx"]
    )
    reference = st.file_uploader("## **Upload References**", type=["pdf"])
    example = st.file_uploader("## **Upload Example**", type=["pdf", "docx"])
    if st.button("Generate Report") and notes and example:
        with st.spinner("Processing files..."):
            try:
                input_notes = process_notes(notes)
                reference_text = extract_text_from_pdf(reference)
                example_text = process_document(example)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
            st.subheader("Notes Preview")
            st.markdown(input_notes[0:250] + "...")

            prompt_template = extract_prompts(("report_prompts.yaml"), "claude")
            replacements = {
                "INPUT_NOTES": input_notes,
                "REFERENCE_PDF": reference_text,
                "EXAMPLE_REPORT": example_text,
            }
            instructions = fill_prompt_template(prompt_template, replacements)

        # Create the report using Claude
        with st.spinner("Generating report..."):
            try:
                message = client.messages.create(
                    model="claude-3-7-sonnet-20250219",
                    max_tokens=4000,
                    temperature=0.5,
                    system="Your task is to review the provided notes and create a report following guidelines and example report provided",
                    messages=[
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": instructions}],
                        }
                    ],
                )
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        st.download_button(
            label="Download Report",
            data=message.content[0].text,
            file_name="rapport_evaluation.md",
            mime="text/plain",
        )
        st.success("Report generated successfully!")


if __name__ == "__main__":
    main()
