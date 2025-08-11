from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, trace, function_tool
import json

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
    
import asyncio

if __name__ == "__main__":
    jobdesc = """My team needs an expert developer who has extensive knowledge on dot net programming and AWS concepts.
                The developer should be proficient in oops concept and possess strong understanding of software design principals."""
    criteria = """Experience in .NET Core, ASP.NET, Python, and RESTful APIs.
                The candidate should have at least 5 years of experience in software development."""
    message = """Please prepare 25 questions for the interview based on the job description and criteria provided.
                The questions should be scenario-based with multiple options to choose from.
                The questions should be designed to assess the candidate's problem-solving abilities and technical knowledge."""

    async def main():
        question_preparer = InterviewQuestionPreparer(jobdesc, criteria)
        prepared_questions = await question_preparer.execute_agent(message)
        # Assuming the response is in JSON format, you can parse it if needed
        print(prepared_questions)

    asyncio.run(main())
