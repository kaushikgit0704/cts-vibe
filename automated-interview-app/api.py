from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, trace, function_tool
import asyncio
import json
import os

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv(override=True)

class InterviewQuestionPreparer:
    def __init__(self, jobdesc, criteria):
        self.jobdesc = jobdesc
        self.criteria = criteria

    def create_interviewer_system_prompt(self):
        """Creates a system prompt for the interviewer agent."""
        return f"""You are a technical guru working for Cognizant Technology Solutions pvt Limited.
        Your job is to prepare questions to interview prospective cadidates on their technical skills based on given job description {self.jobdesc}.
        You must prepare questions based on the criteria {self.criteria}.
        Make sure to prepare scenario based questions with multiple options for the candidate to choose from. All the questions must have multiple options to choose from.
        There should be at least 5 options for each question.
        Some of the questions may have multiple correct answers.
        The questions should be designed to assess the candidate's problem-solving abilities and technical knowledge.
        The questions should be relevant to the job description and criteria provided.
        The questions should be challenging and should require the candidate to demonstrate their understanding of the concepts.
        The questions should be scenario-based, allowing candidates to apply their knowledge in practical situations.
        The questions should be designed to evaluate the candidate's ability to think critically and solve problems effectively.
        The questions should be designed to assess the candidate's experience and expertise in the relevant technologies and methodologies.
        The questions should be designed to assess the candidate's technical skills and knowledge relevant to the job role.
        The questions should be varied in difficulty to ensure a comprehensive assessment of the candidate's abilities.
        The questions should be designed to encourage candidates to explain their thought process and reasoning.
        The questions should be designed to assess the candidate's ability to work under pressure and make decisions quickly.
        The questions should be designed to assess the candidate's ability to communicate technical concepts effectively.
        The questions should be designed to assess the candidate's ability to adapt to new technologies and methodologies.
        The questions should be designed to assess the candidate's understanding of best practices in software development and engineering.
        The questions should be designed to assess the candidate's familiarity with industry standards and practices.
        The questions should be challenging and relevant to the job role and experience level.
        The questions should be clear and concise, avoiding any ambiguity.
        You must create 25 questions based on the above criteria and job description which can be answered in 30 minutes by an expert candidate.
        You must return a json object with the following structure:
        {{
            "questions": [
                {{
                    "question": "Question text here",
                    "options": [
                        "Option 1",
                        "Option 2",
                        "Option 3",
                        "Option 4",
                        "Option 5"
                    ]
                }},
                # Add more questions here
            ]
        }}
        Return only the json object without any additional text or explanation.
        """
    
    @function_tool
    def get_json(content: str, filename: str = "questions.json") -> dict:
        try:
            # Step 1: Remove escaped newlines
            clean_string = content.encode('utf-8').decode('unicode_escape')

            # Step 2: Convert to dictionary
            data = json.loads(clean_string)
            with open(filename, "w") as file:
                    file.write(clean_string)       
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")

    async def execute_agent(self, message):
        """Executes the agent to prepare interview questions."""
        evaluator_agent = Agent(
            name='Question Setter Agent',
            instructions=self.create_interviewer_system_prompt(),
            model='gpt-4o-mini',
            tools=[self.get_json])
                        
        with trace('Automated Technical Evaluation'):
            result = await Runner.run(evaluator_agent, message)
        return result    

class InterviewEvaluator:
    def __init__(self, jobdesc, criteria, interview_json):
        self.jobdesc = jobdesc
        self.criteria = criteria
        self.interview_json = interview_json

    def get_evaluator_prompt(self):
        """Creates a system prompt for the evaluator agent."""
        return f"""You are a technical interview evaluator. 
                Your job is to evaluate the candidate's answers based on the job description {self.jobdesc} and criteria {self.criteria}.
                You will be given a json string containing questions and answers of a candidate.
                The json string will have the following structure:
                {{
                    "questions": [
                        {{
                            "question": "Question text here",
                            "options": [
                                "Option 1",
                                "Option 2",
                                "Option 3",
                                "Option 4",
                                "Option 5"
                            ],
                            "answer": "Candidate's answer here"
                        }},
                        # Add more questions here
                    ]
                }}
                Make sure to evaluate all the answers provided by the candidate.
                You must evaluate the candidate's answers and check if the candidate's answer matches with the correct option from the given options.
                If the candidate's answer matches with the correct option, then consider it as a correct answer.
                If the candidate's answer does not match with the correct option, then consider it as an incorrect answer.
                You must provide a detailed evaluation report based on the candidate's correct and incorrect answers only.
                You do not need to consider the depth of the candidate's answer.
                Analyze the candidate's answers and provide:

                - Strengths
                - Correct Answers if any
                - Incorrect Answers if any
                - Areas of Improvement
                - Technical Knowledge
                - Rank the performance on the scale of 1 to 5 where 1 is for worst performance and 5 is for berst performance.

                Format your response as a detailed evaluation report in json format. 
                The json format should have the following structure:
                {{
                    "evaluation": {{
                        "strengths": "List of strengths",
                        "correct_answers": "List of correct answers if any",
                        "incorrect_answers": "List of incorrect answers if any",                        
                        "technical_knowledge": "Evaluation of technical knowledge",
                        "areas_of_improvement": "List of areas of improvement",
                        "performance_rank": 1  # Rank from 1 to 5
                    }}
                }}
                
                Following is the json string containing questions and answers of a candidate:
                {self.interview_json}
                """   
    
    @function_tool
    def get_evaluationreport_json(content: str, filename: str = "evaluation.json") -> dict:
        try:
            # Step 1: Remove escaped newlines
            clean_string = content.encode('utf-8').decode('unicode_escape')

            # Step 2: Convert to dictionary
            data = json.loads(clean_string)
            with open(filename, "w") as file:
                    file.write(clean_string)       
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")

    async def execute_evaluator_agent(self, message):
        """Executes the agent to prepare interview questions."""       
        evaluator_agent = Agent(
            name='Evaluator Agent',
            instructions=self.get_evaluator_prompt(),
            model='gpt-4o-mini',
            tools=[self.get_evaluationreport_json])
                        
        with trace('Automated Technical Evaluation'):
            result = await Runner.run(evaluator_agent, message)
        return result     

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