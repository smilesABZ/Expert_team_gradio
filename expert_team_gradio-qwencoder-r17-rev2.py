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
     'description': "Considers fairness, social responsibility, and broader societal impacts. Important for ensuring responsible and ethical outcomes.",}]

# Define logging function to capture errors
def log_error(err):
    print(f"Error: {err}")

# Define Gradio interface function
async def gradio_interface(question, role1, role2, role3, role4, model1, model2, model3, model4, eval_model, temp_setting1, temp_setting2, temp_setting3, temp_setting4, eval_temp_setting):
    try:
        temperature = temp_settings[0]
        prompt = f"You are a {role['name']}. {role['sub_prompt']} {question}"
        try:
            ollama.temperature = temperature
            response = await asyncio.to_thread(ollama.chat, model=model1, messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content']
        except Exception as e:
            log_error(e)
            return f"Error occurred during response generation for {role['name']}. Please check console.", "Error extracting perfect answer.", "Error extracting illustration prompt."
    except Exception as e:
        error_message = f"Error from {role['name']} ({model_name}): {e}"
        print(error_message) # Still print to console for debugging
