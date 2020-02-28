# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Activity

from coco_microsoft_bot_framework import CoCoActivityHandler

from lxml import etree

from direct_line_session import DirectLineAPI
from config import DefaultConfig

CONFIG = DefaultConfig()


def fetch_triggered_components(text_with_tags):
    """
    fetch triggered components from text tags .

    Arguments:
        text_with_tags: (string) Text response.
    Returns:
         text_response, triggered components list (tuple).
    """
    xml_response = etree.fromstring(f"<resp>{text_with_tags}</resp>")

    text_response = xml_response.text

    triggered_comps = [ecomp.attrib.get("id") for ecomp in xml_response.xpath("//component")]

    return text_response if text_response else "", triggered_comps


class MyBot(CoCoActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    async def on_message_activity(self, turn_context: TurnContext):
        if self.is_component_active():
            # This is for when we are still in coco context to return response from there
            # and wait for the next message
            await self.call_active_component(turn_context)
            return

        message_id = await self.direct_line_session.send_message(
            turn_context.activity.text)

        response = await self.direct_line_session.get_message_response(message_id)

        response_text_with_tags = response.get("text", "")

        text_response, triggered_comps = fetch_triggered_components(
            response_text_with_tags)

        response["text"] = text_response

        await turn_context.send_activity(Activity().deserialize(response))

        if len(triggered_comps) > 0:
            await self.activate_component(turn_context, triggered_comps[0])

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        # Start Session With Watson Assistant.
        self.direct_line_session = DirectLineAPI(CONFIG.DIRECT_LINE_SECRET)

        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def on_end_of_conversation_activity(
        self, turn_context: TurnContext
    ):
        self.watson_session.delete()
