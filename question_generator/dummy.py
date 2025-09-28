import json
import re


def extract_dict_from_text(text_with_json):
    """
    Extracts a dictionary from a string containing JSON data.

    This function takes a string as input, attempts to parse it as JSON,
    and returns the resulting Python dictionary. It can handle JSON wrapped
    in markdown code blocks.

    Args:
        text_with_json: A string containing a well-formed JSON object,
                       optionally wrapped in markdown code blocks.

    Returns:
        A Python dictionary if parsing is successful.
        None if the string is not valid JSON.
    """
    try:
        # First, try to extract JSON from markdown code blocks
        json_match = re.search(
            r"```(?:json)?\s*\n(.*?)\n```", text_with_json, re.DOTALL
        )
        if json_match:
            json_text = json_match.group(1).strip()
        else:
            # If no code blocks found, use the original text
            json_text = text_with_json.strip()

        # Use json.loads() to parse the JSON string into a Python object
        dictionary = json.loads(json_text)
        return dictionary
    except json.JSONDecodeError as e:
        # Handle cases where the string is not valid JSON
        print(f"An error occurred while decoding JSON: {e}")
        return None


# Example usage with the text you provided:
input_text = """
BLAVJSHXSKIBSBBH
kkdsbclajsblkjd

```json
{
  "questions": [
    "What are the two main categories of quantization methods for deep learning models, and how do they differ?",
    "How does the reconstruction process in GPTQ lead to an over-fitting issue, and what are the implications for preserving generalist abilities of LLMs?",
    "What is the main advantage of using low-bit weight-only quantization (W4A16) over W8A8 quantization for LLMs, and how does it impact hardware efficiency?",
    "What is the purpose of the activation-aware weight quantization (AWQ) approach, and how does it improve the performance of LLMs under INT3-g128 quantization?",
    "What are some system supports for low-bit quantized LLMs, and how do they address the limitations of traditional quantization methods?"
  ]
}
```

adiubldblsdbcilsdbc
"""

# Call the function and store the result
extracted_data = extract_dict_from_text(input_text)

# Print the extracted dictionary to see the result
if extracted_data:
    print("Successfully extracted dictionary:")
    # Using json.dumps for a formatted print
    print(json.dumps(extracted_data, indent=2))
    print(f"\nThe type of the extracted data is: {type(extracted_data)}")
