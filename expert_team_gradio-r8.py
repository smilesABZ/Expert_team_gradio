import gradio as gr
import ollama
import asyncio

# Define possible team roles with their names and sub-prompts
possible_roles = [
    {'name': 'Strategic Business Advisor',
     'sub_prompt': "Analyze the situation from a high-level business perspective. Focus on strategic implications, market opportunities, and potential risks for a company. Consider long-term goals and competitive advantage when addressing the following:"},
    {'name': 'Technical Implementation Expert',
     'sub_prompt': "Explain the technical aspects and implementation challenges. Focus on the practicalities of execution, potential technical roadblocks, and necessary technologies or infrastructure related to:"},
    {'name': 'User Experience (UX) Advocate',
     'sub_prompt': "Evaluate this from the user's perspective. Focus on usability, user needs, potential pain points, and how to optimize the experience for the end-user related to:"},
    {'name': 'Creative Innovation Catalyst',
     'sub_prompt': "Think creatively and outside the box. Focus on generating innovative ideas, novel solutions, and unconventional approaches to:"},
    {'name': 'Risk Assessment Analyst',
     'sub_prompt': "Identify and analyze potential risks and downsides. Focus on possible negative consequences, challenges, and mitigation strategies associated with:"},
    {'name': 'Ethical and Societal Impact Officer',
     'sub_prompt': "Consider the ethical and societal implications. Focus on fairness, social responsibility, potential biases, and the broader impact on society related to:"},
    {'name': 'Financial Efficiency Expert',
     'sub_prompt': "Analyze the financial aspects and efficiency. Focus on costs, return on investment, resource optimization, and financial sustainability related to:"}
]

# Function to generate responses with specified expertise and local sub-prompt (with error handling)
async def generate_response_with_expertise(question, expertise):
    prompt = f"You are a {expertise['name']}. {expertise['sub_prompt']} {question}"
    try:
        response = await asyncio.to_thread(ollama.chat, model=expertise['model'], messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        print(f"Error generating response from {expertise['name']}: {e}")
        return "Error occurred during response generation."

# Main function to generate responses from LLMs with assigned roles
async def generate_responses(question, role1_name, role2_name, role3_name, role4_name):
    print("--- Entering generate_responses ---") # Debug print

    llm_instances = [
        {'name': role1_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role1_name), "Generic Prompt:")},
        {'name': role2_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role2_name), "Generic Prompt:")},
        {'name': role3_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role3_name), "Generic Prompt:")},
        {'name': role4_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role4_name), "Generic Prompt:")}
    ]
    print("llm_instances:", llm_instances) # Debug print

    tasks = [generate_response_with_expertise(question, expertise) for expertise in llm_instances]
    results = await asyncio.gather(*tasks)
    print("results from asyncio.gather:", results) # Debug print

    responses = {llm_instances[i]['name']: results[i] for i in range(len(llm_instances))}
    print("responses dictionary:", responses) # Debug print

    print("--- Exiting generate_responses ---") # Debug print
    return responses['Strategic Business Advisor'], responses['Technical Implementation Expert'], responses['User Experience (UX) Advocate'], responses['Creative Innovation Catalyst'], responses
# Simplified evaluate_responses (for testing LLM responses)
async def evaluate_responses(responses):
    return "Evaluation Placeholder", "Perfect Answer Placeholder", "Illustration Prompt Placeholder"

# Gradio interface (using asyncio) - CORRECT ASYNC FUNCTION WITH 5 ARGUMENTS
async def gradio_interface(question, role1, role2, role3, role4):
    ai_research_scientist_response, medical_expert_response, educational_technologist_response, entertainment_industry_analyst_response, all_responses = await generate_responses(question, role1, role2, role3, role4)
    evaluation, perfect_answer, illustration_prompt = await evaluate_responses(all_responses)
    return ai_research_scientist_response, medical_expert_response, educational_technologist_response, entertainment_industry_analyst_response, evaluation, perfect_answer, illustration_prompt


iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        "text",
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 1 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 2 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 3 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 4 Role")
    ],
    outputs=[
        gr.Textbox(label="Strategic Business Advisor Response"),
        gr.Textbox(label="Technical Implementation Expert Response"),
        gr.Textbox(label="User Experience (UX) Advocate Response"),
        gr.Textbox(label="Creative Innovation Catalyst Response"),
        gr.Textbox(label="Senior Manager Evaluation"),
        gr.Textbox(label="Perfect Answer"),
        gr.Textbox(label="Illustration Prompt")
    ],
    title="Ask the Experts and Get an Evaluation",
    description="Type your question and get answers from a team of experts you select. An additional LLM will evaluate the responses and provide a comprehensive recommendation, a perfect answer, and a prompt for a custom illustration."
)

# Launch the app
if __name__ == "__main__":
    iface.launch()
