import gradio as gr
import ollama
import asyncio

# ... (possible_roles definition remains the same)

async def generate_response_with_expertise(question, expertise):
    prompt = f"You are a {expertise['name']}. {expertise['sub_prompt']} {question}"
    try:
        response = await asyncio.to_thread(ollama.chat, model=expertise['model'], messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"Error generating response from {expertise['name']}: {e}")
        return f"Error occurred during response generation: {e}"  # Include error message

async def generate_responses(question, role1_name, role2_name, role3_name, role4_name):
    llm_instances = [
        {'name': role1_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role1_name), "Generic Prompt:")},
        {'name': role2_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role2_name), "Generic Prompt:")},
        {'name': role3_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role3_name), "Generic Prompt:")},
        {'name': role4_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role4_name), "Generic Prompt:")}
    ]

    tasks = [generate_response_with_expertise(question, expertise) for expertise in llm_instances]
    results = await asyncio.gather(*tasks)

    responses = {llm_instances[i]['name']: results[i] for i in range(len(llm_instances))}
    return responses  # Return the dictionary directly

async def evaluate_responses(responses):
    # Placeholder - replace with your actual evaluation logic
    return "Evaluation Placeholder", "Perfect Answer Placeholder", "Illustration Prompt Placeholder"

# *** KEY CHANGE:  Wrap the async function ***
def gradio_interface(question, role1, role2, role3, role4):
    async def _gradio_interface(question, role1, role2, role3, role4): # inner async
        responses = await generate_responses(question, role1, role2, role3, role4)
        evaluation, perfect_answer, illustration_prompt = await evaluate_responses(responses)
        return (
            responses.get(role1, "No Response"),  # Use .get() and role names
            responses.get(role2, "No Response"),
            responses.get(role3, "No Response"),
            responses.get(role4, "No Response"),
            evaluation,
            perfect_answer,
            illustration_prompt
        )
    return _gradio_interface(question, role1, role2, role3, role4) # call the inner async


iface = gr.Interface(
    fn=gradio_interface,  # No change here
    inputs=[
        "text",
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 1 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 2 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 3 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 4 Role")
    ],
    outputs=[
        gr.Textbox(label=possible_roles[0]['name'] + " Response"), # Use possible_roles for labels
        gr.Textbox(label=possible_roles[1]['name'] + " Response"),
        gr.Textbox(label=possible_roles[2]['name'] + " Response"),
        gr.Textbox(label=possible_roles[3]['name'] + " Response"),
        gr.Textbox(label="Senior Manager Evaluation"),
        gr.Textbox(label="Perfect Answer"),
        gr.Textbox(label="Illustration Prompt")
    ],
    title="Ask the Experts and Get an Evaluation",
    description="Type your question and get answers from a team of experts you select. An additional LLM will evaluate the responses and provide a comprehensive recommendation, a perfect answer, and a prompt for a custom illustration."
)

if __name__ == "__main__":
    iface.launch()
