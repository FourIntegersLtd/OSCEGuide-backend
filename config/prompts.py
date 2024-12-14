FEEDBACK_PROMPT = """
    Carefully evaluate the medical consultation transcript.

    For EACH category:
    1. Assign a score (R/A/G)
    2. Provide a DIRECT quote from the transcript supporting your score
    3. Be specific and evidence-based

    Scoring Guide:
    - Green (G): Excellent performance, clear strengths
    - Amber (A): Some good elements, areas for improvement
    - Red (R): Significant concerns, needs substantial development

    Transcript:
    {transcript}

    Output Instructions:
    - Every field MUST have a score and supporting phrase
  
    """
