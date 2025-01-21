import json
from datetime import datetime
import os

async def jsonify_prompt(responses):
    """
    Convert a list of LLM responses into JSON format and save to a timestamped file.

    Args:
        responses (list): List of LLM response objects containing chat_message attributes
                         with JSON content strings

    Returns:
        list: List of parsed JSON objects from the responses

    The function:
    1. Converts each response's chat_message content into a JSON object
    2. Creates a 'generation_log' directory if it doesn't exist 
    3. Saves raw responses to a timestamped JSON file in the format:
       'generated_data_dict_YYYYMMDDHHMM.json'
    4. Returns the parsed JSON objects from the responses

    Example:
        responses = [Response(chat_message=Message(content='{"key": "value"}'))]
        json_objects = await jsonify_prompt(responses)
        # Creates file: generated_data_dict_202401201430.json
        # Returns: [{"key": "value"}]
    """
    # Turn list of LLM responses into list of JSON objects
    json_response = [json.loads(responses[index].chat_message.content) for index in range(len(responses))]
    
    # Create directory if it doesn't exist
    directory = 'generation_log'
    os.makedirs(directory, exist_ok=True)
    
    # Generate timestamp in yyyymmddhhmm format
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    filename = f"Log_{timestamp}.log"
    
    # Combine directory and filename
    filepath = os.path.join(directory, filename)
    
    # Save each dictionary in the list
    with open(filepath, 'w') as f:
        # Write opening bracket for JSON array
        f.write('[\n')
        
        # Write each dictionary
        for i, item in enumerate(json_response):
            json.dump(item, f, indent=4)
            if i < len(json_response) - 1:
                f.write(',\n')
            else:
                f.write('\n')
                
        # Write closing bracket
        f.write(']')
        
    print(f"Data saved to: {filepath}")
    return json_response, filepath  # Return filename for reference