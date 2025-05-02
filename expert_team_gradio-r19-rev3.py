import gradio as gr
import asyncio
import ollama
import re

# Define temperature presets
temperature_presets = {
    "Cautious": 0.1,
    "Balanced": 0.7,
    "Creative": 1.2
}

expert_role_descriptions = {
    "Strategic Business Advisor": "Analyze the potential benefits and challenges from a strategic business perspective, focusing on long-term goals and competitive advantage.",
    "Technical Implementation Expert": "Detail the technical aspects, implementation challenges, and solutions, considering current  infrastructure and data systems.",
    "Ethical and Societal Impact Officer": "Evaluate the ethical and societal implications, including  privacy, data security, bias in algorithms, and impact on  equity.",
    "Creative Innovation Catalyst": "Explore innovative and unconventional applications, focusing on how LLMs can revolutionize solutions to satisfy the needs of the prompt ."
}

async def generate_expert_responses(sub_prompt, expert_roles, expert_models, expert_temperature_settings):
    responses = {}
    for i, role_name in enumerate(expert_roles):
        model_name = expert_models[i]
        temperature_setting = expert_temperature_settings[i]
        approach_style = temperature_presets.get(temperature_setting, 0.7) # Default to 'Balanced'

        ollama.temperature = approach_style # Apply temperature setting here
        expert_prompt = expert_role_descriptions[role_name] + "\n---\n" + sub_prompt
        response_obj = await asyncio.to_thread(ollama.chat, model=model_name, messages=[{'role': 'user', 'content': expert_prompt}])
        responses[role_name] = response_obj['message']['content']
    return responses

async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
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

        # --- ADDED PRINT STATEMENT FOR RAW OUTPUT ---
        print(f"Raw Evaluation Content:\n{evaluation_content}")
        # --- END ADDED PRINT STATEMENT ---

        perfect_answer_match = re.search(r"\*\*Perfect Answer:\*\*\s*\n(.+?)(?=(\*\*Illustration Prompt:\*\*|\*\*Summary:\*\*|\*\*Evaluation:\*\*|\*\*Key Takeaways:\*\*|--- End Evaluation Details ---|$))", evaluation_content, re.DOTALL | re.IGNORECASE)
        illustration_prompt_match = re.search(r"\*\*Prompt for Custom Illustration:\*\*\s*\n(.+?)(?=(\*\*Summary:\*\*|\*\*Evaluation:\*\*|\*\*Key Takeaways:\*\*|--- End Evaluation Details ---|$))", evaluation_content, re.DOTALL | re.IGNORECASE)


        perfect_answer_text = perfect_answer_match.group(1).strip() if perfect_answer_match else "No Perfect Answer provided in evaluation." # More informative message
        illustration_prompt_text = illustration_prompt_match.group(1).strip() if illustration_prompt_match else "No Illustration Prompt provided in evaluation." # More informative message


        print (f"Perfect Answer: {perfect_answer_text}")
        print (f"Illustration Prompt: {illustration_prompt_text}")
        print ("--- End Evaluation Details ---")


        return [responses.get("Strategic Business Advisor", ""), responses.get("Technical Implementation Expert", ""),
                responses.get("Ethical and Societal Impact Officer", ""), responses.get("Creative Innovation Catalyst", ""),
                evaluation_content, perfect_answer_text, illustration_prompt_text]


    except Exception as e:
        error_message = f"Error during evaluation ({eval_model_name}): {e}"
        print(error_message) # Still print to console for debugging
        return ["", "", "", "", error_message,  "Evaluation Error", "Evaluation Error"]

def gradio_interface():
    expert_roles = ["Strategic Business Advisor", "Technical Implementation Expert", "Ethical and Societal Impact Officer", "Creative Innovation Catalyst"]
    expert_models_list = ["qwen:0.5b", "qwen:0.5b", "qwen:0.5b", "smollm2:135m"] # Default models
    temperature_options = ["Cautious", "Balanced", "Creative"]
    eval_models_list = ["gemma2:2b", "dolphin-llama3:latest", "llama2:13b"] # Evaluation models list


    iface = gr.Interface(
        fn=process_prompt,
        inputs=[
            gr.Textbox(lines=2, label="Enter your prompt for the expert team"),
            gr.Dropdown(expert_roles, value=expert_roles[0], label="Expert Role 1"),
            gr.Dropdown(expert_roles, value=expert_roles[1], label="Expert Role 2"),
            gr.Dropdown(expert_roles, value=expert_roles[2], label="Expert Role 3"),
            gr.Dropdown(expert_roles, value=expert_roles[3], label="Expert Role 4"),
            gr.Dropdown(expert_models_list, value=expert_models_list[0], label="Model for Role 1"),
            gr.Dropdown(expert_models_list, value=expert_models_list[1], label="Model for Role 2"),
            gr.Dropdown(expert_models_list, value=expert_models_list[2], label="Model for Role 3"),
            gr.Dropdown(expert_models_list, value=expert_models_list[3], label="Model for Role 4"),
            gr.Dropdown(temperature_options, value="Balanced", label="Approach style Role 1"),
            gr.Dropdown(temperature_options, value="Balanced", label="Approach style  Role 2"),
            gr.Dropdown(temperature_options, value="Balanced", label="Approach style  Role 3"),
            gr.Dropdown(temperature_options, value="Creative", label="Approach style  Role 4"),
            gr.Dropdown(eval_models_list, value=eval_models_list[0], label="Evaluation Model"),
            gr.Dropdown(temperature_options, value="Balanced", label="Approach style (Evaluation Model)")


        ],
        outputs=[
            strategic_advisor_output := gr.Textbox(label="Strategic Business Advisor Response", lines=5),
            technical_expert_output := gr.Textbox(label="Technical Implementation Expert Response", lines=5),
            ethical_officer_output := gr.Textbox(label="Ethical and Societal Impact Officer Response", lines=5),
            creative_catalyst_output := gr.Textbox(label="Creative Innovation Catalyst Response", lines=5),
            evaluation_output := gr.Textbox(label="Senior Manager Evaluation", lines=7),
            perfect_answer_output := gr.Textbox(label="Perfect Answer", lines=7),
            illustration_prompt_output := gr.Textbox(label="Illustration Prompt", lines=7)
        ],
        title="Expert Team Response Generator",
        description="Generate responses from a team of experts with different roles and evaluate their outputs."
    )
    return iface

async def process_prompt(prompt_text, role1, role2, role3, role4, model1, model2, model3, model4, temp_role1, temp_role2, temp_role3, temp_role4, eval_model_name, eval_temperature_setting):
    expert_roles = [role1, role2, role3, role4]
    expert_models = [model1, model2, model3, model4]
    expert_temperature_settings = [temp_role1, temp_role2, temp_role3, temp_role4]
    sub_prompt = prompt_text

    expert_responses = {}
    all_role_outputs = []  # To collect all outputs for return

    # --- ADDED PRINT STATEMENT: START OF EXPERT RESPONSE LOOP ---
    print ("--- START EXPERT RESPONSE GENERATION LOOP ---")
    # --- END ADDED PRINT STATEMENT ---


    for i, role_name in enumerate(expert_roles): # Enumerate to track index
        model_name = expert_models[i] # Get model based on index
        temperature_setting = expert_temperature_settings[i]
        approach_style = temperature_presets.get(temperature_setting, 0.7) # Default to 'Balanced'

        # --- ADDED PRINT STATEMENTS INSIDE LOOP ---
        print(f"  Role Index: {i}") # Print role index
        print(f"  Role Name: {role_name}") # Print role name
        print(f"  Model Name: {model_name}") # Print model name
        print(f"  Temperature Setting: {temperature_setting}") # Print temperature setting
        print(f"  Approach Style: {approach_style}") # Print approach style
        # --- END ADDED PRINT STATEMENTS ---


        ollama.temperature = approach_style # Apply temperature setting here
        expert_prompt = expert_role_descriptions[role_name] + "\n---\n" + sub_prompt
        response_obj = await asyncio.to_thread(ollama.chat, model=model_name, messages=[{'role': 'user', 'content': expert_prompt}])
        response_text = response_obj['message']['content']
        expert_responses[role_name] = response_text
        all_role_outputs.append(response_text) # Append to list in correct order


    # --- ADDED PRINT STATEMENT: END OF EXPERT RESPONSE LOOP ---
    print ("--- END EXPERT RESPONSE GENERATION LOOP ---")
    # --- END ADDED PRINT STATEMENT ---


    evaluation_results = await evaluate_responses(expert_responses, eval_model_name, eval_temperature_setting)
    # evaluation_content, perfect_answer_text, illustration_prompt_text = evaluation_results[4:7] # Extract evaluation text and prompts # THIS LINE COMMENTED OUT

    # --- ADDED PRINT STATEMENT: LOG ENTIRE evaluation_results ---
    print ("--- evaluation_results (entire list) ---")
    print (f"  Evaluation Results List: {evaluation_results}")
    # --- END ADDED PRINT STATEMENT ---


    evaluation_content, perfect_answer_text, illustration_prompt_text = evaluation_results[4:7] # Extract evaluation text and prompts # THIS LINE RE-ENABLED


    # --- ADDED PRINT STATEMENTS BEFORE GRADIO RETURN ---
    print ("--- BEFORE GRADIO RETURN ---")
    print (f"  Perfect Answer Text (before return): {perfect_answer_text}") # Print perfect_answer_text
    print (f"  Illustration Prompt Text (before return): {illustration_prompt_text}") # Print illustration_prompt_text
    # --- END ADDED PRINT STATEMENTS ---


    return [all_role_outputs[0], all_role_outputs[1], all_role_outputs[2], all_role_outputs[3],  # Expert responses
            evaluation_content, perfect_answer_text, illustration_prompt_text] # Evaluation outputs


iface = gradio_interface()

if __name__ == "__main__":
    iface.launch()
