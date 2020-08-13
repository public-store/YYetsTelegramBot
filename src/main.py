#!/usr/bin/python
# coding:utf-8

import os
import time
import requests
import yyetsBot

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types
from telebot import apihelper

import config

TOKEN = os.environ.get('TOKEN') or config.TGBOT_TOKEN
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda m: True)
def talk_with_user(message):
    """
    此处用于获取用户输入的内容
    :param message:
    :return:
    """
    config.logger1.info("echo_all 获取到用户:{}，输入数据:{}".format(message.chat.id, message.text))

    img_data = yyetsBot.download_poster(message.text)
    if img_data is None:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, 'Ops，你查询的资源不存在，换个名称试试？')
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "你想看哪个呢？请点击选择")
        for i in img_data:
            channel_cn = i[0]
            cnname = i[1]
            img = i[2]
            bot.send_chat_action(message.chat.id, 'typing')
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("{}:{}".format(channel_cn, cnname), callback_data="{}:{}".format(channel_cn, cnname)))
            bot.send_photo(message.chat.id, img, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data != 'fix')
def send_video_link(call):
    bot.send_chat_action(call.message.chat.id, 'typing')
    dict_r = get(call.data)
    if not dict_r:
        bot.send_message(call.message.chat.id, '我失忆惹，请在聊天框内重新发送你想要的影视名称')
    bot.answer_callback_query(call.id, '文件大小为%s' % dict_r['size'])
    bot.send_message(call.message.chat.id, dict_r['ed2k'] if dict_r['ed2k'] else '哎呀，没有ed2k链接')
    bot.send_message(call.message.chat.id, dict_r['magnet'] if dict_r['magnet'] else '哎呀，没有magnet链接')


if __name__ == '__main__':
    bot.polling(none_stop=True)
