# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
# slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)
#
#
# # Create an event listener for "reaction_added" events and print the emoji name
# @slack_events_adapter.on("reaction_added")
# def reaction_added(event_data):
#   emoji = event_data["event"]["reaction"]
#   print(emoji)
import os
import certifi
import ssl as ssl_lib
from slack import WebClient


ssl_context = ssl_lib.create_default_context(cafile=certifi.where())

def init_client() -> WebClient:
    client = WebClient(
        token=os.environ['SLACK_BOT_TOKEN'],
        ssl=ssl_context,
        run_async=True
    )
    return client

async def send_message(client: WebClient, channel: str, text: str):
    client.chat_postMessage(
        channel=channel,
        # text=text
        blocks=[
        		{
        			"type": "section",
        			"text": {
        				"type": "mrkdwn",
        				"text": "This is a mrkdwn section block :ghost: *this is bold*, and ~this is crossed out~, and <https://google.com|this is a link>"
        			}
        		},
        		{
        			"type": "actions",
        			"elements": [
        				{
        					"type": "button",
        					"text": {
        						"type": "plain_text",
        						"text": "Click 1",
        						"emoji": True
        					},
        					"value": "click_me_123"
        				},
        				{
        					"type": "button",
        					"text": {
        						"type": "plain_text",
        						"text": "Click 2",
        						"emoji": True
        					},
        					"value": "click_me_123"
        				}
        			]
        	}]
    )
