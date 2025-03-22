import streamlit as st
import anthropic
from utils import (
    transcribe_audio,
    extract_text_from_docx_notes,
    extract_text_from_pdf,
    fill_prompt_template,
    extract_prompts,
)

client = anthropic.Anthropic()


def process_notes(notes):
    if notes.name.endswith(".docx"):
        input_notes = extract_text_from_docx_notes(notes)
    elif notes.name.endswith(".m4a"):
        input_notes = transcribe_audio(notes)
    return input_notes


def main():
    st.title("Report Generator v1.0")
    st.write("Welcome to the report generator Demo!")
    notes = st.file_uploader(
        "Upload Notes in Word or Audio format", type=["m4a", "wav", "docx"]
    )
    reference = st.file_uploader("Upload References", type=["pdf", "docx"])
    example = st.file_uploader("Upload Example", type=["pdf", "docx"])
    if st.button("Generate Report") and notes:
        with st.spinner("Processing files..."):
            try:
                input_notes = process_notes(notes)
                reference_text = extract_text_from_pdf(reference)
                example_text = extract_text_from_docx_notes(example)
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()
            st.subheader("Notes Preview")
            st.markdown(input_notes[0:500])

            prompt_template = extract_prompts(("report_prompts.yaml"), "claude")
            replacements = {
                "INPUT_NOTES": input_notes,
                "REFERENCE_PDF": reference_text,
                "EXAMPLE_REPORT": example_text,
            }
            instructions = fill_prompt_template(prompt_template, replacements)

            # Create the report using Claude
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

            st.download_button(
                label="Download Notes",
                data=message.content[0].text,
                file_name="rapport_evaluation.md",
                mime="text/plain",
            )
            st.success("Report generated successfully!")


if __name__ == "__main__":
    main()
