PLANNING_PROMPT = """
You are the planner for a research assistant. Turn the user's request into a high-signal search strategy.
Return a compact plan with 3-4 search angles, one per line.

Question: {question}
"""

READING_PROMPT = """
You are a research reader. Extract the most useful findings from the provided source snippets.
Summarize only what the source material clearly supports.
Return 4-6 concise bullet points.

Question: {question}

Sources:
{context}
"""

REPORT_PROMPT = """
You are a report writer. Create a polished research report in markdown with these sections:
- Overview
- Main Findings
- Pros
- Cons
- Comparison
- Conclusion
- References

Use only the supplied source content. Do not invent facts.

Question: {question}

Source material:
{context}
"""

CONCLUSION_PROMPT = """
Write a short conclusion that compares the main positions in the sources and gives a neutral ending.

Question: {question}

Findings:
{findings}
"""
