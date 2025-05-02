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
     'sub_prompt': "Identify and analyze potential risks and challenges. Focus on identifying and mitigating potential issues related to:"},
    {'name': 'Email Server Security Manager',
     'description': "Ensure secure communication channels. Protects user privacy, system integrity, and data security.",
     'sub_prompt': "Secure your email communication. Ensure data privacy, system integrity, and information security related to:"},
]

async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
    """
    Evaluates responses from different expert perspectives.
    """
    temperature = temperature_presets.get(eval_temperature_setting, 0.7)
    
    # Create a list of temperature preset options for each role and evaluation model
    temp preset options:
    Cautious, Balanced, Creative
    
    Perfect Answer Match:
    illustrate prompt match:

    print("\n--- Evaluation Details (Console Output) ---")
    print("Perfect Answer:", perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found in evaluation.")
    print("Illustration Prompt:", illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found in evaluation.")

    return (
        f"Key elements: {response} \n\n"
        "Perfect Answer:\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))",
        f"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))"
    )

async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
    """
    Evaluates responses from different expert perspectives.
    """
    temperature = temperature_presets.get(eval_temperature_setting, 0.7) # Default to 'Balanced'

    # Create a list of radio button options for each role's temp preset
    radio preset options:
    Cautious, Balanced, Creative
    
    Perfect Answer Match: 
    illustrate prompt match:

    print("\n--- Evaluation Details (Console Output) ---")
    print("Perfect Answer:", perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found in evaluation.")
    print("Illustration Prompt:", illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found in evaluation.")

    return (
        f"Key elements: {response} \n\n"
        "Perfect Answer:\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))",
        f"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))"
    )

async def generate_expert_response(question, role, model_name, temperature_setting):
    """
    Generates a response from a specified expert role using a given model and temperature.
    Handles potential errors and provides informative error messages.
    """
    temperature = temperature_setting
    prompt = f"You are {role['name']}. {role['sub_prompt']} {question}"
    
    try:
        ollama.temperature = temperature
        response = await asyncio.to_thread(ollama.chat, model=model_name, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']
    except Exception as e:
        error_message = f"Error from {role['name']}: ({model_name}) {e}"
        print(error_message)
        return f"Error occurred during response generation for {role['name']}. Please check console for details."

async def evaluate_responses(responses, eval_model_name, eval_temperature_setting):
    """
    Evaluates responses from different expert perspectives.
    Extracts key elements and provides detailed feedback on the perfect answer and illustration prompt.
    """
    temperature = temperature_presets.get(eval_temperature_setting, 0.7) # Default to 'Balanced'

    # Create radio buttons for each expert's temperature setting
    role_temp preset options:
    Expert 1: Cautious
    Expert 2: Balanced
    Expert 3: Creative

    Perfect Answer Match: 
    illustrate prompt match:

    print("\n--- Evaluation Details (Console Output) ---")
    print("Perfect Answer:", perfect_answer_match.group(1).strip() if perfect_answer_match else "Perfect answer not found in evaluation.")
    print("Illustration Prompt:", illustration_prompt_match.group(1).strip() if illustration_prompt_match else "Illustration prompt not found in evaluation.")

    return (
        f"Key elements: {response} \n\n"
        "Perfect Answer:\s*(.+?)(?=(Illustration Prompt:|Summary:|Evaluation:|Key Takeaways:|$))",
        f"Illustration Prompt:\s*(.+?)(?=(Summary:|Evaluation:|Key Takeaways:|$))"
    )

async def gradio_interface(
    question,
    role1, role2, role3, role4,
    model1, model2, model3, model4,
    eval_model,
    temp_setting1, temp_setting2, temp_setting3, temp_setting4,
    eval_temp_setting
):
    """
    Main function for the Gradio interface.
    Handles user input and generates expert responses based on selected roles and models.
    Evaluates the responses and provides feedback.
    """
    selected_roles = [role1, role2, role3, role4]
    selected_models = [model1, model2, model3, model4]

    expert_responses = {}
    tasks = []

    for i in range(4):
        if selected_roles[i]:
            role = selected_roles[i]
            model_name = selected_models[i]
            temp_setting = temp_settings[i]
            tasks.append(generate_expert_response(question, role, model_name, temp_setting))

    results = await asyncio.gather(*tasks)

    k = 0 # Index to track results
    for i in range(4):
        if selected_roles[i]:
            role = selected_roles[i]['name']
            expert_responses[role] = results[k]
            k += 1

    evaluation_text, perfect_answer_text, illustration_prompt_text = await evaluate_responses(expert_responses, eval_model, eval_temperature_setting)

    return *response_texts, evaluation_text, perfect_answer_text, illustration_prompt_text # Correct unpacking

if __name__ == "__main__":
    iface.launch()
