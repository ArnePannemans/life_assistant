from datetime import datetime
from phi.utils.log import logger

def get_todays_date() -> str:
    """Returns today's date in ISO format.

    Returns:
        str: Today's date in ISO format.
    """
    today = datetime.today().isoformat()
    logger.info('Getting today\'s date: %s', today)
    return today