from transformers import pipeline

def summarize_texts(texts):
    try:
        # Combine and preprocess input texts
        comments_combined = " ".join(texts)
        comments_cleaned = comments_combined.replace("However,", "However, ").strip()

        # Check if input is long enough
        if len(comments_cleaned.split()) < 50:
            return "The feedback is too short to generate a meaningful summary."

        # Summarize using the pipeline
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary_raw = summarizer(comments_cleaned, max_length=50, min_length=10, do_sample=False)[0]['summary_text']

        # Post-process the summary to improve readability
        if "However," in summary_raw:
            parts = summary_raw.split("However,")
            refined_summary = f"Students appreciate {parts[0].strip()}. However, {parts[1].strip()}."
        else:
            refined_summary = summary_raw

        return refined_summary
    except Exception as e:
        return f"Error generating summary: {str(e)}"
