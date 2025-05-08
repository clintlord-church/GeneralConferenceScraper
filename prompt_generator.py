import json
import requests
import re

# Function to send request to LM Studio and get the topic prompt
def get_topic_prompt(talk_text):
    prompt = (
        "Read the talk below and determine the topic of the talk. Then respond with a prompt that looks like this "
        "'Write me a talk about ...' and replace the ... with the topic of the talk:\n\n" + talk_text
    )
    payload = {
        #"model": "gpt-3.5-turbo",  # Adjust model name as needed
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }
    try:
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        raw_content = response.json()["choices"][0]["message"]["content"].strip()
        # Remove the "thinking" portion if present
        cleaned_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
        return cleaned_content
    except requests.RequestException as e:
        print(f"Error communicating with LM Studio: {e}")
        return None

# Main processing loop
def process_conference_talks(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(output_file, "w", encoding="utf-8") as outfile:
        for line in infile:
            try:
                record = json.loads(line.strip())
                response_text = record.get("response")
                if not response_text:
                    print("Skipping record with missing response")
                    continue
                
                # Get the topic prompt from LM Studio
                topic_prompt = get_topic_prompt(response_text)
                if not topic_prompt:
                    print("Skipping record due to LM Studio error")
                    continue
                
                # Create new training data record
                training_record = {
                    "prompt": topic_prompt,
                    "completion": response_text
                }
                
                # Write to output file
                json.dump(training_record, outfile, ensure_ascii=False)
                outfile.write("\n")
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON line: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error processing record: {e}")
                continue

if __name__ == "__main__":
    input_file = "conference_talks.jsonl"
    output_file = "training_data.jsonl"
    process_conference_talks(input_file, output_file)
    print(f"Processing complete. Output written to {output_file}")