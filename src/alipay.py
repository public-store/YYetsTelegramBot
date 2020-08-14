from alipay import AliPay
import config
# 订单超时时间
# m：分钟，只可为整数，建议与config配置的超时时间一致
PAY_TIMEOUT = '5m'

try:
    alipay = AliPay(
        appid=config.appid,
        app_notify_url=None,  # 默认回调url，不要改
        app_private_key_string=config.app_private_key_string,
        alipay_public_key_string=config.alipay_public_key_string,
        sign_type="RSA2",
    )
except Exception as e:
    config.logger1.exception('Alipay对象创建失败，请检查公钥和密钥是否配置正确，抛出异常:{}'.format(e))


def submit(price, subject, trade_id):
    try:
        order_string = alipay.api_alipay_trade_precreate(
            subject=subject,
            out_trade_no=trade_id,
            total_amount=price,
            qr_code_timeout_express=PAY_TIMEOUT
        )
        print(order_string)
        if order_string['msg'] == 'Success':
            pr_code = order_string['qr_code']
            print(pr_code)
            return_data = {
                'status': 'Success',
                'type': 'qr_code',  # url / qr_code
                'data': pr_code
            }
            return return_data
        else:
            print(order_string['msg'])
            return_data = {
                'status': 'Failed',
                'data': 'API请求失败'
            }
            return return_data
    except Exception as e:
        print(e)
        print('支付宝当面付API请求失败')
        return_data = {
            'status': 'Failed',
            'data': 'API请求失败'
        }
        return return_data


def query(out_trade_no):
    try:
        result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            print('用户支付成功')
            return '支付成功'
        else:
            return '支付失败'
    except Exception as e:
        print(e)
        print('支付宝当面付 | 请求失败')
        return 'API请求失败'


def cancel(out_trade_no):
    try:
        alipay.api_alipay_trade_cancel(out_trade_no=out_trade_no)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    submit()