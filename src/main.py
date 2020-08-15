# -*- coding: utf-8 -*-

import os

import telebot
from telebot import types

import config
import yyetsBot
import alifacepay

TOKEN = os.environ.get('TOKEN') or config.TGBOT_TOKEN
bot = telebot.TeleBot(TOKEN)


def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(str)
        return True
    except (ValueError, TypeError):
        pass

    return False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, '欢迎使用，发送想要的剧集标题，我会帮你搜索。'
                                      '建议使用<a href="http://www.zmz2019.com/">人人影视</a>标准译名',
                     parse_mode='html')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id,
                     '''不会使用？可以查看为你们录制的视频 <a href='https://cdn.jsdelivr.net/gh/AlphaBrock/md_img/macos/20200815001650.mp4'>戳我</a>''',
                     parse_mode='html')


@bot.message_handler(commands=['credits'])
def send_credits(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, '''感谢字幕组的无私奉献！本机器人资源来源:\n
    <a href="http://www.zmz2019.com/">人人影视</a>''', parse_mode='html')


@bot.message_handler(commands=['donate'])
def send_help(message):
    bot.send_chat_action(message.chat.id, 'typing')
    btn_list = []
    size = 3
    markup = types.InlineKeyboardMarkup(size)
    btn_list.append(types.InlineKeyboardButton("0.1元", callback_data='donate:0.11'))
    btn_list.append(types.InlineKeyboardButton("0.5元", callback_data='donate:0.5'))
    btn_list.append(types.InlineKeyboardButton("1元", callback_data='donate:1'))
    markup.add(btn_list[0], btn_list[1], btn_list[2])
    bot.send_message(message.chat.id, "最近有点穷，捐赠点？")
    bot.send_photo(message.chat.id, photo="https://cdn.jsdelivr.net/gh/AlphaBrock/md_img/macos/20200815184151.png", reply_markup=markup)


@bot.message_handler(func=lambda m: True)
def talk_with_user(message):
    """
    此处用于获取用户输入的内容
    :param message:
    :return:
    """
    config.logger1.info("talk_with_user 获取到用户:{}，输入数据:{}".format(message.chat.id, message.text))
    img_data = yyetsBot.download_poster(message.text)
    if img_data is None:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, 'Ops，你查询的资源不存在，换个名称试试？')
    else:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "你想看哪个呢？请点击选择")
        for i in img_data:
            id = i[0]
            channel_cn = i[1]
            cnname = i[2]
            img = i[3]
            bot.send_chat_action(message.chat.id, 'typing')
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("{}:{}".format(channel_cn, cnname),
                                                  callback_data="{}:{}:{}".format(channel_cn, cnname, id)))
            bot.send_photo(message.chat.id, img, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data != 'fix')
def send_video_link(call):
    config.logger1.info('send_video_link 接收到用户选择查看下载链接信息:{}'.format(call.data))
    data = call.data.split(':')
    if "donate" in data:
        donate_money = data[1]
        out_trade_no = alifacepay.get_trade_id()
        qr_code = alifacepay.donate(donate_money, out_trade_no)
        bot.send_chat_action(call.message.chat.id, 'typing')
        if qr_code == "Failed":
            bot.send_message(call.message.chat.id, "Ops，支付网关异常，无法生成捐赠收款码!")
        else:
            bot.send_message(call.message.chat.id, "请在5分钟支付，超时将关闭捐赠通道")
            bot.send_photo(call.message.chat.id, photo='http://api.qrserver.com/v1/create-qr-code/?data={}'.format(qr_code))
            status = alifacepay.check_donate(out_trade_no)
            if status == "支付成功":
                bot.send_message(call.message.chat.id, "感谢你的捐赠，好人一生平安")
            elif status == "超时未支付":
                bot.send_message(call.message.chat.id, "5分钟未支付，关闭捐赠通道")
    else:
        if len(data) == 2:
            # if "season" in data:
            videoID = data[0]
            season = data[1]
            episodeCount = yyetsBot.get_episode_count(season, videoID)
            if is_number(episodeCount) is False:
                bot.send_message(call.message.chat.id, 'Ops，无下载资源提供...')
            else:
                btn_list = []
                size = 3
                markup = types.InlineKeyboardMarkup(size)
                for episode in range(1, int(episodeCount) + 1):
                    btn_list.append(types.InlineKeyboardButton("第%s集" % episode,
                                                               callback_data='{}:{}:{}:{}'.format('电视剧', videoID,
                                                                                                  season,
                                                                                                  episode)))
                for i in range(0, len(btn_list), size):
                    part = btn_list[i:i + size]
                    if len(part) == 3:
                        markup.add(part[0], part[1], part[2])
                    elif len(part) == 2:
                        markup.add(part[0], part[1])
                    else:
                        markup.add(part[0])
                bot.answer_callback_query(call.id, '你要的信息取回来惹')
                bot.edit_message_text('那么看第几集好呢😘', chat_id=call.message.chat.id, message_id=call.message.message_id)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            # elif "episode" in data:
            #     pass
        elif len(data) == 3:
            if data[0] == "电影":
                videoID = data[2]
                movie_links = yyetsBot.get_movie_link(videoID)
                if movie_links is None:
                    bot.send_chat_action(call.message.chat.id, 'typing')
                    bot.send_message(call.message.chat.id, 'Ops，无下载资源提供...')
                else:
                    for movie_link in movie_links:
                        name = movie_link[0]
                        size = movie_link[1]
                        way_name = movie_link[2]
                        address = movie_link[3]
                        info = "资源名称: " + name + "\n" + "文件大小: " + size + "\n" + "下载类型: " + way_name + "\n" + "下载地址: " + address
                        bot.answer_callback_query(call.id, '你要的信息取回来惹')
                        bot.send_message(call.message.chat.id, info)
            elif data[0] == "电视剧":
                videoID = data[2]
                season_count = yyetsBot.get_season_count(videoID)
                markup = types.InlineKeyboardMarkup()
                for season in range(1, int(season_count) + 1):
                    markup.add(types.InlineKeyboardButton
                               ("第%s季" % season,
                                callback_data='{}:{}'.format(videoID, season)))
                bot.answer_callback_query(call.id, '你要的信息取回来惹')
                bot.send_message(call.message.chat.id, "你想看第几季呢？请点击选择", reply_markup=markup)
        elif len(data) == 4:
            videoID = data[1]
            season = data[2]
            episode = data[3]
            tv_links = yyetsBot.get_tv_link(videoID, season, episode)
            for tv_link in tv_links:
                name = tv_link[0]
                size = tv_link[1]
                way_name = tv_link[2]
                address = tv_link[3]
                info = "资源名称: " + name + "\n" + "文件大小: " + size + "\n" + "下载类型: " + way_name + "\n" + "下载地址: " + address
                bot.answer_callback_query(call.id, '你要的信息取回来惹')
                bot.send_message(call.message.chat.id, info)
        else:
            pass


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        config.logger1.exception("__main__ Telegram Bot运行异常，抛出信息:{}".format(e))
