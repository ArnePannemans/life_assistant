import os
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from phi.tools import Toolkit
from phi.utils.log import logger
from typing import List, Dict

from data_models.data_models import CalendarEvent

# Ensure SCOPES is set to include the necessary permissions
SCOPES = ["https://www.googleapis.com/auth/calendar"]

class GoogleCalendarToolkit(Toolkit):
    def __init__(self, credentials_file: str):
        super().__init__(name="google_calendar_toolkit")
        self.credentials_file = credentials_file
        self.service = self._get_service()
        self.register(self.add_event_to_calendar)
        self.register(self.list_events)
        self.register(self.delete_event)
        self.register(self.update_event)

    def _get_service(self):
        logger.info("Getting Google Calendar service.")
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            logger.info("Loaded credentials from token.json.")
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logger.info("Refreshed expired credentials.")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Obtained new credentials.")
            with open("token.json", "w") as token:
                token.write(creds.to_json())
                logger.info("Saved new credentials to token.json.")
        return build("calendar", "v3", credentials=creds)

    def add_event_to_calendar(self, event: Dict) -> str:
        """
        Adds an event to the user's Google Calendar. Use this to add an event to my calendar. If not all data is known, make assumptions.

        Args:
            event (dict): A dictionary containing event details.
                summary (str): The summary or title of the event.
                location (str): The location where the event will take place.
                description (str): A brief description of the event.
                start_datetime (str): The start date and time of the event in ISO format.
                end_datetime (str): The end date and time of the event in ISO format.

        Returns:
            str: The HTML link to the created event or an error message.
        """
        logger.info(f"Adding event to calendar: {event}")
        event_body = {
            'summary': event['summary'],
            'location': event['location'],
            'description': event['description'],
            'start': {
                'dateTime': event['start_datetime'],
                'timeZone': 'Europe/Amsterdam',
            },
            'end': {
                'dateTime': event['end_datetime'],
                'timeZone': 'Europe/Amsterdam',
            },
        }

        try:
            event_result = self.service.events().insert(calendarId='primary', body=event_body).execute()
            logger.info('Event created: %s', event_result.get('htmlLink'))
            return event_result.get('htmlLink')
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"Error: {error}"

    def list_events(self, start_time: str, end_time: str) -> str:
        """
        Lists events in the user's Google Calendar within a specified time range.
        This function is used to get get information about events in the user's Google Calendar,
        but also to get the event IDs to be able to delete or update them.
        Make sure to end time range with "Z".

        Args:
            start_time (str): The start time for the range in ISO format.
            end_time (str): The end time for the range in ISO format.

        Returns:
            str: A JSON string of events within the specified time range or an error message including their ids.
        """
        logger.info(f"Listing events from {start_time} to {end_time}")
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            logger.info(f"Found {len(events)} events.")
            return json.dumps(events)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"Error: {error}"

    def delete_event(self, event_id: str) -> str:
        """
        Deletes an event from the user's Google Calendar.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            str: A message indicating the event was deleted or an error message.
        """
        logger.info(f"Deleting event with ID: {event_id}")
        try:
            self.service.events().delete(calendarId='primary', eventId=event_id).execute()
            logger.info(f"Event with ID {event_id} has been deleted.")
            return f"Event with ID {event_id} has been deleted."
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"Error: {error}"

    def update_event(self, event_id: str, updated_event: Dict) -> str:
        """
        Updates an event in the user's Google Calendar.

        Args:
            event_id (str): The ID of the event to update.
            updated_event (dict): A dictionary containing the updated event details.
                summary (str): The summary or title of the event.
                location (str): The location where the event will take place.
                description (str): A brief description of the event.
                start_datetime (str): The updated start date and time of the event in ISO format.
                end_datetime (str): The updated end date and time of the event in ISO format.

        Returns:
            str: A message indicating the event was updated or an error message.
        """
        logger.info(f"Updating event with ID {event_id} to {updated_event}")
        event_body = {
            'summary': updated_event.get('summary'),
            'location': updated_event.get('location'),
            'description': updated_event.get('description'),
            'start': {
                'dateTime': updated_event.get('start_datetime'),
                'timeZone': 'Europe/Amsterdam',
            },
            'end': {
                'dateTime': updated_event.get('end_datetime'),
                'timeZone': 'Europe/Amsterdam',
            },
        }

        try:
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event_body
            ).execute()
            logger.info(f"Event with ID {event_id} has been updated.")
            return f"Event with ID {event_id} has been updated."
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return f"Error: {error}"
