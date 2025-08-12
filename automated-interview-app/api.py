from flask import Flask, request, jsonify
import asyncio
import json
from automated-interview-app.interviewer import InterviewQuestionPreparer
from automated-interview-app.evaluator import InterviewEvaluator
import os

app = Flask(__name__)

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    data = request.json
    jobdesc = data.get('jobdesc')
    criteria = data.get('criteria')
    message = data.get('message')
    if not all([jobdesc, criteria, message]):
        return jsonify({'error': 'Missing required fields'}), 400

    question_preparer = InterviewQuestionPreparer(jobdesc, criteria)
    prepared_questions = asyncio.run(question_preparer.execute_agent(message))
    # Try to parse as JSON if it's a string
    if not os.path.exists("questions.json"):
        return jsonify({"error": "JSON file not found"}), 404
    
    # Read the JSON file
    with open("questions.json", "r") as f:
        data = json.load(f)
    
    # Send JSON response
    return jsonify(data)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    jobdesc = data.get('jobdesc')
    criteria = data.get('criteria')
    interview_json_str = data.get('interview_json')
    if not all([jobdesc, criteria, interview_json_str]):
        return jsonify({'error': 'Missing required fields'}), 400
    interview_json = json.loads(interview_json_str)
    evaluator = InterviewEvaluator(jobdesc, criteria, interview_json)
    message = "Evaluate the candidate's answers and provide a detailed evaluation report."
    # Execute the evaluation agent
    evaluation_report = asyncio.run(evaluator.execute_evaluator_agent(message))
    # Try to parse as JSON if it's a string
    if not os.path.exists("evaluation.json"):
        return jsonify({"error": "JSON file not found"}), 404
    
    # Read the JSON file
    with open("evaluation.json", "r") as f:
        data = json.load(f)
    
    # Send JSON response
    return jsonify(data)

@app.route('/housekeeping', methods=['get'])
def housekeeping():
    """Endpoint to clean up files created during the interview process."""
    files_to_remove = ["questions.json", "evaluation.json"]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    return jsonify({"message": "Housekeeping completed, files removed."})

if __name__ == "__main__":
    app.run(debug=True, port=5000)