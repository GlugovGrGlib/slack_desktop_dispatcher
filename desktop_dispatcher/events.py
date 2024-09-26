import logging

from sqlalchemy import select

from .models import Desktop, TempDesktopSelection
from .utils import (
    get_session,
    notify_channel,
    handle_free_desktops_block,
    handle_occupied_desktop_block,
    get_temp_selection,
    get_desktops,
    update_desktop_status,
    get_available_desktops,
)
from .slack_client import app


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command("/desktop")
async def list_of_desktops(ack, body, say):
    """
    Handles the '/desktop' command, displaying the user's current desktop
    or a list of available desktops

    Args:
        ack (function): The function to acknowledge receipt of the slash command
        body (dict): The incoming slash command payload from Slack
        say (function): The function to send a message back to Slack
    """
    await ack()
    user_id = body["user_id"]

    async with get_session() as session:
        try:
            occupied_desktop = await session.scalar(
                select(Desktop).where(
                    Desktop.occupied == True, Desktop.user_id == user_id
                )
            )

            if occupied_desktop:
                await handle_occupied_desktop_block(occupied_desktop, say)
            else:
                free_desktops = await session.scalars(
                    select(Desktop).where(Desktop.occupied == False)
                )
                await handle_free_desktops_block(free_desktops, say) if free_desktops else await say(
                    text="⛔  Error getting available Desktops. Please contact maintainer"
                )
        except Exception as unexpected_error:
            logger.error(f"An error occurred: {str(unexpected_error)}")
            await say(
                text="⛔  Error getting available Desktops. Please contact maintainer"
            )


@app.action("desktop_selection")
async def handle_desktop_selection(ack, body, say):
    """
    Handles desktop selection by marking it as occupied and confirms the action

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack
        body (dict): The payload of the incoming action request from Slack
        say (function): The function to send a message back to Slack
    """
    await ack()
    selected_option = body["actions"][0]["selected_option"]
    desktop_id = int(selected_option["value"])
    user_id = body["user"]["id"]

    async with get_session() as session:
        try:
            selected_desktop = await session.scalar(
                select(Desktop).where(Desktop.id == desktop_id)
            )
            
            if not selected_desktop.occupied:
                # Notify and display occupied status before making changes to the desktop
                await handle_occupied_desktop_block(selected_desktop, say)
                await notify_channel(f"🖥️   *<@{user_id}>* is now using {selected_desktop.name}")

                selected_desktop.occupied = True
                selected_desktop.user_id = user_id
                await session.commit()
            else:
                await say("⛔  The selected desktop is no longer available. Please try again.")
        except Exception as unexpected_error:
            logger.error(f"An error occurred while processing selection: {str(unexpected_error)}")
            await say("⛔  An error occurred. Please contact maintainer.")


@app.action("leave_desktop")
async def handle_leave_desktop(ack, body, say):
    """
    Handles leave a desktop by marking as unoccupied and shows the list of desktops

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack
        body (dict): The payload of the incoming action request from Slack
        say (function): The function to send a message back to Slack
    """
    await ack()
    desktop_id = int(body["actions"][0]["value"])
    user_id = body["user"]["id"]

    async with get_session() as session:
        try:
            desktop = await session.scalar(
                select(Desktop).where(
                    Desktop.id == desktop_id, Desktop.user_id == user_id
                )
            )

            if desktop:
                # Notify and display leave status before making changes to the desktop
                await say(f"⚪  You left: *{desktop.name}*")
                await notify_channel(f"⚪  *<@{user_id}>* left *{desktop.name}*")

                desktop.occupied = False
                desktop.user_id = None
                await session.commit()
            else:
                await say(text="⛔  You are not currently occupying this desktop.")
        except Exception as unexpected_error:
            logger.error(f"An error occurred while processing leave request: {str(unexpected_error)}")
            await say(text="⛔  An error occurred. Please contact maintainer.")


@app.action("new_desktop_selection")
async def handle_new_desktop_selection(ack, body, say):
    """
    Handles the selection of a new desktop and stores the selected desktop

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack
        body (dict): The payload of the incoming action request from Slack
        say (function): The function to send a message back to Slack (unused in this function)
    """
    await ack()
    selected_desktop_id = int(body["actions"][0]["selected_option"]["value"])
    user_id = body["user"]["id"]

    async with get_session() as session:
        try:
            temp_selection = await session.scalar(
                select(TempDesktopSelection).where(
                    TempDesktopSelection.user_id == user_id
                )
            )

            if temp_selection:
                temp_selection.desktop_id = selected_desktop_id
            else:
                temp_selection = TempDesktopSelection(
                    user_id=user_id, desktop_id=selected_desktop_id
                )
                session.add(temp_selection)

            await session.commit()
        except Exception as unexpected_error:
            logger.error(
                f"Error storing temporary desktop selection: {str(unexpected_error)}"
            )
            await say(
                text="⛔ An error occurred. Please try again or contact the maintainer."
            )


@app.action("confirm_desktop_change")
async def handle_confirm_desktop_change(ack, body, say):
    """
    Handles the confirmation of a desktop change by validating the selected desktop 
    and updating the user's current desktop accordingly.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack.
    """
    await ack()
    user_id = body["user"]["id"]

    async with get_session() as session:
        try:
            # Get the new desktop ID from the database
            temp_selection = await get_temp_selection(session, user_id)
            if not temp_selection:
                say("⛔ No desktop selected. Please try again.")
                return

            new_desktop_id = temp_selection.desktop_id

            current_desktop, new_desktop = await get_desktops(session, user_id, new_desktop_id)

            if not new_desktop or new_desktop.occupied:
                say("⛔ The selected desktop is no longer available. Please try again.")
                return

            await say(
                text=f"🟢 You changed {current_desktop.name} -> *{new_desktop.name}*"
            )
            await notify_channel(
                f"🖥️ *<@{user_id}>* changed desktop from *{current_desktop.name}* -> *{new_desktop.name}*"
            )

            await update_desktop_status(session, current_desktop, new_desktop, user_id, temp_selection)
        except Exception as unexpected_error:
            logger.error(f"An error occurred while changing desktop: {str(unexpected_error)}")
            await say(text="⛔ An error occurred. Please contact maintainer.")


@app.action("cancel_desktop_change")
async def handle_cancel_desktop_change(ack, body, say):
    """
    Handles the cancellation of a desktop change request by removing any temporary
    selection stored for the user.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack.
    """
    await ack()
    user_id = body["user"]["id"]

    async with get_session() as session:
        try:
            temp_selection = await get_temp_selection(session, user_id)

            if temp_selection:
                await session.delete(temp_selection)
                await session.commit()

            await say(text="⛔ Desktop change cancelled.")
        except Exception as unexpected_error:
            logger.error(f"Error cancelling desktop change: {str(unexpected_error)}")
            await say(
                text="⛔ An error occurred while cancelling. Please try again or contact the maintainer."
            )


@app.action("change_desktop")
async def handle_change_desktop(ack, body, say):
    """
    Handles the action of changing a desktop by displaying a list of available desktops 
    and providing options to confirm or cancel the change when a user chooses to do so.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack.
    """
    await ack()
    user_id = body["user"]["id"]

    async with get_session() as session:
        try:
            # Get the current desktop for the user
            current_desktop = await session.scalar(
                select(Desktop).filter(
                    Desktop.occupied == True, Desktop.user_id == user_id)
            )
            if not current_desktop:
                await say(text="⛔  You are not currently using any desktop.")
                return

            await get_available_desktops(session, current_desktop, say)

        except Exception as unexpected_error:
            logger.error(
                f"An error occurred while processing change desktop request: {str(unexpected_error)}"
            )
            await say(text="⛔  An error occurred. Please contact maintainer.")
