import logging
from contextlib import asynccontextmanager

from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import (
    ActionsBlock,
    ButtonElement,
    DividerBlock,
    Option,
    PlainTextObject,
    SectionBlock,
    StaticSelectElement,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .slack_client import slack_client
from .config import notification_channel_name
from .models import TempDesktopSelection, Desktop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_channel_id_by_name(channel_name):
    """
    Retrieves the ID of a Slack channel by its name.

    Args:
        channel_name (str): The name of the Slack channel to retrieve the ID for.

    Returns:
        str: The ID of the Slack channel, or None if the channel is not found.
    """
    try:
        response = await slack_client.conversations_list()
        channels = response["channels"]
        for channel in channels:
            if channel["name"] == channel_name:
                return channel["id"]
        return None
    except SlackApiError as e:
        logger.error(f"Error fetching channels: {str(e)}")
        return None


async def notify_channel(message):
    """
    Sends a message to a specified Slack channel.

    Args:
        message (str): The message to send to the Slack channel.
    """
    channel_id = await get_channel_id_by_name(notification_channel_name)
    if not channel_id:
        logger.error(f"Channel {notification_channel_name} not found.")
        return
    try:
        await slack_client.chat_postMessage(channel=channel_id, text=message)
    except Exception as e:
        logger.error(f"Failed to send notification to channel: {str(e)}")


@asynccontextmanager
async def get_session():
    from .session import async_session

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def handle_occupied_desktop_block(occupied_desktop, say):
    """Create message blocks for occupied desktops"""
    blocks = [
        SectionBlock(text=f"🟢  You are using *{occupied_desktop.name}*"),
        ActionsBlock(
            elements=[
                ButtonElement(
                    text="Change desktop",
                    action_id="change_desktop",
                ),
                ButtonElement(
                    text="Leave",
                    action_id="leave_desktop",
                    value=str(occupied_desktop.id),
                    style="danger",
                ),
            ]
        ),
        DividerBlock(),
    ]
    await say(
        text=f"You are using {occupied_desktop.name}. Options: Change desktop or Leave.",
        blocks=blocks,
    )


async def handle_free_desktops_block(free_desktops, say):
    """Create message blocks for select free desktops"""
    options = [
        Option(text=PlainTextObject(text=desktop.name), value=str(desktop.id))
        for desktop in free_desktops
    ]

    blocks = [
        DividerBlock(),
        SectionBlock(text="⚪  You're not using any desktop"),
        ActionsBlock(
            elements=[
                StaticSelectElement(
                    placeholder=PlainTextObject(text="Select desktop"),
                    options=options,
                    action_id="desktop_selection",
                )
            ]
        ),
        DividerBlock(),
    ]

    await say(
        text="You're not using any desktop. Please select a desktop.",
        blocks=blocks,
    )


async def handle_new_desktops_block(available_desktops, current_desktop, say):
    """Create message blocks for select new desktops"""

    if not available_desktops:
        await say(
            text=f"You are currently using {current_desktop.name}, but no other desktops are available to switch to.",
            blocks=[
                SectionBlock(text=f"🟢 You are currently using *{current_desktop.name}*"),
                DividerBlock(),
            ]
        )
        return

    options = [
        Option(text=PlainTextObject(text=desktop.name), value=str(desktop.id))
        for desktop in available_desktops
    ]

    blocks = [
        SectionBlock(text=f"🟢 You are currently using *{current_desktop.name}*"),
        ActionsBlock(
            elements=[
                StaticSelectElement(
                    placeholder=PlainTextObject(text="Select new desktop"),
                    options=options,
                    action_id="new_desktop_selection",
                ),
                ButtonElement(
                    text="Change",
                    action_id="confirm_desktop_change",
                    style="primary",
                ),
                ButtonElement(
                    text="Cancel",
                    action_id="cancel_desktop_change",
                ),
            ]
        ),
        DividerBlock(),
    ]
    await say(
        text=f"You are currently using {current_desktop.name}. Select a new desktop to change.",
        blocks=blocks,
    )


async def get_temp_selection(session, user_id):
    """Retrieve the temporary desktop selection for the user."""
    return await session.scalar(
        select(TempDesktopSelection).where(TempDesktopSelection.user_id == user_id)
    )


async def get_desktops(session, user_id, new_desktop_id):
    """Retrieve current and new desktop information."""
    current_desktop_result = await session.execute(
        select(Desktop).filter(Desktop.occupied == True, Desktop.user_id == user_id)
    )
    current_desktop = current_desktop_result.scalar_one_or_none()

    new_desktop_result = await session.execute(
        select(Desktop).filter(Desktop.id == new_desktop_id)
    )
    new_desktop = new_desktop_result.scalar_one_or_none()

    return current_desktop, new_desktop


async def get_available_desktops(session, current_desktop,say):
    """Retrieve available_desktops"""
    try:
        available_desktops = await session.scalars(
            select(Desktop).filter(Desktop.occupied == False)
        )
        if available_desktops:
            raise SQLAlchemyError 
            
        await handle_new_desktops_block(available_desktops, current_desktop, say)
    except SQLAlchemyError as alchemy_error:
        logger.error(
        f"An error occurred while get available desktop: {str(alchemy_error)}"
    )
    await say(text="⛔  All desktops are occupied")


async def update_desktop_status(
    session, current_desktop, new_desktop, user_id, temp_selection
):
    """Update the status of the current and new desktop."""
    if current_desktop:
        current_desktop.occupied = False
        current_desktop.user_id = None

    new_desktop.occupied = True
    new_desktop.user_id = user_id

    await session.delete(temp_selection)
    await session.commit()
