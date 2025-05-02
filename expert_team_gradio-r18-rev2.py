import gradio as gr
import ollama
import asyncio
import re

# Define possible team roles with enhanced descriptions
possible_roles = [
    {'name': 'Strategic Business Advisor',
     'description': "Analyzes from a business perspective, focusing on strategy, market opportunities, and risks. Ideal for understanding the big-picture implications.",
     'sub_prompt': "Analyze the situation from a high-level business perspective. Focus on strategic implications, market opportunities, and potential risks for a company. Consider long-term goals and competitive advantage when addressing the following:"},
    {'name': 'Technical Implementation Expert',
     'description': "Focuses on the 'how' - technical aspects, implementation challenges, and infrastructure. Best for understanding the practical execution.",
     'sub_prompt': "Explain the technical aspects and implementation challenges. Focus on the practicalities of execution, potential technical roadblocks, and necessary technologies or infrastructure related to:"},
    {'name': 'User Experience (UX) Advocate',
     'description': "Champions the user, focusing on usability, needs, and pain points. Essential for making sure solutions are user-friendly.",
     'sub_prompt': "Evaluate this from the user's perspective. Focus on usability, user needs, potential pain points, and how to optimize the experience for the end-user related to:"},
    {'name': 'Creative Innovation Catalyst',
     'description': "Generates new ideas and unconventional solutions. Great for brainstorming and exploring novel approaches.",
     'sub_prompt': "Think creatively and outside the box. Focus on generating innovative ideas, novel solutions, and unconventional approaches to:"},
    {'name': 'Risk Assessment Analyst',
     'description': "Identifies potential risks and downsides, focusing on negative consequences and mitigation. Crucial for anticipating problems.",
     'sub_prompt': "Identify and analyze potential risks and downsides. Focus on possible negative consequences, challenges, and mitigation strategies associated with:"},
    {'name': 'Ethical and Societal Impact Officer',
     'description': "Considers fairness, social responsibility, and broader societal impacts. Important for ensuring responsible and ethical outcomes.",
     'sub_prompt': "Consider the ethical and societal implications. Focus on fairness, social responsibility, potential biases, and the broader impact on society related to:"},
    {'name': 'Financial Efficiency Expert',
     'description': "Analyzes costs, ROI, and financial sustainability. Key for understanding the economic viability.",
     'sub_prompt': "Analyze the financial aspects and efficiency. Focus on costs, return on investment, resource optimization, and financial sustainability related to:"},
]

# Temperature Presets - descriptive names
temperature_presets = {
    "Cautious": 0.3, # Best for factual or sensitive topics
    "Balanced": 0.7, # Good for general use, moderate creativity
    "Creative": 0.9, # Ideal for brainstorming and idea generation
}

# Reorganized Model Options for Clarity and Readability
available_models = ['qwen:0.5b', 'smollm2:135m', 'gemma2:2b','llava:7b','dolphin-llama3:latest']
model_options = {model: model for model in available_models} # Using dict comprehension for clarity

evaluation_models = ['gemma2:2b', 'dolphin-llama3:latest'] # Limiting evaluation models for focused selection
evaluation_model_options = {model: model for model in evaluation_models}


# --- Utility Functions (Improved Structure) ---
async def generate_expert_response(question, role, model_name, temperature_setting):
    """
    Generates a response from a specified expert role using a given model and temperature.
    Handles potential errors and provides informative error messages.
    """
    temperature = temperature_presets.get(temperature_setting, 0.7) # Default to 'Balanced' if not found
    prompt = f"You are a {role['name']}. {role['sub_prompt']} {question}"
    try:
        ollama.temperature = temperature
        response = await asyncio.to_thread(ollama.chat, model=model_name, messages=[{'role': 'user', 'content': prompt}])
        print (response)
        return response['message']['content']
  
    except Exception as e:
        error_message = f"Error from {role['name']} ({model_name}): {e}"
        print(error_message) # Still print to console for debugging
        return f"Error occurred during response generation for {role['name']}. Please check console for details."


async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
    """
    Evaluates responses from different expert roles using a senior manager perspective.
    Extracts key elements like perfect answer and illustration prompt using regex for robustness.
    Provides detailed console output for debugging and monitoring.
    """
    temperature = temperature_presets.get(eval_temperature_setting, 0.7) # Default to 'Balanced'
    responses_text = "\n".join([f"{role_name} Response: {response}\n" for role_name, response in responses.items()])

    prompt = (
        "As the Senior Manager, please review and evaluate the following responses from junior managers based on clarity, relevance, depth of information, and practicality. "
        "Consider the target audience for each response (e.g., technical vs. general public).\n\n"
        f"{responses_text}\n"
        "Provide your evaluation and elaborate on the findings. Which response is the most compelling and why? Are there any responses that are misleading or inaccurate? "
        "Finally, provide a concise summary of the key takeaways.\n\n"
        "Also provide a perfect answer to the question. Lastly, craft a prompt to create a custom illustration depicting the key concepts and insights from the responses."
    )

    try:
        ollama.temperature = temperature
        evaluation_response = await asyncio.to_thread(ollama.chat, model=eval_model_name, messages=[{'role': 'user', 'content': prompt}])
        evaluation_content = evaluation_response['message']['content']

        perfect_answer_match = re.search(r"Perfect Answer:\s*\n\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)
        illustration_prompt_match = re.search(r"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)

        perfect_answer = perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found in evaluation."
        illustration_prompt = illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found in evaluation."

        print("\n--- Evaluation Details (Console Output) ---") # Clearer console output
        print("Perfect Answer:", perfect_answer)
        print("Illustration Prompt:", illustration_prompt)
        print("Full Evaluation Output:\n", evaluation_content) # Display full output for debugging
        print("--- End Evaluation Details ---")

        return evaluation_content, perfect_answer, illustration_prompt

    except Exception as e:
        error_message = f"Error during evaluation process: {e}"
        print(error_message)
        return "Error in evaluation. Please check console.", "Error extracting perfect answer.", "Error extracting illustration prompt."


# --- Gradio Interface Function ---
async def gradio_interface(question, role1, role2, role3, role4, model1, model2, model3, model4, eval_model, temp_setting1, temp_setting2, temp_setting3, temp_setting4, eval_temp_setting):
    """
    Main function for the Gradio interface.
    Handles user input, generates expert responses, evaluates them, and returns outputs for display.
    """
    selected_roles = [role1, role2, role3, role4]
    selected_models = [model1, model2, model3, model4]
    selected_temp_settings = [temp_setting1, temp_setting2, temp_setting3, temp_setting4]

    expert_responses = {}
    tasks = []

    for i in range(4):
        if selected_roles[i]:
            role = selected_roles[i]
            model_name = selected_models[i]
            temp_setting = selected_temp_settings[i]
            tasks.append(generate_expert_response(question, role, model_name, temp_setting)) # Using utility function

    results = await asyncio.gather(*tasks)

    k = 0 # Index to track results
    for i in range(4):
        if selected_roles[i]:
            role_name = selected_roles[i]['name']
            expert_responses[role_name] = results[k]
            k += 1

    evaluation_text, perfect_answer_text, illustration_prompt_text = await evaluate_responses(expert_responses, eval_model, eval_temp_setting) # Using utility function

    response_texts = [expert_responses.get(role['name'], "") if role else "" for role in selected_roles] # List comprehension for conciseness

    return *response_texts, evaluation_text, perfect_answer_text, illustration_prompt_text # Correct unpacking


# --- Gradio Interface Definition ---
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Pose your question here"), # More descriptive label
        gr.Dropdown(possible_roles, label="Expert Role 1", info="Choose the first Expert role."), # Added info
        gr.Dropdown(possible_roles, label="Expert Role 2", info="Choose the second Expert role."),
        gr.Dropdown(possible_roles, label="Expert Role 3", info="Choose the third Expert role."),
        gr.Dropdown(possible_roles, label="Expert Role 4", info="Choose the fourth Expert role."),
        gr.Dropdown(model_options, label="Model for Role 1", info="Select the language model for Expert 1."), # More descriptive labels and info
        gr.Dropdown(model_options, label="Model for Role 2", info="Select model for Expert 2."),
        gr.Dropdown(model_options, label="Model for Role 3", info="Select model for Expert 3."),
        gr.Dropdown(model_options, label="Model for Role 4", info="Select model for Expert 4."),
        gr.Dropdown(evaluation_model_options, label="Evaluation Model", info="Choose the model for senior manager evaluation."), # Specific evaluation model dropdown
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 1", info="Set approach for Expert 1 (Cautious, Balanced, Creative)."), # More descriptive temperature labels
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 2", info="Set approach for Expert 2."),
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 3", info="Set approach for Expert 3."),
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style  Role 4", info="Set approach for Expert 4."),
        gr.Dropdown(list(temperature_presets.keys()), label="Approach style ", info="Set approach for Senior Manager evaluation."),
        

    ],
    outputs=[
        gr.Textbox(label="Response from Expert 1"), # More descriptive output labels
        gr.Textbox(label="Response from Expert 2"),
        gr.Textbox(label="Response from Expert 3"),
        gr.Textbox(label="Response from Expert 4"),
        gr.Textbox(label="Senior Manager Evaluation", lines=10), # Increased lines for better readability
        gr.Textbox(label="Perfect Answer (from Evaluation)", lines=3), # Clarified label
        gr.Textbox(label="Illustration Prompt (from Evaluation)", lines=3), # Clarified label
    ],
    title="Ask the Experts: Multi-Perspective Response System", # More engaging title
    description="""
    This tool simulates a team of experts providing answers to your questions from different perspectives. 
    Select up to four expert roles, each with a specific focus (e.g., Strategic, Technical, UX, Ethical). 
    Choose language models and temperature settings for each expert and an evaluation model for the 'Senior Manager' who reviews all responses, provides a perfect answer, and suggests an illustration prompt.
    """, # More detailed and user-friendly description
    examples=[ # Example questions to guide users
        ["What are the benefits and risks of implementing AI in customer service?"],
        ["How can we improve user engagement with our mobile app?"],
        ["Discuss the ethical implications of using facial recognition technology."],
        ["Analyze the potential market for a new eco-friendly product."],
    ],
    live=False, # Consider setting to False for performance in some environments
)


if __name__ == "__main__":
    iface.launch()
