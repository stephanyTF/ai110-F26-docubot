# DocuBot Model Card

This model card is a short reflection on your DocuBot system. Fill it out after you have implemented retrieval and experimented with all three modes:

1. Naive LLM over full docs  
2. Retrieval only  
3. RAG (retrieval plus LLM)

Use clear, honest descriptions. It is fine if your system is imperfect.

---

## 1. System Overview

**What is DocuBot trying to do?**  
Describe the overall goal in 2 to 3 sentences.

> The DocuBot helps find the right information that best answers the user's questions related to one or more of the four technical files. It's meant to give appropiate answers and avoids giving and answering non relevant information.

**What inputs does DocuBot take?**  
For example: user question, docs in folder, environment variables.

> A user question (free-style written form)

**What outputs does DocuBot produce?**

> For non llm models, it returned a piece of text from one of the files if there was a relevant enough answer. For llm models, it returns a short summary and says what file its answer is based on.

---

## 2. Retrieval Design

**How does your retrieval system work?**  
Describe your choices for indexing and scoring.

- How do you turn documents into an index?
- How do you score relevance for a query?
- How do you choose top snippets?

> - Documents are turned into an index by first being split into sections and then each unique word is put into the index with its corresponding filename and section.
> - Query are scored for relevancy by how many of the query words appear in the text
> - The top snippest are chosen by highest score and the top_k (default = 3).

**What tradeoffs did you make?**  
For example: speed vs precision, simplicity vs accuracy.

>Leaning toward simplicity vs accuracy. Eventhough we narrowed down the sources from files to section and removed common / stop words to avoid adding noise, there's a lack of weighing which words are actually relevant or even if the query shows up in the title as well. This is because due to time. 

---

## 3. Use of the LLM (Gemini)

**When does DocuBot call the LLM and when does it not?**  
Briefly describe how each mode behaves.

- Naive LLM mode:
- Retrieval only mode:
- RAG mode:

> Naive LLM mode: The LLM answers with no context of the files
>

**What instructions do you give the LLM to keep it grounded?**  
Summarize the rules from your prompt. For example: only use snippets, say "I do not know" when needed, cite files.

> Avoids giving low scoring information and falls back to "not knowing enough information" and always cite files when applicable. 

---

## 4. Experiments and Comparisons

Run the **same set of queries** in all three modes. Fill in the table with short notes.

You can reuse or adapt the queries from `dataset.py`.

| Query | Naive LLM: helpful or harmful? | Retrieval only: helpful or harmful? | RAG: helpful or harmful? | Notes |
|------|---------------------------------|--------------------------------------|---------------------------|-------|
| Example: Where is the auth token generated? |Not helpful (asks more specific questions) | Not helpful | Not helpful | Section provided is not the best associated with the query |
| Example: How do I connect to the database? | helpful but risky (provides info but not grounded in docs) | helpful| helpful| With llm and retrieval, clear and right info |
| Example: Which endpoint lists all users? |harmful info provided is different from the API_REFERENCE.md doc| Not helpful | helpful|With llm and retrieval, clear and right info |
| Example: How does a client refresh an access token? | helpful but risky (provides info but not grounded in docs) | Not helpful | helpful| With llm and retrieval, clear and right info|

**What patterns did you notice?**  

- When does naive LLM look impressive but untrustworthy?  
- When is retrieval only clearly better?  
- When is RAG clearly better than both?

> Naive LLM looks impressive when it gives a confident answer but untrustworthy because it's not grounded in the docs.
> Retrieval is clearly better when the question is straightforward and can be found easily in the files
> RAG is clearly better when it can answer the query directly using relevant info from the docs.
---

## 5. Failure Cases and Guardrails

**Describe at least two concrete failure cases you observed.**  
For each one, say:

- What was the question?  
- What did the system do?  
- What should have happened instead?

> Failure case 1: Where is the auth token generated?
> The system returns that it doesn't know even though the answer is in the AUTH.md Token Generation section

> Failure case 2: Which fields are stored in the users table?
> the system fails to know eventhough the answer is in the DATABASE.md Tables section.

**When should DocuBot say “I do not know based on the docs I have”?**  
Give at least two specific situations.

> The DocuBot should admit limited knowledge when the query can't be answered by the docs or the docs relevance score is too low.

**What guardrails did you implement?**  
Examples: refusal rules, thresholds, limits on snippets, safe defaults.

> Safe Defaults: “I do not know based on the docs I have” when score relevancy is low

---

## 6. Limitations and Future Improvements

**Current limitations**  
List at least three limitations of your DocuBot system.

1. Accuracy of responses
2. Rejecting unrelated questions
3. Lack following up in case the query could be reworded differently to get the intended answer

**Future improvements**  
List two or three changes that would most improve reliability or usefulness.

1. Weighing of key words in query to improve accuracy
2. Have the LLM recognize irrelvant questions and refuse to look thru the docs
3. Follow up w/ the user in case a legitimate question is turned down.

---

## 7. Responsible Use

**Where could this system cause real world harm if used carelessly?**  
Think about wrong answers, missing information, or over trusting the LLM.

> If not grounded in the docs, the LLM could give poor or malicious instructions that could harm the user or their software.

**What instructions would you give real developers who want to use DocuBot safely?**  
Write 2 to 4 short bullet points.

- Always ask clear and specific queries 
- Refrain from jail breaking unless implementing those safety features


---
