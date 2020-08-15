# -*- coding: utf-8 -*-
import time

from alipay import AliPay
import config
import datetime
import random

try:
    alipay = AliPay(
        appid=config.appid,
        app_notify_url=None,  # 默认回调url，不要改
        app_private_key_string=config.app_private_key_string,
        alipay_public_key_string=config.alipay_public_key_string,
        sign_type="RSA2",
    )
except Exception as e:
    config.logger1.exception('alifacepay.Alipay对象创建失败，请检查公钥和密钥是否配置正确，抛出异常:{}'.format(e))


def get_trade_id():
    """
    创建订单号
    :return:
    """
    now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(0, 99)
    if random_num <= 10:
        random_num = str(0) + str(random_num)
    unique_num = str(now_time) + str(random_num)
    return unique_num


def submit(price, subject, trade_id):
    try:
        order_string = alipay.api_alipay_trade_precreate(
            subject=subject,
            out_trade_no=trade_id,
            total_amount=price,
            qr_code_timeout_express=config.PAY_TIMEOUT
        )
        config.logger1.info("submit order_string:{}".format(order_string))
        if order_string['msg'] == 'Success':
            return_data = {
                'status': 'Success',
                'data': '{}'.format(order_string['qr_code'])
            }
            return return_data
        else:
            config.logger1.error("alifacepay.submit 提交订单失败，返回结果:{}".format(order_string))
            return_data = {
                'status': 'Failed',
                'data': 'API请求失败'
            }
            return return_data
    except Exception as e:
        config.logger1.exception("alifacepay.submit 支付宝当面付API请求失败,抛出异常:{}".format(e))
        return_data = {
            'status': 'Failed',
            'data': 'API请求失败'
        }
        return return_data


def donate(money, out_trade_no):
    subject = "YYetsTelegramBot捐赠渠道"
    submit_data = submit(money, subject, out_trade_no)
    if submit_data.get('status') == "Success":
        return submit_data.get('data')
    else:
        return "Failed"


def check_donate(out_trade_no):
    """
    检查是否支付成功，在5分钟内未支付则取消订单
    :param out_trade_no:
    :return:
    """
    paid = False
    status = ''
    for i in range(50):
        time.sleep(5)
        result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        config.logger1.info("alifacepay.check_donate result:{}".format(result))
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            config.logger1.info("alifacepay.check_donate 支付成功，向用户发送信息")
            paid = True
            status = "支付成功"
            break

    if paid is False:
        alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
        config.logger1.error("alifacepay.check_donate 超时未支付，取消订单")
        status = "超时未支付"

    return status


if __name__ == '__main__':
    trade_id = get_trade_id()
    print(trade_id)
    price = "0.1"
    subject = "测试"
    out_trade_no = "2020081519364721"
    donate(price, trade_id)