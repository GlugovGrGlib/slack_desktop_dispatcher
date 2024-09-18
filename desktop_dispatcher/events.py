import logging

from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.models.blocks import (
    ActionsBlock,
    ButtonElement,
    DividerBlock,
    Option,
    PlainTextObject,
    SectionBlock,
    StaticSelectElement,
)

from .models import Desktop, TempDesktopSelection
from .session import SessionLocal
from .utils import get_env_variable, notify_channel

app = App(token=get_env_variable("SLACK_BOT_TOKEN"))
slack_client = WebClient(token=get_env_variable("SLACK_BOT_TOKEN"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = SessionLocal()


@app.command("/desktop")
def list_of_desktops(ack, body, say):
    """
    Responds to the '/desktop' slash command by displaying the user's current desktop
    with a 'Leave Desktop' button if occupied, a list of available desktops if not,
    or informs if none are available.

    Args:
        ack (function): The function to acknowledge receipt of the slash command.
        body (dict): The incoming slash command payload from Slack.
        say (function): The function to send a message back to Slack.
    """
    ack()
    try:
        user_id = body["user_id"]
        free_desktops = session.query(Desktop).filter(Desktop.occupied == False).all() 
        occupied_desktop = (
            session.query(Desktop)
            .filter(Desktop.occupied == True, Desktop.user_id == user_id)
            .first()
        )

        if occupied_desktop:
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
            say(blocks=blocks)

        elif free_desktops:
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

            say(blocks=blocks)
        else:
            say(
                "⛔  Error getting available Desktops. Please contact maintainer"
            )
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        say("⛔  An error occurred. Please contact maintainer.")


@app.action("desktop_selection")
def handle_desktop_selection(ack, body, say):
    """
    Handles the desktop selection action.

    When a user selects a desktop, this function marks it as occupied and
    provides a confirmation message with a 'Leave Desktop' button.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack.
    """
    ack()
    selected_option = body["actions"][0]["selected_option"]
    desktop_id = selected_option["value"]
    desktop_name = selected_option["text"]["text"]
    user_id = body["user"]["id"]

    try:
        desktop = session.query(Desktop).filter(Desktop.id == desktop_id).first()
        if desktop and not desktop.occupied:
            desktop.occupied = True
            desktop.user_id = user_id
            session.commit()

            blocks = [
                SectionBlock(text=f"🟢  You are using *{desktop_name}*"),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text="Change desktop",
                            action_id="change_desktop",
                        ),
                        ButtonElement(
                            text="Leave",
                            action_id="leave_desktop",
                            value=str(desktop.id),
                            style="danger",
                        ),
                    ]
                ),
                DividerBlock(),
            ]

            say(blocks=blocks)
            notify_channel(f"🖥️    *<@{user_id}>* is now using {desktop_name}")
        else:
            say("⛔  The selected desktop is no longer available. Please try again.")
    except Exception as e:
        logger.error(f"An error occurred while processing selection: {str(e)}")
        say("⛔  An error occurred. Please contact maintainer.")


@app.action("leave_desktop")
def handle_leave_desktop(ack, body, say):
    """
    Handles the action of leaving a desktop

    When a user chooses to leave a desktop, this function marks the desktop as unoccupied
    and shows the list of available desktops again.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack.
    """
    ack()
    desktop_id = body["actions"][0]["value"]
    user_id = body["user"]["id"]

    try:
        desktop = (
            session.query(Desktop)
            .filter(Desktop.id == desktop_id, Desktop.user_id == user_id)
            .first()
        )
        if desktop:
            desktop.occupied = False
            desktop.user_id = None
            session.commit()
            say(f"⚪  You left: *{desktop.name}*")
            notify_channel(f"⚪  *<@{user_id}>* left *{desktop.name}*")
        else:
            say(f"⛔  You are not currently occupying this desktop. {desktop.name}")
    except Exception as e:
        logger.error(f"An error occurred while processing leave request: {str(e)}")
        say("⛔  An error occurred. Please contact maintainer.")


@app.action("new_desktop_selection")
def handle_new_desktop_selection(ack, body, say):
    """
    Handles the selection of a new desktop from the dropdown menu.

    This function stores the selected desktop ID in temporary storage for later use
    when confirming the desktop change.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack (unused in this function).
    """
    ack()
    selected_desktop_id = body["actions"][0]["selected_option"]["value"]
    user_id = body["user"]["id"]
    
    try:
        temp_selection = session.query(TempDesktopSelection).filter_by(user_id=user_id).first()
        
        if temp_selection:
            # Update existing selection
            temp_selection.desktop_id = selected_desktop_id
        else:
            # Create new selection
            temp_selection = TempDesktopSelection(user_id=user_id, desktop_id=selected_desktop_id)
            session.add(temp_selection)
    
        session.commit()
    except Exception as e:
        logger.error(f"Error storing temporary desktop selection: {str(e)}")
        say("⛔ An error occurred. Please try again or contact the maintainer.")


@app.action("confirm_desktop_change")
def handle_confirm_desktop_change(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    
    try:
        temp_selection = session.query(TempDesktopSelection).filter_by(user_id=user_id).first()
        if not temp_selection:
            say("⛔ No desktop selected. Please try again.")
            return

        new_desktop_id = temp_selection.desktop_id

        current_desktop = (
            session.query(Desktop)
            .filter(Desktop.occupied == True, Desktop.user_id == user_id)
            .first()
        )

        new_desktop = session.query(Desktop).filter(Desktop.id == new_desktop_id).first()

        if not new_desktop or new_desktop.occupied:
            say("⛔ The selected desktop is no longer available. Please try again.")
            return

        # Mark the current desktop as unoccupied
        if current_desktop:
            current_desktop.occupied = False
            current_desktop.user_id = None

        # Mark the new desktop as occupied
        new_desktop.occupied = True
        new_desktop.user_id = user_id

        # Clear the temporary selection from the database
        session.delete(temp_selection)
        
        session.commit()

        say(f"🟢 You changed {current_desktop.name} -> *{new_desktop.name}*")
        notify_channel(f"🖥️ *<@{user_id}>* changed desktop from *{current_desktop.name}* -> *{new_desktop.name}*")

    except Exception as e:
        logger.error(f"An error occurred while changing desktop: {str(e)}")
        say("⛔ An error occurred. Please contact maintainer.")
        # Rollback the session in case of error
        session.rollback()


@app.action("cancel_desktop_change")
def handle_cancel_desktop_change(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    
    try:
        temp_selection = session.query(TempDesktopSelection).filter_by(user_id=user_id).first()
        if temp_selection:
            session.delete(temp_selection)
            session.commit()

        say("⛔ Desktop change cancelled.")
    except Exception as e:
        logger.error(f"Error cancelling desktop change: {str(e)}")
        say("⛔ An error occurred while cancelling. Please try again or contact the maintainer.")


@app.action("change_desktop")
def handle_change_desktop(ack, body, say):
    """
    Handles the action of changing a desktop

    When a user chooses to change a desktop, this function displays a list of available desktops
    and provides options to confirm or cancel the change.

    Args:
        ack (function): The function to acknowledge receipt of the action from Slack.
        body (dict): The payload of the incoming action request from Slack.
        say (function): The function to send a message back to Slack.
    """
    ack()
    user_id = body["user"]["id"]

    try:
        # Get the current desktop for the user
        current_desktop = (
            session.query(Desktop)
            .filter(Desktop.occupied == True, Desktop.user_id == user_id)
            .first()
        )

        if not current_desktop:
            say("⛔  You are not currently using any desktop.")
            return

        # Get all available desktops
        available_desktops = session.query(Desktop).filter(Desktop.occupied == False).all()

        # Create options for the dropdown
        options = [
            Option(text=PlainTextObject(text=desktop.name), value=str(desktop.id))
            for desktop in available_desktops
        ]

        blocks = [
            SectionBlock(text=f"🟢  You are currently using *{current_desktop.name}*"),
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

        say(blocks=blocks)

    except Exception as e:
        logger.error(f"An error occurred while processing change desktop request: {str(e)}")
        say("⛔  An error occurred. Please contact maintainer.")
