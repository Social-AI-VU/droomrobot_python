from sic_framework.devices.alphamini import Alphamini
from sic_framework.devices.common_mini.mini_animation import MiniActionRequest


"""
Demo: Animation with alphamini.

"""


class AnimationTest:
    def __init__(self, mini_ip, mini_id, mini_password, redis_ip):
            self.mini_id = mini_id
            self.mini = Alphamini(
                ip=mini_ip,
                mini_id=self.mini_id,
                mini_password=mini_password,
                redis_ip=redis_ip
            )

    def run(self):
        self.mini.animation.request(MiniActionRequest(self.mini_id, "018", "action"))


if __name__ == '__main__':
    droomrobot = AnimationTest(mini_ip="192.168.178.111", mini_id="00167", mini_password="alphago",
                               redis_ip="192.168.178.84")
    droomrobot.run()
