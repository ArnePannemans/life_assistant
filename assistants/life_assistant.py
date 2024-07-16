import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from phi.assistant import Assistant
from toolkits.GoogleCalendar import GoogleCalendarToolkit
from phi.llm.openai import OpenAIChat
from functions import date
from dotenv import load_dotenv
from finance_assistant import finance_assistant
from assistants.secretary_assistant import secretary_assistant

load_dotenv()

finance_assistant = finance_assistant
secretary_assistant = secretary_assistant


instructions = [
    "You are a Personal Life Assistant with a team of specialized assistants to help manage various aspects of life.",
    "For financial tasks such as tracking expenses, generating financial reports, and managing monthly expense records, delegate the task to the Finance Assistant.",
    "For calendar-related tasks such as managing events, adding new events, listing upcoming events, and removing events, delegate the task to the Secretary Assistant.",
    "Ensure you clearly specify the task and the relevant details when delegating tasks to your team.",
    "When asked to generate a report or summary, make sure to gather all necessary information from the relevant assistants before providing a final response.",
    "If a task involves both financial and calendar aspects, coordinate between the Finance and Secretary Assistants to complete the task.",
    "Always confirm the successful completion of tasks and provide feedback or follow-up if needed."
]

# Create the Personal Life Assistant with the Calendar Toolkit
personal_assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o", max_tokens=500, temperature=0.3),  # advanced chat model
    name="Personal Life Assistant",
    description="Helps you manage your personal life",
    team=[secretary_assistant, finance_assistant],
    instructions=instructions,
    add_chat_history_to_prompt=True,
    add_chat_history_to_messages=True,
    debug_mode=True
)

answer = personal_assistant.cli_app()

