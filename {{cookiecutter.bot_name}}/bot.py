# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

from coco_microsoft_bot_framework import CoCoActivityHandler

from lxml import etree

from direct_line_session import DirectLineAPI
from config import DefaultConfig

CONFIG = DefaultConfig()


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

        response_text_with_tags = await self.direct_line_session.get_message_response(message_id)

        xml_response = etree.fromstring(f"<resp>{response_text_with_tags}</resp>")

        text_response = xml_response.text

        triggred_comps = xml_response.xpath("//component")

        await turn_context.send_activity(text_response)

        if len(triggred_comps) > 0:
            await self.activate_component(turn_context, triggred_comps[0].attrib.get("id"))



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
                await self.activate_component(turn_context, "namer_vp3")

    async def on_end_of_conversation_activity(
        self, turn_context: TurnContext
    ):
        self.watson_session.delete()
