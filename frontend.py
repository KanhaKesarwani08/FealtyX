import gradio as gr
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def create_student(name, age, email):
    try:
        response = requests.post(
            f"{BASE_URL}/students",
            json={"name": name, "age": int(age), "email": email}
        )
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_all_students():
    try:
        response = requests.get(f"{BASE_URL}/students")
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_student(student_id):
    try:
        response = requests.get(f"{BASE_URL}/students/{student_id}")
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def update_student(student_id, name, age, email):
    try:
        # Create update data dictionary with only provided values
        update_data = {}
        if name.strip():  # Only include if not empty
            update_data["name"] = name
        if age is not None and age != 0:  # Include if age is provided and not 0
            update_data["age"] = int(age)
        if email.strip():  # Only include if not empty
            update_data["email"] = email
            
        if not update_data:  # If no fields to update
            return "Error: Please provide at least one field to update"
        
        response = requests.put(
            f"{BASE_URL}/students/{student_id}",
            json=update_data
        )
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def delete_student(student_id):
    try:
        response = requests.delete(f"{BASE_URL}/students/{student_id}")
        if response.status_code == 200:
            return "Student deleted successfully"
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_student_summary(student_id):
    try:
        response = requests.get(f"{BASE_URL}/students/{student_id}/summary")
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Student Management System") as demo:
    gr.Markdown("# Student Management System")
    
    with gr.Tab("Create Student"):
        with gr.Row():
            with gr.Column():
                create_name = gr.Textbox(label="Name")
                create_age = gr.Number(label="Age", minimum=16, maximum=120)
                create_email = gr.Textbox(label="Email")
                create_btn = gr.Button("Create Student")
            with gr.Column():
                create_output = gr.Textbox(label="Result", lines=5)
        create_btn.click(
            create_student,
            inputs=[create_name, create_age, create_email],
            outputs=create_output
        )

    with gr.Tab("Get All Students"):
        get_all_btn = gr.Button("Get All Students")
        get_all_output = gr.Textbox(label="Result", lines=10)
        get_all_btn.click(get_all_students, inputs=[], outputs=get_all_output)

    with gr.Tab("Get Student"):
        with gr.Row():
            with gr.Column():
                get_id = gr.Number(label="Student ID", precision=0)
                get_btn = gr.Button("Get Student")
            with gr.Column():
                get_output = gr.Textbox(label="Result", lines=5)
        get_btn.click(get_student, inputs=[get_id], outputs=get_output)

    with gr.Tab("Update Student"):
        with gr.Row():
            with gr.Column():
                update_id = gr.Number(label="Student ID", precision=0)
                update_name = gr.Textbox(label="Name (Optional - leave empty to keep current)")
                update_age = gr.Number(label="Age (Optional - leave empty to keep current)", minimum=16, maximum=120)
                update_email = gr.Textbox(label="Email (Optional - leave empty to keep current)")
                update_btn = gr.Button("Update Student")
        with gr.Column():
            update_output = gr.Textbox(label="Result", lines=5)
    update_btn.click(
        update_student,
        inputs=[update_id, update_name, update_age, update_email],
        outputs=update_output
    )

    with gr.Tab("Delete Student"):
        with gr.Row():
            with gr.Column():
                delete_id = gr.Number(label="Student ID", precision=0)
                delete_btn = gr.Button("Delete Student")
            with gr.Column():
                delete_output = gr.Textbox(label="Result", lines=5)
        delete_btn.click(delete_student, inputs=[delete_id], outputs=delete_output)

    with gr.Tab("Get Student Summary"):
        with gr.Row():
            with gr.Column():
                summary_id = gr.Number(label="Student ID", precision=0)
                summary_btn = gr.Button("Get Summary")
            with gr.Column():
                summary_output = gr.Textbox(label="Result", lines=10)
        summary_btn.click(get_student_summary, inputs=[summary_id], outputs=summary_output)

if __name__ == "__main__":
    demo.launch(share= True)