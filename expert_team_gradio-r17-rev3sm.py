import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("gpt-4")
model = AutoModelForCausalLM.from_pretrained("your_model_name")

temperature_presets = {
    "Cautious": 0.3,
    "Balanced": 0.3,
    "Creative": 0.3
}
def gradio_interface(question, role1, role2, role3, role4, model1, model2, model3, model4, eval_model, temp_setting1, temp_setting2, temp_setting3, temp_setting4, eval_temp_setting):
    """
    Main function for the Gradio interface.
    Handles user input, generates expert responses, evaluates them, and returns outputs for display.
    """
    selected_roles = [role1, role2, role3, role4]
    selected_models = [model1, model2, model3, model4]
    selected_temperature_settings = [temp_setting1, temp_setting2, temp_setting3, temp_setting4]

    # Initialize the tokenizer and model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = tokenizer.to(device)
    model = model.to(device)

    # Function to process input data
    async def preprocess_input(prompt):
        return tokenizer.encode(prompt, truncation=True, max_length=2048)

    async def process_events(event):
        try:
            # Preprocess the input
            response = await preprocess_input(event["input"])

            # Call the model for prediction
            outputs = await model.generate(
                prompt=response,
                max_length=1024,
                num_return_sequences=1  # Number of top predictions to return
            )

            # Extract the predicted text and temperature
            predicted_text = outputs[0][0].strip()
            temperature = outputs[0][1]

            # Process the response
            prediction = await fn(*processed_input)
            return {
                "prediction": prediction,
                "temperature": temperature,
                "response": predicted_text
            }

        except Exception as e:
            print(f"Error: {e}")
            return None

    # Set up the interface
    iface = gr.Interface(
        fn=process_events,
        inputs=[
            gr.Textbox(label="Enter your question here"),  # More descriptive label
            gr.Dropdown(possible_roles, label="Expert Role 1", info="Choose the first expert role to consult."),  # Added info
            gr.Dropdown(model_options, label="Model for Role 1", info="Select model for Expert 1."),  # Selected model
            gr.Dropdown(selected_temperature_settings, label="Temperature Settings", info="Select temperature settings"),  # Temperature settings
            gr.Dropdown(possible_roles, label="Expert Role 2", info="Choose the second expert role."),  # Added info
            gr.Dropdown(model_options, label="Model for Role 2", info="Select model for Expert 2."),  # Selected model
            gr.Dropdown(selected_temperature_settings, label="Temperature Settings", info="Select temperature settings"),  # Temperature settings
            gr.Dropdown(possible_roles, label="Expert Role 3", info="Choose the third expert role."),  # Added info
            gr.Dropdown(model_options, label="Model for Role 3", info="Select model for Expert 3."),  # Selected model
            gr.Dropdown(selected_temperature_settings, label="Temperature Settings", info="Select temperature settings"),  # Temperature settings
            gr.Dropdown(possible_roles, label="Expert Role 4", info="Choose the fourth expert role."),  # Added info
            gr.Dropdown(model_options, label="Model for Role 4", info="Select model for Expert 4."),  # Selected model
        ],
        outputs=[
            gr.Textbox(label="Response from Expert 1"),  # More descriptive output labels
            gr.Textbox(label="Response from Expert 2"),
            gr.Textbox(label="Response from Expert 3"),
            gr.Textbox(label="Response from Expert 4"),
            gr.Textbox(label="Senior Manager Evaluation", lines=10), # Increased lines for better readability
            gr.Textbox(label="Perfect Answer (from Evaluation)", lines=3), # Clarified label
            gr.Textbox(label="Illustration Prompt (from Evaluation)", lines=3), # Clarified label
        ],
        title="Ask the Experts: Multi-Perspective Response System",  # More engaging title
        description="""
        This tool simulates a team of experts providing answers to your questions from different perspectives. 
        Select up to four expert roles, each with a specific focus (e.g., Strategic, Technical, UX, Ethical). 
        Choose language models and temperature settings for each expert and an evaluation model for the 'Senior Manager' who reviews all responses, provides a perfect answer, and suggests an illustration prompt.
        """,  # More detailed and user-friendly description
        examples=[ # Example questions to guide users
            ["What are the benefits and risks of implementing AI in customer service?"],
            ["How can we improve user engagement with our mobile app?"],
            ["Discuss the ethical implications of using facial recognition technology."],
            ["Analyze the potential market for a new eco-friendly product."],
        ],
        live=False  # Consider setting to False for performance in some environments
    )

    return iface.launch()

if __name__ == "__main__":
    interface = gradio_interface()
    interface.run()

