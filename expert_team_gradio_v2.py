import gradio as gr
import ollama
import asyncio

# Define possible team roles with their names and sub-prompts (same as before)
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

# Function to generate responses with specified expertise (no change needed in core logic)
async def generate_response_with_expertise(question, expertise):
    prompt = f"You are a {expertise['name']}. {expertise['sub_prompt']} {question}"
    try:
        response = await asyncio.to_thread(ollama.chat, model=expertise['model'], messages=[{'role': 'user', 'content': prompt}])  # Async call
        return response['message']['content']
    except Exception as e:
        print(f"Error generating response from {expertise['name']}: {e}")
        return "Error occurred during response generation."

# Main function to generate responses from LLMs with assigned roles (modified)
async def generate_responses(question, role1_name, role2_name, role3_name, role4_name): # Now accepts role names for each LLM
    llm_instances = [ # Define LLM instances with assigned roles
        {'name': role1_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role1_name), "Generic Prompt:")}, # Find sub-prompt based on selected role
        {'name': role2_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role2_name), "Generic Prompt:")},
        {'name': role3_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role3_name), "Generic Prompt:")},
        {'name': role4_name, 'model': 'qwen:0.5b', 'sub_prompt': next((role['sub_prompt'] for role in possible_roles if role['name'] == role4_name), "Generic Prompt:")}
    ]

    tasks = [generate_response_with_expertise(question, expertise) for expertise in llm_instances]
    results = await asyncio.gather(*tasks)

    responses = {llm_instances[i]['name']: results[i] for i in range(len(llm_instances))} # Responses dict now keyed by assigned role name

    return responses['Strategic Business Advisor'], responses['Technical Implementation Expert'], responses['User Experience (UX) Advocate'], responses['Creative Innovation Catalyst'], responses # Still return first 4 as before for output mapping


# Function to evaluate responses using a senior manager LLM (modified prompt)
async def evaluate_responses(responses):
    prompt = (
        f"As the senior manager, please review and evaluate the following responses from different team members in their assigned roles, based on clarity, relevance, depth of information, and practicality. Consider the target audience for each response.\n\n"
        f"Strategic Business Advisor Response: {responses.get('Strategic Business Advisor', 'No Response')}\n\n"
        f"Technical Implementation Expert Response: {responses.get('Technical Implementation Expert', 'No Response')}\n\n"
        f"User Experience (UX) Advocate Response: {responses.get('User Experience (UX) Advocate', 'No Response')}\n\n"
        f"Creative Innovation Catalyst Response: {responses.get('Creative Innovation Catalyst', 'No Response')}\n\n"
        # Note: Evaluation prompt still includes all role names for consistency, even if some are not used. You can customize this further.
        f"Risk Assessment Analyst Response: {responses.get('Risk Assessment Analyst', 'No Response')}\n\n"
        f"Ethical and Societal Impact Officer Response: {responses.get('Ethical and Societal Impact Officer', 'No Response')}\n\n"
        f"Financial Efficiency Expert Response: {responses.get('Financial Efficiency Expert', 'No Response')}\n\n"
        "Provide your evaluation and elaborate on the findings. Which response is the most compelling and why? Are there any responses that are misleading or inaccurate? Finally, provide a concise summary of the key takeaways.\n\n"
        "Also provide a perfect answer to the question. Lastly, craft a prompt to create a custom illustration depicting the key concepts and insights from the responses."
    )

    try:
        evaluation_response = await asyncio.to_thread(ollama.chat, model='gemma2:2b', messages=[{'role': 'user', 'content': prompt}])
        evaluation_content = evaluation_response['message']['content']

        # Extract perfect answer and illustration prompt (no change needed)
        try:
            perfect_answer_start = evaluation_content.find("Perfect Answer:")
            illustration_prompt_start = evaluation_content.find("Illustration Prompt:")

            if perfect_answer_start != -1 and illustration_prompt_start != -1:
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

# Gradio interface (modified inputs for role assignment)
async def gradio_interface(question, role1, role2, role3, role4): # Now accepts roles as individual dropdown selections
    ai_research_scientist_response, medical_expert_response,
