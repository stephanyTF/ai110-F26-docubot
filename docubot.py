"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob
import re #added for punctuation handling

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Split documents into sections: List of (filename, section_text)
        self.sections = self.split_all_sections(self.documents)

        # Build a retrieval index over sections (implemented in Phase 1)
        self.index = self.build_index(self.sections)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Section Splitting
    # -----------------------------------------------------------

    def split_sections(self, filename, text)-> :
        """
        Splits one document into sections.
        Markdown files split before each heading; any section without
        headings (e.g. .txt files) falls back to blank-line paragraphs.
        Returns a list of (filename, section_text).
        """
        parts = re.split(r"(?m)^(?=#{1,3} )", text)
        sections = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.startswith("#"):
                sections.append((filename, part))
            else:
                # No heading: split into paragraphs
                for para in re.split(r"\n\s*\n", part):
                    if para.strip():
                        sections.append((filename, para.strip()))
        return sections

    def split_all_sections(self, documents):
        """Splits every document into sections."""
        sections = []
        for filename, text in documents:
            sections.extend(self.split_sections(filename, text))
        return sections

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, sections):
        """
        Build a tiny inverted index mapping lowercase words to the sections
        they appear in.

        Example structure:
        {
            "token": {0, 5},      # indexes into self.sections
            "database": {12}
        }
        """
        index = {}
        for section_id, (filename, text) in enumerate(sections):
            tokens = re.findall(r"\w+", text.lower())  # words only, no punctuation
            for token in tokens:
                if token not in index:
                    index[token] = set()  # Use a set to avoid duplicates
                index[token].add(section_id)

        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        TODO (Phase 1):
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        #include stop words list to skip insignficant query words
        stop_words_lst = ["is", "the", "and", "can", "at", "an", "what", "how", "does", "do","the", "a", "which", "where", 'i']
       
       #1. Create a count var 
        count = 0
        query_words = query.lower().split()
        text_words = re.findall(r"\w+", text.lower()) #turns into word list and strips punctuation

        #2. Count how many query words appear in the text
        for word in query_words:
            if word in text_words and word not in stop_words_lst:
                count += 1

        return count

    def retrieve(self, query, top_k=3):
        """
        TODO (Phase 1):
        Use the index and scoring function to select top_k relevant document snippets.

        Return a list of (filename, text) sorted by score descending.
        """
        scored_lst = []

        #1. Use the index to find candidate sections containing any query word
        candidate_ids = set()
        for word in re.findall(r"\w+", query.lower()):
            candidate_ids |= self.index.get(word, set())

        #2. Score each candidate section using score_document()
        for section_id in candidate_ids:
            filename, text = self.sections[section_id]
            score = self.score_document(query, text)
            if score > 1: #add guardrail to avoid low quality answers
                scored_lst.append((score,filename,text))
        #3. Sort the list of tuples by the descending score
        scored_lst.sort(key=lambda item: item[0], reverse=True)
        #4. Use top_k to find the first k number of files and append that file and text as a tuple into the results list
        results = [(filename, text) for _, filename, text in scored_lst[:top_k]]


        return results

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets: 
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
