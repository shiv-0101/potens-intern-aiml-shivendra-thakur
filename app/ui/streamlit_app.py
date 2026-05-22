import streamlit as st
import requests
import json
from pathlib import Path
import os

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Research Paper RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# ─── Sidebar Navigation ────────────────────────────────────────────────────────

st.sidebar.title("📚 RAG Assistant")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "📄 Upload Documents", "❓ Ask Questions", "⚡ Contradiction Checker"]
)

# ─── Health Check ──────────────────────────────────────────────────────────────

def check_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.json()
    except Exception:
        return None

# ─── Page: Home ────────────────────────────────────────────────────────────────

if page == "🏠 Home":
    st.title("📚 Research Paper RAG Assistant")
    st.markdown("""
    ### AI-Powered Research Paper Question Answering
    
    This system allows you to:
    - 📄 **Upload** research papers (PDF)
    - ❓ **Ask** natural language questions
    - 📎 **Get** cited answers with source references
    - ⚡ **Detect** contradictions between papers
    - 🌍 **Query** in multiple languages
    """)
    
    st.markdown("---")
    
    # System Status
    st.subheader("System Status")
    health = check_health()
    
    if health:
        col1, col2, col3 = st.columns(3)
        col1.metric("Status", "✅ Online")
        col2.metric("Documents", health.get("documents_loaded", 0))
        col3.metric("Chunks", health.get("total_chunks", 0))
        
        if health.get("documents"):
            st.subheader("Loaded Documents")
            for doc in health["documents"]:
                st.markdown(f"- 📄 `{doc}`")
    else:
        st.error("❌ API not reachable. Make sure `python run.py api` is running.")

# ─── Page: Upload Documents ────────────────────────────────────────────────────

elif page == "📄 Upload Documents":
    st.title("📄 Upload Documents")
    
    tab1, tab2 = st.tabs(["Upload PDFs", "Ingest from Directory"])
    
    with tab1:
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("📥 Ingest Documents", type="primary"):
            # Save uploaded files to data/raw
            saved_paths = []
            for uploaded_file in uploaded_files:
                save_path = f"./data/raw/{uploaded_file.name}"
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_paths.append(save_path)
            
            with st.spinner("Ingesting documents... This may take a few minutes."):
                try:
                    r = requests.post(
                        f"{API_BASE}/ingest",
                        json={"file_paths": saved_paths},
                        timeout=300
                    )
                    result = r.json()
                    
                    if result.get("status") == "success":
                        st.success(f"✅ Successfully ingested {result['documents_processed']} documents!")
                        st.json(result)
                    else:
                        st.error(f"❌ Ingestion failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab2:
        st.info("Auto-ingest all PDFs from `data/raw/` directory")
        if st.button("🔄 Ingest from data/raw/", type="primary"):
            with st.spinner("Ingesting..."):
                try:
                    r = requests.post(f"{API_BASE}/ingest", json={}, timeout=300)
                    result = r.json()
                    st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")

# ─── Page: Ask Questions ───────────────────────────────────────────────────────

elif page == "❓ Ask Questions":
    st.title("❓ Ask Research Questions")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_area(
            "Your Question",
            placeholder="What is the transformer architecture? How does attention work?",
            height=100
        )
    
    with col2:
        language = st.selectbox(
            "Language",
            options=["en", "hi", "fr", "de", "es"],
            format_func=lambda x: {
                "en": "🇬🇧 English",
                "hi": "🇮🇳 Hindi",
                "fr": "🇫🇷 French",
                "de": "🇩🇪 German",
                "es": "🇪🇸 Spanish"
            }[x]
        )
        top_k = st.slider("Results", 1, 10, 5)
        use_reranker = st.checkbox("Use Reranker", value=True)
    
    if st.button("🔍 Ask", type="primary") and query:
        with st.spinner("Searching and generating answer..."):
            try:
                r = requests.post(
                    f"{API_BASE}/ask",
                    json={
                        "query": query,
                        "language": language,
                        "top_k": top_k,
                        "use_reranker": use_reranker
                    },
                    timeout=60
                )
                result = r.json()
                
                # Display answer
                st.markdown("---")
                
                if result.get("is_fallback"):
                    st.warning("⚠️ " + result["answer"])
                else:
                    st.subheader("📝 Answer")
                    st.markdown(result["answer"])
                
                # Confidence
                confidence = result.get("confidence", 0)
                st.metric("Confidence Score", f"{confidence:.2%}")
                
                # Citations
                citations = result.get("citations", [])
                if citations:
                    st.subheader(f"📎 Citations ({len(citations)})")
                    
                    for i, cite in enumerate(citations):
                        with st.expander(
                            f"📄 {cite['source_file']} — Page {cite['page']} "
                            f"(Score: {cite.get('similarity_score', 0):.3f})"
                        ):
                            st.markdown(f"**Chunk ID:** {cite['chunk_id']}")
                            st.markdown(f"**Snippet:**")
                            st.markdown(f"> {cite['snippet']}")
                
            except Exception as e:
                st.error(f"Error: {e}")

# ─── Page: Contradiction Checker ───────────────────────────────────────────────

elif page == "⚡ Contradiction Checker":
    st.title("⚡ Contradiction Checker")
    st.markdown("Detect conflicting claims between two research papers.")
    
    # Get available documents
    health = check_health()
    available_docs = health.get("documents", []) if health else []
    
    if not available_docs:
        st.warning("No documents loaded. Please upload documents first.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            doc1 = st.selectbox("Paper 1", options=available_docs)
        
        with col2:
            doc2 = st.selectbox("Paper 2", options=available_docs)
        
        topic = st.text_input(
            "Topic to Compare",
            placeholder="training efficiency, model accuracy, architecture..."
        )
        
        if st.button("⚡ Check for Contradictions", type="primary") and topic and doc1 != doc2:
            with st.spinner("Analyzing papers for contradictions..."):
                try:
                    r = requests.post(
                        f"{API_BASE}/contradict",
                        json={"doc1": doc1, "doc2": doc2, "topic": topic},
                        timeout=60
                    )
                    result = r.json()
                    
                    st.markdown("---")
                    
                    if result.get("conflict"):
                        st.error("⚡ Contradiction Detected!")
                    else:
                        st.success("✅ No significant contradiction found")
                    
                    st.subheader("Reasoning")
                    st.markdown(result.get("reasoning", ""))
                    
                    evidence = result.get("evidence", [])
                    if evidence:
                        st.subheader("Evidence")
                        for ev in evidence:
                            with st.expander(f"📄 {ev.get('source', 'Unknown')}"):
                                st.markdown(ev.get("claim", ev.get("snippet", "")))
                
                except Exception as e:
                    st.error(f"Error: {e}")
        
        elif doc1 == doc2:
            st.warning("Please select two different documents.")