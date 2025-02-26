
import os
from flask import Flask, request, jsonify, render_template, session
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import PyPDF2
import pytesseract
from PIL import Image
import io

# Initialize Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Initialize Vertex AI
PROJECT_ID = ""  # Replace with your Google Cloud Project ID
LOCATION = "us-central1"  # Change if using a different region
vertexai.init(project=PROJECT_ID, location=LOCATION)


# 📌 Home Route
@app.route('/')
def home():
    return render_template('home.html')


# 📌 Upload & Extract Text from PDFs & Images
@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']

        # Process PDF
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        # Process Image
        elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            text = extract_text_from_image(file)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Store extracted text in session for later use
        session['extracted_text'] = text

        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📌 Extract Text from PDF
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""  # Handle cases where text extraction might fail
    return text.strip() if text else "No text found in PDF."


# 📌 Extract Text from Image
def extract_text_from_image(file):
    try:
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)
        return text.strip() if text else "No text found in image."
    except Exception as e:
        return f"Error extracting text from image: "


# 📌 AI Summarization Route
@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text input"}), 400

        text = data['text']

        model = GenerativeModel("gemini-1.5-pro-001")
        prompt = f"Provide a concise summary of the following text, highlighting the key points and main arguments in no more than 200 words:\n\n{text}"

        response = model.generate_content(
            [Part.from_text(prompt)],
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 500
            },
            stream=False
        )

        return jsonify({"summary": response.text if response.text else "No summary generated."})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📌 AI Quiz Generation Route
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text input"}), 400

        text = data['text']

        model = GenerativeModel("gemini-1.5-pro-001")
        prompt = f"Generate a 5-question quiz based on this: {text}\n\n" \
                 f"Format the quiz as follows:\n" \
                 f"**Question 1:** [Question Text]\n" \
                 f"   * A) [Option A]\n" \
                 f"   * B) [Option B]\n" \
                 f"   * C) [Option C]\n" \
                 f"   * D) [Option D]\n" \
                 f"**Answer:** [Correct Answer Letter]"

        response = model.generate_content(
            [Part.from_text(prompt)],
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "max_output_tokens": 700
            },
            stream=False
        )

        return jsonify({"quiz": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📌 AI Chatbot Route (Enhanced with RAG & Markdown Formatting)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or "message" not in data:
            return jsonify({"error": "Missing message input"}), 400

        user_message = data['message']
        extracted_text = session.get('extracted_text', "")  # Retrieve stored text

        model = GenerativeModel("gemini-1.5-pro-001")
        chat = model.start_chat()

        # Enhanced Prompt for better formatting and clarity
        combined_prompt = (
            f"You are a helpful AI assistant.  Your goal is to answer the user's question based on the relevant document text provided below. Format your response using markdown for clear structure and readability.\n\n"
            f"### 📝 **User Message:**\n{user_message}\n\n"
            f"### 📄 **Relevant Document Text:**\n{extracted_text}\n\n"
            f"### 🤖 **AI Answer Guidelines:**\n"
            f"*   Provide a concise and informative answer.\n"
            f"*   Use markdown formatting to structure your response (e.g., headings, bullet points, numbered lists).\n"
            f"*   If the document text does not contain the answer, clearly state that you cannot answer the question based on the provided information.\n"
            f"*   Avoid unnecessary introductory or concluding remarks.\n"
        )

        response = chat.send_message(
            combined_prompt,
            generation_config={
                "temperature": 0.5,  # Lower temperature for more focused answers
                "top_p": 0.95,
                "max_output_tokens": 700
            },
            stream=False
        )

        # Post-Processing:  Remove redundant headers if the AI includes them
        ai_response = response.text
        if ai_response.startswith("### 🤖 **AI Answer:**"):
            ai_response = ai_response[len("### 🤖 **AI Answer:**"):].strip()  #remove the header


        # ✅ Improved Formatting and Clarity
        formatted_response = f"""
<div class="ai-response">
  <h3>🤖 AI Response</h3>
  <div class="ai-content">
    {ai_response}
  </div>
 
</div>
"""

        return jsonify({"response": formatted_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📌 Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
