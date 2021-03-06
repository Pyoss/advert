import bot_handlers
import config
import buttons
import datahandler
import json
from telebot import types


ad_dict = {}
state_dict = {}


class Ad:
    def __init__(self, chat_id=None, db_id=None, message_id=None):
        if db_id is not None:
            self.message_id = db_id
            info = datahandler.get_ad(self)
            self.author = info[-1][0]
            self.text = info[-1][1]
            self.album = json.loads(info[-1][2])
            ad_dict[config.admin_id] = self
        else:
            self.message_id = int(str(chat_id) + str(message_id))
            self.author = chat_id
            self.album = []
            self.text = ''
            ad_dict[self.author] = self

        self.contacts = None

    def edit_text(self, message):
        self.text = message

    def edit_album(self, photo):
        self.album.append(photo)

    def add_contacts(self):
        self.text = self.text + "\n\n" + self.contacts

    def post(self):
        media_array = []
        for file in self.album:
            media_array.append(types.InputMediaPhoto(file))
        if media_array:
            if len(self.text) < 999:
                media_array[0].caption = self.text
                bot_handlers.send_media_group(config.channel_id, media_array)
            else:
                bot_handlers.send_media_group(config.channel_id, media_array)
                bot_handlers.send_message(config.channel_id, self.text)
        else:
            bot_handlers.send_message(config.channel_id, self.text)
        bot_handlers.send_message(config.admin_id, 'Объявление опубликовано!')

    def public(self, chat_id, name):
        if chat_id in state_dict:
            del state_dict[chat_id]
        if chat_id == config.admin_id:
            self.post()
            datahandler.delete_ad(self)
        else:
            datahandler.save_ad(self)
            text = self.text
            photo = {types.InputMediaPhoto(file) for file in self.album}
            if photo:
                bot_handlers.send_media_group(config.admin_id, photo)
            message = bot_handlers.send_message(config.admin_id, text, reply_markup=buttons.admin_keyboard(self))
            bot_handlers.send_message(chat_id, '{}, объявление отправлено на модерацию и скоро будет опубликовано!'.format(name))
