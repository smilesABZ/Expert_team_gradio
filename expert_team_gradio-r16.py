import gradio as gr
import ollama
import asyncio
import re

# Define possible team roles
possible_roles = [
    {'name': 'Strategic Business Advisor', 'sub_prompt': "Analyze the situation from a high-level business perspective. Focus on strategic implications, market opportunities, and potential risks for a company. Consider long-term goals and competitive advantage when addressing the following:"},
    {'name': 'Technical Implementation Expert', 'sub_prompt': "Explain the technical aspects and implementation challenges. Focus on the practicalities of execution, potential technical roadblocks, and necessary technologies or infrastructure related to:"},
    {'name': 'User Experience (UX) Advocate', 'sub_prompt': "Evaluate this from the user's perspective. Focus on usability, user needs, potential pain points, and how to optimize the experience for the end-user related to:"},
    {'name': 'Creative Innovation Catalyst', 'sub_prompt': "Think creatively and outside the box. Focus on generating innovative ideas, novel solutions, and unconventional approaches to:"},
    {'name': 'Risk Assessment Analyst', 'sub_prompt': "Identify and analyze potential risks and downsides. Focus on possible negative consequences, challenges, and mitigation strategies associated with:"},
    {'name': 'Ethical and Societal Impact Officer', 'sub_prompt': "Consider the ethical and societal implications. Focus on fairness, social responsibility, potential biases, and the broader impact on society related to:"},
    {'name': 'Financial Efficiency Expert', 'sub_prompt': "Analyze the financial aspects and efficiency. Focus on costs, return on investment, resource optimization, and financial sustainability related to:"},
]

# Temperature Presets
temperature_presets = {
    "Cautious": 0.3,
    "Normal": 0.7,
    "Creative": 0.9,
}

# Function to generate responses
async def generate_response_with_expertise(question, role, model='qwen:0.5b', temperature_setting="Normal"):
    temperature = temperature_presets.get(temperature_setting, 0.7)
    prompt = f"You are a {role['name']}. {role['sub_prompt']} {question}"
    try:
        ollama.temperature = temperature
        response = await asyncio.to_thread(ollama.chat, model=model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"Error generating response from {role['name']}: {e}")
        return "Error occurred during response generation."

# Function to evaluate responses (Improved Extraction and Console Output)
async def evaluate_responses(responses, model='gemma2:2b', temperature_setting="Normal"):
    temperature = temperature_presets.get(temperature_setting, 0.7)
    responses_text = ""
    for role_name, response in responses.items():
        responses_text += f"{role_name} Response: {response}\n\n"

    prompt = (
        f"As the senior manager, please review and evaluate the following responses from junior managers based on clarity, relevance, depth of information, and practicality. Consider the target audience for each response (e.g., technical vs. general public).\n\n"
        f"{responses_text}\n"
        "Provide your evaluation and elaborate on the findings. Which response is the most compelling and why? Are there any responses that are misleading or inaccurate? Finally, provide a concise summary of the key takeaways.\n\n"
        "Also provide a perfect answer to the question. Lastly, craft a prompt to create a custom illustration depicting the key concepts and insights from the responses."
    )

    try:
        ollama.temperature = temperature
        evaluation_response = await asyncio.to_thread(ollama.chat, model=model, messages=[{'role': 'user', 'content': prompt}])
        evaluation_content = evaluation_response['message']['content']

        perfect_answer_match = re.search(r"Perfect Answer:\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)
        illustration_prompt_match = re.search(r"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)

        perfect_answer = perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found, check Senior Manager Evaluation ."
        illustration_prompt = illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found, check Senior Manager Evaluation."

        print("Perfect Answer:", perfect_answer)  # Print to console
        print("Illustration Prompt:", illustration_prompt) # Print to console

        return evaluation_content, perfect_answer, illustration_prompt # Correct return!

    except Exception as e:
        print(f"Error in evaluation: {e}")
        return "Error in evaluation.", "Could not extract perfect answer.", "Could not extract illustration prompt."

# Gradio interface
async def gradio_interface(question, role1, role2, role3, role4, model1, model2, model3, model4, eval_model, temp_setting1, temp_setting2, temp_setting3, temp_setting4, eval_temp_setting):
    selected_roles = [role1, role2, role3, role4]
    selected_models = [model1, model2, model3, model4]
    selected_temp_settings = [temp_setting1, temp_setting2, temp_setting3, temp_setting4]

    expert_responses = {}
    tasks = []

    for i in range(4):
        if selected_roles[i]:
            role_name = selected_roles[i]['name']
            expert_responses[role_name] = ""
            tasks.append(generate_response_with_expertise(question, selected_roles[i], model=selected_models[i], temperature_setting=selected_temp_settings[i]))

    results = await asyncio.gather(*tasks)

    k = 0
    for i in range(4):
        if selected_roles[i]:
            role_name = selected_roles[i]['name']
            expert_responses[role_name] = results[k]
            k += 1

    evaluation, perfect_answer, illustration_prompt = await evaluate_responses(expert_responses, model=eval_model, temperature_setting=eval_temp_setting)

    response_texts = []
    for role in [role1, role2, role3, role4]:
        if role:
            role_name = role['name']
            response_texts.append(expert_responses.get(role_name, ""))
        else:
            response_texts.append("")

    return response_texts[0], response_texts[1], response_texts[2], response_texts[3], evaluation, perfect_answer, illustration_prompt # Correct return statement


iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        "text",
        gr.Dropdown(possible_roles, label="Role 1"),
        gr.Dropdown(['qwen:0.5b', 'smollm2:135m', 'gemma2:2b','llava:7b','dolphin-llama3:latest'], label="Model 1"),
        gr.Dropdown(list(temperature_presets.keys()), label="Temperature 1"),

        gr.Dropdown(possible_roles, label="Role 2"),
        gr.Dropdown(['qwen:0.5b', 'smollm2:135m', 'gemma2:2b','llava:7b','dolphin-llama3:latest'], label="Model 2"),
        gr.Dropdown(list(temperature_presets.keys()), label="Temperature 2"),

        gr.Dropdown(possible_roles, label="Role 3"),
        gr.Dropdown(['qwen:0.5b', 'smollm2:135m', 'gemma2:2b','llava:7b','dolphin-llama3:latest'], label="Model 3"),
        gr.Dropdown(list(temperature_presets.keys()), label="Temperature 3"),

        gr.Dropdown(possible_roles, label="Role 4"),
        gr.Dropdown(['qwen:0.5b', 'smollm2:135m', 'gemma2:2b','llava:7b','dolphin-llama3:latest'], label="Model 4"),
        gr.Dropdown(list(temperature_presets.keys()), label="Temperature 4"),

        
        
        
        
        gr.Dropdown(['gemma2:2b', 'gemma2:2b', 'gemma2:2b','dolphin-llama3:latest'], label="Evaluation Model"),
        

        gr.Dropdown(list(temperature_presets.keys()), label="Evaluation Temperature"),

    ],
    outputs=[
        gr.Textbox(label="Response 1"),
        gr.Textbox(label="Response 2"),
        gr.Textbox(label="Response 3"),
        gr.Textbox(label="Response 4"),
        gr.Textbox(label="Senior Manager Evaluation"),
        gr.Textbox(label="Perfect Answer"),
        gr.Textbox(label="Illustration Prompt"),
    ],
    title="Ask the Experts",
    description="Ask a question and get answers from a team of 4 experts, with a senior manager evaluation."
)

if __name__ == "__main__":
    iface.launch()
