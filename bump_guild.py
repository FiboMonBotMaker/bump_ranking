class Bump_guild():

    def __init__(self):
        self.bumpers = []
        self.bump_channel = None
        self.chat_channel = None

    def get_bumper(self):
        return self.bumpers

    def set_bump_channel(self, bump_channel):
        self.bump_channel = bump_channel

    def get_bump_channel(self):
        return self.bump_channel

    def set_chat_channel(self, chat_channel):
        self.chat_channel = chat_channel

    def get_chat_channel(self):
        return self.chat_channel
