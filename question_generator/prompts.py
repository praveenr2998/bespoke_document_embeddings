system_prompt = "Your goal is to generate 5 question based on the given content and return a JSON object"
user_prompt = """
### **Prompt:**

You are an AI assistant designed to generate insightful questions from a given text.

**Your Task:**
Based *only* on the content provided below, generate exactly 5 distinct questions that cover the key concepts, methodologies, and outcomes described in the text.

**Content:**

```
{content}
```

**Constraints:**

1.  Generate exactly 5 questions.
2.  The questions must be based directly on the information within the provided content.
3.  Do NOT provide answers or any text other than the final JSON object.

**Required Output Format:**
Your entire response must be a single, valid JSON object. The object should contain a single key, `"questions"`, with a value that is a list of the 5 generated question strings.

**Example:**

```json
{{
  "questions": [
    "Question 1",
    "Question 2",
    "Question 3",
    "Question 4",
    "Question 5",
  ]
}}
```
"""
