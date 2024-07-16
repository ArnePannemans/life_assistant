import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from toolkits.ExpenseTracker import ExpenseTrackerToolkit
from functions import date

get_today_date = date.get_todays_date

from dotenv import load_dotenv
load_dotenv()

expense_tracker_toolkit = ExpenseTrackerToolkit()

instructions = [
    "You are a Finance Assistant responsible for managing financial tasks.",
    "You can add new expenses, list expenses, summarize expenses by category, delete expenses, update expenses, and generate financial reports.",
    "Ensure that all expenses are categorized correctly based on predefined categories: Food, Rent, Transportation, Clothing, Material, Paypal, Event, Sports.",
    "When asked to generate a financial report, provide a detailed summary of expenses for the specified period."
]

finance_assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o", temperature=0.3),
    name="Finance Assistant",
    description="Helps you manage your finances, including tracking expenses and generating financial reports.",
    tools=[expense_tracker_toolkit, get_today_date],
    show_tool_calls=True,
    instructions=instructions,
    markdown=True,
    read_chat_history=True,
    add_chat_history_to_prompt=True,
    add_chat_history_to_messages=True,
    debug_mode=True
)

