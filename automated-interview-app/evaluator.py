from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, trace, function_tool
import json

load_dotenv(override=True)

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
    
import asyncio

if __name__ == "__main__":
    jobdesc = """My team needs an expert developer who has extensive knowledge on dot net programming and AWS concepts.
                The developer should be proficient in oops concept and possess strong understanding of software design principals."""
    
    criteria = """Experience in .NET Core, ASP.NET, Python, and RESTful APIs.
                The candidate should have at least 5 years of experience in software development."""
    
    message = "Evaluate the candidate's answers and provide a detailed evaluation report."  
    
    answer_json = """
    {
        "questions": [
            {
                "question": "You need to implement a RESTful API for a new service that interacts with a database. What approach would you take to ensure scalability and performance?",
                "options": [
                    "Use caching mechanisms like Redis",
                    "Implement API rate limiting",
                    "Use gRPC instead of REST",
                    "Utilize a SQL database instead of NoSQL",
                    "Create multiple microservices for distinct functionalities"
                ],
                "answer": "Use caching mechanisms like Redis"
            },
            {
                "question": "In a .NET Core application, you encounter a performance issue when connecting to the database. What is your first course of action?",
                "options": [
                    "Profile the application to find bottlenecks",
                    "Increase the database server's resources",
                    "Implement connection pooling",
                    "Switch to a NoSQL database",
                    "Check for any locking issues in the database"
                ],
                "answer": "Profile the application to find bottlenecks"
            },
            {
                "question": "You are tasked with designing a new feature that requires integrating an existing Python service with an ASP.NET Core application. What would be a suitable approach?",
                "options": [
                    "Use REST APIs for communication",
                    "Directly invoke the Python code within the .NET application",
                    "Convert the Python service to .NET Core",
                    "Use message queuing for asynchronous communication",
                    "Implement a shared database between services"
                ],
                "answer": "Use REST APIs for communication"
            },
            {
                "question": "While maintaining a legacy ASP.NET application, you notice the code lacks documentation and structure. What methodology would you apply to improve its maintainability?",
                "options": [
                    "Refactor the code to follow SOLID principles",
                    "Write unit tests to ensure functionality",
                    "Document the code without making any structural changes",
                    "Use design patterns to improve code readability",
                    "Rewrite the application from scratch"
                ],
                "answer": "Refactor the code to follow SOLID principles"
            },
            {
                "question": "You have to create a generic repository pattern in .NET. Which of the following options represents the correct approach?",
                "options": [
                    "Create a base repository class that implements CRUD operations",
                    "Use Entity Framework directly without a repository",
                    "Create a separate repository for each entity type",
                    "Use dependency injection for repositories",
                    "Create a repository interface with generic type parameters"
                ],
                "answer": "Create a repository interface with generic type parameters"
            },
            {
                "question": "In AWS, you're tasked with deploying a scalable .NET Core application. Which service would you choose for hosting?",
                "options": [
                    "AWS Lambda for a serverless approach",
                    "Amazon EC2 for full control over the server",
                    "Elastic Beanstalk for easy deployment and scaling",
                    "Amazon ECS for containerized application management",
                    "Amazon Lightsail for a simple use case"
                ],
                "answer": "Elastic Beanstalk for easy deployment and scaling"
            },
            {
                "question": "You are working on a project where you need to ensure that the software is bug-free before production. How would you approach quality assurance?",
                "options": [
                    "Implement test-driven development (TDD)",
                    "Only perform manual testing",
                    "Use automated UI testing tools exclusively",
                    "Run tests after deployment",
                    "Implement continuous integration and continuous deployment (CI/CD) with automated tests"
                ],
                "answer": "Implement continuous integration and continuous deployment (CI/CD) with automated tests"
            },
            {
                "question": "You have been asked to learn a new technology on the job. What would be your strategy to adapt quickly and effectively?",
                "options": [
                    "Focus on online courses and tutorials",
                    "Seek guidance from experienced team members",
                    "Read documentation and practice hands-on",
                    "Join communities and forums for additional help",
                    "All of the above"
                ],
                "answer": "All of the above"
            },
            {
                "question": "While designing a critical module, you need to ensure loose coupling and high cohesion. What is the best design principle to follow?",
                "options": [
                    "Dependency Inversion Principle",
                    "Liskov Substitution Principle",
                    "Interface Segregation Principle",
                    "Single Responsibility Principle",
                    "Open/Closed Principle"
                ],
                "answer": "Dependency Inversion Principle"
            },
            {
                "question": "You are developing a web application and need to store sensitive user data. What is the best practice for handling this data safely?",
                "options": [
                    "Encrypt the data before storing it",
                    "Store it in plain text and secure access",
                    "Only store user IDs instead of sensitive data",
                    "Store sensitive data in a third-party service",
                    "Use hashing for all data"
                ],
                "answer": "Encrypt the data before storing it"
            },
            {
                "question": "Your application frequently faces high traffic, leading to slow response times. What would be your approach to improve this?",
                "options": [
                    "Implement server-side caching",
                    "Upgrade the server configuration",
                    "Increase database storage capacity",
                    "Add more servers without load balancing",
                    "Optimize the application code"
                ],
                "answer": "Implement server-side caching"
            },
            {
                "question": "In the context of OOP, how can you ensure that your classes adhere to the Open/Closed principle?",
                "options": [
                    "Make classes abstract and extensible",
                    "Ensure classes cannot be modified once created",
                    "Use interfaces to define behavior",
                    "Group related classes together in modules",
                    "All of the above"
                ],
                "answer": "All of the above"
            },
            {
                "question": "You are reviewing a piece of code that seems to violate the DRY (Don't Repeat Yourself) principle. What action should you take?",
                "options": [
                    "Refactor the code to create reusable functions",
                    "Leave it as it is to avoid breaking functionality",
                    "Document the repeats in comments",
                    "Ignore it since it works fine",
                    "Replace the entire module with a new one"
                ],
                "answer": "Refactor the code to create reusable functions"
            },
            {
                "question": "You need to consume a third-party REST API in your .NET application. What should you consider to ensure efficient error handling?",
                "options": [
                    "Implement a try-catch around the API call",
                    "Log the error details for troubleshooting",
                    "Check if the API is up before each call",
                    "Implement a retry strategy for failed calls",
                    "Validate inputs before making the call"
                ],
                "answer": "Implement a retry strategy for failed calls"
            },
            {
                "question": "Your team is debating whether to use Python for data analysis versus C#. What factors would influence your decision?",
                "options": [
                    "Team expertise in each language",
                    "Performance of the libraries available",
                    "Deployment requirements for each language",
                    "Community support and resources available",
                    "All of the above"
                ],
                "answer": "All of the above"
            },
            {
                "question": "In an AWS setup, you need to ensure that your application can access services securely. What is the best practice for managing access?",
                "options": [
                    "Use IAM roles for service access",
                    "Hard-code credentials in your application",
                    "Use public access for all services",
                    "Revise access settings whenever needed",
                    "Monitor access logs only during audits"
                ],
                "answer": "Use IAM roles for service access"
            },
            {
                "question": "To enhance your .NET application’s security, which layer should you primarily focus on?",
                "options": [
                    "Database access layer",
                    "Frontend validation layer",
                    "Backend logic layer",
                    "Authentication and authorization layer",
                    "Logging and monitoring layer"
                ],
                "answer": "Authentication and authorization layer"
            },
            {
                "question": "You are working on a microservices architecture and need to ensure that services can communicate effectively. What's your best option?",
                "options": [
                    "Use an API Gateway",
                    "Directly connect services with each other",
                    "Use shared databases between services",
                    "Communicate solely with synchronous calls",
                    "Use message brokers for asynchronous communication"
                ],
                "answer": "Use an API Gateway"
            },
            {
                "question": "How would you handle a situation where a critical bug has been discovered in production?",
                "options": [
                    "Deploy a rollback to the previous stable version",
                    "Ignore it to focus on new feature development",
                    "Fix the bug in the next scheduled release",
                    "Create a hotfix and deploy immediately",
                    "Communicate the bug to the users"
                ],
                "answer": "Create a hotfix and deploy immediately"
            },
            {
                "question": "When optimizing a .NET application for performance, which profiling tool would you consider to identify bottlenecks?",
                "options": [
                    "Visual Studio Diagnostic Tools",
                    "Performance Analyzer of AWS",
                    "Fiddler for API calls",
                    "JMeter for load testing",
                    "Entity Framework Profiler"
                ],
                "answer": "Visual Studio Diagnostic Tools"
            },
            {
                "question": "To ensure adhere to industry best practices, what should you prioritize in your software development process?",
                "options": [
                    "Regular code reviews",
                    "Writing extensive documentation",
                    "Unit testing for critical components",
                    "Following agile methodologies",
                    "All of the above"
                ],
                "answer": "All of the above"
            },
            {
                "question": "In your RESTful service design, you encounter a need for versioning. What strategy would you adopt?",
                "options": [
                    "Use URL-based versioning",
                    "Never version the API",
                    "Embed the version in request headers",
                    "Use query parameters for versioning",
                    "Both URL-based and query parameters"
                ],
                "answer": "Use URL-based versioning"
            },
            {
                "question": "To communicate effectively within your development team, which method do you find most beneficial?",
                "options": [
                    "Daily stand-up meetings",
                    "Using collaborative coding tools like Git",
                    "Writing detailed documentation",
                    "Random brainstorming sessions",
                    "Periodic email updates"
                ],
                "answer": "Daily stand-up meetings"
            }
        ]
    }

    """
    async def main():
        evaluator = InterviewEvaluator(jobdesc, criteria, answer_json)
        evaluation = await evaluator.execute_evaluator_agent(message)
        # Assuming the response is in JSON format, you can parse it if needed
        print(evaluation)

    asyncio.run(main())
