import gradio as gr
import ollama
import asyncio
import re
import threading

temperature_presets = {
    'Cautious': 0.3,  # More descriptive names
    'Balanced': 0.7,
    'Creative': 1.3
}

possible_roles = [
    {'name': 'Strategic Business Advisor', 'description': "Analyzes from a business perspective...", 'sub_prompt': "Analyze the situation from a high-level business perspective..."},
    # ... (rest of your role definitions)
]

available_models = ['qwen:0.5b', 'smollm2:135m', 'gemma2:2b', 'llava:7b', 'dolphin-llama3:latest']
model_options = {model: model for model in available_models}

evaluation_models = ['gemma2:2b', 'dolphin-llama3:latest']
evaluation_model_options = {model: model for model in evaluation_models}


async def generate_expert_response(question, role, model_name, temperature_setting):
    temperature = temperature_presets.get(temperature_setting, 0.7)
    prompt = f"You are a {role['name']}. {role['sub_prompt']} {question}"
    try:
        ollama.temperature = temperature
        response = await asyncio.to_thread(ollama.chat, model=model_name, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        error_message = f"Error from {role['name']} ({model_name}): {e}"
        print(error_message)
        return f"Error occurred during response generation for {role['name']}. Please check console for details."


async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
    temperature = temperature_presets.get(eval_temperature_setting, 0.7)
    responses_text = "\n".join([f"{role_name} Response: {response}\n" for role_name, response in responses.items()])

    prompt = (
        "As the senior manager, please review and evaluate the following responses... "  # (Your detailed prompt here)
    )

    try:
        ollama.temperature = temperature
        evaluation_response = await asyncio.to_thread(ollama.chat, model=eval_model_name, messages=[{'role': 'user', 'content': prompt}])
        evaluation_content = evaluation_response['message']['content']

        perfect_answer_match = re.search(r"Perfect Answer:\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)
        illustration_prompt_match = re.search(r"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))", evaluation_content, re.DOTALL | re.IGNORECASE)

        perfect_answer = perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found in evaluation."
        illustration_prompt = illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found in evaluation."

        print("\n--- Evaluation Details (Console Output) ---")
        print("Perfect Answer:", perfect_answer)
        print("Illustration Prompt:", illustration_prompt)
        print("Full Evaluation Output:\n", evaluation_content)
        print("--- End Evaluation Details ---")

        return evaluation_content, perfect_answer, illustration_prompt

    except Exception as e:
        error_message = f"Error during evaluation process: {e}"
        print(error_message)
        return "Error in evaluation. Please check console.", "Error extracting perfect answer.", "Error extracting illustration prompt."


async def gradio_interface(question, role1, role2, role3, role4, model1, model2, model3, model4, eval_model, temp_setting1, temp_setting2, temp_setting3, temp_setting4, eval_temp_setting):
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
            tasks.append(generate_expert_response(question, role, model_name, temp_setting))

    results = await asyncio.gather(*tasks)

    k = 0
    for i in range(4):
        if selected_roles[i]:
            role_name = selected_roles[i]['name']
            expert_responses[role_name] = results[k]
            k += 1

    evaluation_text, perfect_answer_text, illustration_prompt_text = await evaluate_responses(expert_responses, eval_model, eval_temp_setting)

    response_texts = [expert_responses.get(role['name'], "") if role else "" for role in selected_roles]

    return *response_texts, evaluation_text, perfect_answer_text, illustration_prompt_text


iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter your question here"),
        # ... (rest of your input definitions)
        gr.Radio(list(temperature_presets.keys()), label="Approach style ", info="Set approach for very senior Manager evaluation."),

    ],
    outputs=[
        gr.Textbox(label="Response from Expert 1"),
        # ... (rest of your output definitions)
        gr.Textbox(label="Illustration Prompt (from Evaluation)", lines=3),
    ],
    title="Ask the Experts: Multi-Perspective Response System",
    description="This tool simulates a team of experts...",  # (Your description)
    examples=[
        ["What are the benefits and risks..."],  # (Your examples)
    ],
    live=False,
)


def launch_gradio(iface):
    iface.launch()


async def main():
    gradio_thread = threading.Thread(target=launch_gradio, args=(iface,))
    gradio_thread.start()

    # You can now use the event loop for other asyncio tasks if needed.
    # For example:
    # await asyncio.sleep(5)  # Do something else while Gradio runs.

if __name__ == "__main__":
    asyncio.run(main())
