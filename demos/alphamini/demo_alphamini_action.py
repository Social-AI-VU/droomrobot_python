import time

from sic_framework.devices.alphamini import Alphamini
from sic_framework.devices.common_mini.mini_animation import MiniActionRequest
from sic_framework.devices.common_mini.mini_speaker import MiniSpeakersConf
from mini import mini_sdk as MiniSdk
from mini.apis.api_action import GetActionList, GetActionListResponse, RobotActionType
from mini.apis.api_action import MoveRobot, MoveRobotDirection, MoveRobotResponse
from mini.apis.api_action import PlayAction, PlayActionResponse
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice
import asyncio
"""
This demo shows how to make Nao perform predefined postures and animations.
"""

mini = Alphamini(ip="10.0.0.155",
            mini_id="00199",
            mini_password="alphago",
            redis_ip="10.0.0.107",
            )
# mini.animation.request(MiniActionRequest("codemao3", "expression", mini_id="00199"))
# print("Animation request sent")
mini.animation.request(MiniActionRequest("018", "action", mini_id="00199"))


