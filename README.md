# AI / ML

**What we’re testing:** how you wire LLM components end-to-end, your honesty about model limits, and whether your prompts and traces look like a person who thought about it rather than someone who copied a tutorial.

---

## Q1. Document Q&A with Citations

Build a RAG system over five or more documents of your choice. Any domain. Anything substantive (policy text, product docs, research papers, technical guides). The point is your retrieval, your chunking strategy, and your discipline about not letting the model hallucinate when the docs don’t cover the answer.

### REQUIRED
- Ingest, chunk, embed, and store the documents. Explain your chunking strategy in the README.
- An `/ask` endpoint that returns answers with citations. Each citation must include the source file, the chunk or page reference, and the snippet used.
- A `/contradict` endpoint that takes two document IDs and returns whether they conflict on a topic, with reasoning.
- A multilingual flow: a query in one language returns an answer in the same language. A translation step at the boundary is acceptable for the 24-hour version.
- A simple Streamlit or Gradio UI so we can try it without Postman.
- No silent hallucination. If the docs do not cover the question, the system must say so explicitly.
- Any vector store (Chroma, FAISS, pgvector). Any LLM with a free tier (Groq, Gemini, OpenAI free credits).

### STRETCH (OPTIONAL)
- A confidence score per answer with a human-in-the-loop gate when confidence falls below a threshold.
- A reranker layered on top of vector retrieval.
- An eval set of 10 Q&A pairs with ground truth, scored on retrieval at top-k.

---

## Q2. Triage Agent with Real Tool Calling

Build an agentic system that takes a free-text input (the input could be a complaint, a request, a ticket, you decide), and produces a structured triage decision. Use real tool calling, not a string-matching shortcut.

### REQUIRED
- **Input:** free text plus optional metadata.
- **Output:** `{ category, priority, next_tool, reasoning }`. You define four to six categories and a P0 / P1 / P2 priority scheme.
- Three callable tools that the agent picks from. You implement them as real functions. Examples: a lookup tool, an acknowledgment-drafting tool, a similar-past-input search tool. Pick what fits your problem framing.
- The full reasoning trace must be visible for every decision. Not just the final answer.
- An `/examples` folder with at least ten test inputs and the agent’s outputs.
- A “why” explanation field on every output. No silent magic.

### STRETCH (OPTIONAL)
- A low-confidence escalation path that calls a human-in-the-loop tool when the agent is unsure.
- Run the same ten examples through a baseline (single-prompt classifier) and report the numbers side by side.
- A small Streamlit UI that visualises the reasoning trace as a tree.