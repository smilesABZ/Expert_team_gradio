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
async def generate_response_with_expertise(question, expertise): # Modified to accept expertise dict directly
    prompt = f"You are a {expertise['name']}. {expertise['sub_prompt']} {question}" # Access sub_prompt from expertise dict
    try:
        response = await asyncio.to_thread(ollama.chat, model=expertise['model'], messages=[{'role': 'user', 'content': prompt}])  # Async call
        return response['message']['content']
    except Exception as e:
        print(f"Error generating response from {expertise['name']}: {e}")
        return "Error occurred during response generation."

# Main function to generate responses from selected LLMs (using asyncio)
async def generate_responses(question, selected_roles_names): # Modified to accept selected role names
    expertises = []
    for role_name in selected_roles_names:
        for role_def in possible_roles:
            if role_def['name'] == role_name:
                expertises.append({'name': role_def['name'], 'model': 'qwen:0.5b', 'sub_prompt': role_def['sub_prompt']}) # Dynamically create expertise list

    tasks = [generate_response_with_expertise(question, expertise) for expertise in expertises] # Pass expertise dict directly
    results = await asyncio.gather(*tasks)

    responses = {expertises[i]['name']: results[i] for i in range(len(expertises))}

    # Ensure responses are returned in a consistent order for output mapping in Gradio.
    # We will return responses based on the order of selected_roles_names
    ordered_expert_responses = []
    for role_name in selected_roles_names:
        ordered_expert_responses.append(responses.get(role_name, "No response generated.")) # Handle case where a role might not have a response

    # Pad with empty strings if fewer than 4 roles are selected, to match original output structure
    while len(ordered_expert_responses) < 4:
        ordered_expert_responses.append("")


    return ordered_expert_responses[0], ordered_expert_responses[1], ordered_expert_responses[2], ordered_expert_responses[3], responses # Return responses in order and all responses dict


# Function to evaluate responses using a senior manager LLM (with extraction and improved prompt)
async def evaluate_responses(responses):
    prompt = (
        f"As the senior manager, please review and evaluate the following responses from junior managers based on clarity, relevance, depth of information, and practicality. Consider the target audience for each response (e.g., technical vs. general public).\n\n"
        f"Strategic Business Advisor Response: {responses.get('Strategic Business Advisor', 'No Response')}\n\n" # Use .get() for robustness
        f"Technical Implementation Expert Response: {responses.get('Technical Implementation Expert', 'No Response')}\n\n"
        f"User Experience (UX) Advocate Response: {responses.get('User Experience (UX) Advocate', 'No Response')}\n\n"
        f"Creative Innovation Catalyst Response: {responses.get('Creative Innovation Catalyst', 'No Response')}\n\n"
        f"Risk Assessment Analyst Response: {responses.get('Risk Assessment Analyst', 'No Response')}\n\n"
        f"Ethical and Societal Impact Officer Response: {responses.get('Ethical and Societal Impact Officer', 'No Response')}\n\n"
        f"Financial Efficiency Expert Response: {responses.get('Financial Efficiency Expert', 'No Response')}\n\n"
        "Provide your evaluation and elaborate on the findings. Which response is the most compelling and why? Are there any responses that are misleading or inaccurate? Finally, provide a concise summary of the key takeaways.\n\n"
        "Also provide a perfect answer to the question. Lastly, craft a prompt to create a custom illustration depicting the key concepts and insights from the responses."
    )

    try:
        evaluation_response = await asyncio.to_thread(ollama.chat, model='gemma2:2b', messages=[{'role': 'user', 'content': prompt}])
        evaluation_content = evaluation_response['message']['content']

        # Extract perfect answer and illustration prompt (robust extraction)
        try:
            perfect_answer_start = evaluation_content.find("Perfect Answer:")
            illustration_prompt_start = evaluation_content.find("Illustration Prompt:")

            if perfect_answer_start != -1 and illustration_prompt_start != -1:  # check if found
                perfect_answer = evaluation_content[perfect_answer_start + len("Perfect Answer:"):illustration_prompt_start].strip()
                illustration_prompt = evaluation_content[illustration_prompt_start + len("Illustration Prompt:"):].strip()
            else:
                perfect_answer = "Perfect answer not found."
                illustration_prompt = "Illustration prompt not found."

        except Exception as e:
            print(f"Error extracting perfect answer or illustration prompt: {e}")
            perfect_answer = "Could not extract perfect answer."
            illustration_prompt = "Could not extract illustration prompt."

        return evaluation_content, perfect_answer, illustration_prompt

    except Exception as e:
        print(f"Error in evaluation: {e}")
        return "Error in evaluation.", "Could not extract perfect answer.", "Could not extract illustration prompt."

# Gradio interface (using asyncio)
async def gradio_interface(question, selected_roles): # Modified to accept selected_roles
    ai_research_scientist_response, medical_expert_response, educational_technologist_response, entertainment_industry_analyst_response, all_responses = await generate_responses(question, selected_roles) # Pass selected_roles
    evaluation, perfect_answer, illustration_prompt = await evaluate_responses(all_responses)
    return ai_research_scientist_response, medical_expert_response, educational_technologist_response, entertainment_industry_analyst_response, evaluation, perfect_answer, illustration_prompt

iface = gr.Interface(
    fn=gradio_interface, # Keep your working gradio_interface function from the Checkbox Group version
    inputs=[
        "text",
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 1 Role"), # Changed to Dropdown
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 2 Role"), # Changed to Dropdown
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 3 Role"), # Changed to Dropdown
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 4 Role")  # Changed to Dropdown
    ],
    outputs=[ # Keep your working outputs from the Checkbox Group version
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
# Launch the app (using asyncio)
if __name__ == "__main__":
    iface.launch()
