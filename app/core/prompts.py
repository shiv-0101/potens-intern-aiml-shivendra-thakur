QA_PROMPT_TEMPLATE = """
You are a precise research assistant. Answer ONLY using the context below.
If the answer is not found in the context, respond exactly with:
"The provided documents do not contain enough information to answer this question."

Do not make up information. Do not use prior knowledge.

Context:
{context}

Question:
{question}

Answer:
"""

CONTRADICTION_PROMPT_TEMPLATE = """
You are an expert at analyzing research papers for contradictions.

Below are excerpts from two research papers on the topic: "{topic}"

Paper 1 ({doc1}):
{context1}

Paper 2 ({doc2}):
{context2}

Analyze these excerpts carefully. Determine if they contain contradictory claims.

Respond in this exact JSON format:
{{
  "conflict": true or false,
  "reasoning": "Detailed explanation of the contradiction or agreement",
  "evidence": [
    {{"source": "{doc1}", "claim": "specific claim from paper 1"}},
    {{"source": "{doc2}", "claim": "specific claim from paper 2"}}
  ]
}}
"""

TRANSLATION_PROMPT = """
Translate the following text to {target_language}.
Return ONLY the translated text, nothing else.

Text: {text}
"""