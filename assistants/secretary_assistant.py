import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phi.assistant import Assistant
from toolkits.GoogleCalendar import GoogleCalendarToolkit
from phi.llm.openai import OpenAIChat
from functions import date
from dotenv import load_dotenv


load_dotenv()

# Initialize the Google Calendar Toolkit
calendar_toolkit = GoogleCalendarToolkit(credentials_file="credentials.json")
get_today_date = date.get_todays_date

instructions = [
    "You are a Secretary Assistant responsible for managing calendar-related tasks.",
    "You can add new events, list upcoming events, update existing events, and delete events from the user's Google Calendar.",
    "Ensure all events are recorded accurately with the correct date, time, and details.",
    "When asked to list or manage events, provide detailed information and confirm actions taken."
]

secretary_assistant = Assistant(
    # llm=OpenAIChat(model="gpt-4o", max_tokens=500, temperature=0.3), # advanced chat model
    llm=OpenAIChat(model="gpt-4o", max_tokens=500, temperature=0.3), # cheap model
    name="Secretary assistent",
    description="Helps you manage your personal life, starting with your Google Calendar.",
    tools=[calendar_toolkit, get_today_date],
    instructions=instructions,
    show_tool_calls=True,
    markdown=True,
    read_chat_history=True, # adds a tool that allows the assistant to read chat history when the function is called -> only for explicit calls
    add_chat_history_to_prompt=True, # disable for cheaper use
    add_chat_history_to_messages=True, # disable for cheaper use
    add_references_to_prompt=True,
    debug_mode=True,
)
