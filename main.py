from phi.assistant import Assistant
from toolkits.GoogleCalendar import GoogleCalendarToolkit
from phi.llm.openai import OpenAIChat
from functions import date
from dotenv import load_dotenv

load_dotenv()

# Initialize the Google Calendar Toolkit
calendar_toolkit = GoogleCalendarToolkit(credentials_file="credentials.json")
get_today_date = date.get_todays_date

# Create the Personal Life Assistant with the Calendar Toolkit
personal_assistant = Assistant(
    # llm=OpenAIChat(model="gpt-4o", max_tokens=500, temperature=0.3), # advanced chat model
    llm=OpenAIChat(model="gpt-3.5-turbo", max_tokens=500, temperature=0.3), # cheap model
    name="Personal Life Assistant",
    description="Helps you manage your personal life, starting with your Google Calendar.",
    tools=[calendar_toolkit, get_today_date],
    show_tool_calls=True,
    markdown=True,
    read_chat_history=True, # adds a tool that allows the assistant to read chat history when the function is called -> only for explicit calls
    add_chat_history_to_prompt=True, # disable for cheaper use
    add_chat_history_to_messages=True, # disable for cheaper use
    add_references_to_prompt=True,
)

personal_assistant.cli_app(markdown=True)