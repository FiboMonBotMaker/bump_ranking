import datetime

ja_time = datetime.timedelta(hours=9)


class Bump_guild():

    def __init__(self):
        self.bumpers = []
        self.channels = {'bump': None, 'chat': None}
        global ja_time
        tmpdate = datetime.datetime.now()
        self.date = datetime.datetime(
            year=tmpdate.year, month=tmpdate.month, day=1) - ja_time

    def get_bumper(self):
        return self.bumpers

    def set_bump_channel(self, bump_channel):
        self.channels['bump'] = bump_channel

    def get_bump_channel(self):
        return self.channels['bump']

    def set_chat_channel(self, chat_channel):
        self.channels['chat'] = chat_channel

    def get_chat_channel(self):
        return self.channels['chat']

    def set_date(self, date: datetime.datetime):
        self.date = date

    def get_date(self):
        return self.date

    def check_channels(self, command, channel_id):
        return channel_id == self.channels[command[1]]
