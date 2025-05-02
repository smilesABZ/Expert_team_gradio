import gradio as gr

possible_roles = [
    {'name': 'Role 1'},
    {'name': 'Role 2'},
    {'name': 'Role 3'},
    {'name': 'Role 4'},
    {'name': 'Role 5'},
    {'name': 'Role 6'},
    {'name': 'Role 7'}
]

def gradio_interface_test(question, role1, role2, role3, role4):
    return "Response from LLM 1 with Role: " + role1, \
           "Response from LLM 2 with Role: " + role2, \
           "Response from LLM 3 with Role: " + role3, \
           "Response from LLM 4 with Role: " + role4, \
           "Evaluation Output", \
           "Perfect Answer Output", \
           "Illustration Prompt Output"

iface = gr.Interface(
    fn=gradio_interface_test,
    inputs=[
        "text",
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 1 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 2 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 3 Role"),
        gr.Dropdown([role['name'] for role in possible_roles], label="LLM 4 Role")
    ],
    outputs=[
        gr.Textbox(label="LLM 1 Response"),
        gr.Textbox(label="LLM 2 Response"),
        gr.Textbox(label="LLM 3 Response"),
        gr.Textbox(label="LLM 4 Response"),
        gr.Textbox(label="Senior Manager Evaluation"),
        gr.Textbox(label="Perfect Answer"),
        gr.Textbox(label="Illustration Prompt")
    ],
    title="Minimal Gradio Test",
    description="Testing dropdown inputs and text outputs"
)

if __name__ == "__main__":
    iface.launch()
