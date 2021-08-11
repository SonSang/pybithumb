from pybithumb.core import *
from pandas import DataFrame
import pandas as pd
import datetime
import math


class Bithumb:
    def __init__(self, conkey, seckey):
        self.api = PrivateApi(conkey, seckey)

    @staticmethod
    def _convert_unit(unit):
        try:
            unit = math.floor(unit * 10000) / 10000
            return unit
        except:
            return 0

    @staticmethod
    def raise_wrong_status_exception(resp):
        raise Exception("Wrong Response Status: {}".format(resp))

    @staticmethod
    def get_tickers(payment_currency="KRW"):
        """
        빗썸이 지원하는 암호화폐의 리스트
        :param payment_currency : KRW
        :return:
        """
        resp = PublicApi.ticker("ALL", payment_currency)
        if resp['status'] == '0000':
            data = resp['data']
            tickers = [k for k, v in data.items() if isinstance(v, dict)]
            return tickers
        else:
            Bithumb.raise_wrong_status_exception(resp)

    @staticmethod
    def get_current_price(order_currency, payment_currency="KRW"):
        """
        최종 체결 가격 조회
        :param order_currency   : BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN/TRX/ELF/MITH/MCO/OMG/KNC
        :param payment_currency : KRW
        :return                 : price
        """
        resp = PublicApi.ticker(order_currency, payment_currency)
        if resp['status'] == '0000':
            if order_currency != "ALL":
                return float(resp['data']['closing_price'])
            else:
                del resp["data"]['date']
                return resp["data"]
        else:
            Bithumb.raise_wrong_status_exception(resp)

    @staticmethod
    def get_candlestick(order_currency, payment_currency="KRW", chart_intervals="24h"):
        """
        Candlestick API
        :param order_currency   : BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN/TRX/ELF/MITH/MCO/OMG/KNC
        :param payment_currency : KRW
        :param chart_instervals : 24h {1m, 3m, 5m, 10m, 30m, 1h, 6h, 12h, 24h 사용 가능}
        :return                 : DataFrame (시가, 고가, 저가, 종가, 거래량)
                                   - index : DateTime
        """
        resp = PublicApi.candlestick(order_currency=order_currency, payment_currency=payment_currency, chart_intervals=chart_intervals)
        if resp.get('status') == '0000':
            resp = resp.get('data')
            df = DataFrame(resp, columns=['time', 'open', 'close', 'high', 'low', 'volume'])
            df = df.set_index('time')
            df = df[~df.index.duplicated()]
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df.index = pd.to_datetime(df.index, unit='ms', utc=True)
            df.index = df.index.tz_convert('Asia/Seoul')
            df.index = df.index.tz_localize(None)

            return df.astype(float)
        else:
            Bithumb.raise_wrong_status_exception(resp)

    def get_trading_fee(self, order_currency, payment_currency="KRW"):
        """
        거래 수수료 조회
        :param order_currency   : BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN/TRX/ELF/MITH/MCO/OMG/KNC
        :param payment_currency : KRW
        :return                 : 수수료
        """
        resp = self.api.account(order_currency=order_currency,
                                payment_currency=payment_currency)
        if resp['status'] == '0000':
            return float(resp['data']['trade_fee'])
        else:
            Bithumb.raise_wrong_status_exception(resp)

    def get_balance(self, currency):
        """
        거래소 회원의 잔고 조회
        :param currency   : BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN/TRX/ELF/MITH/MCO/OMG/KNC
        :return           : (보유코인, 사용중코인, 보유원화, 사용중원화)
        """
        resp = self.api.balance(currency=currency)
        if resp['status'] == '0000':
            specifier = currency.lower()
            return (float(resp['data']["total_" + specifier]),
                    float(resp['data']["in_use_" + specifier]),
                    float(resp['data']["total_krw"]),
                    float(resp['data']["in_use_krw"]))
        else:
            Bithumb.raise_wrong_status_exception(resp)

    def get_order_completed(self, order_desc):
        """
        거래 완료 정보 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래정보
        """
        resp = self.api.order_detail(type=order_desc[0],
                                    order_currency=order_desc[1],
                                    order_id=order_desc[2],
                                    payment_currency=order_desc[3])
        if resp['status'] == '0000':
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp['data']
        else:
            Bithumb.raise_wrong_status_exception(resp)

    def buy_market_order(self, order_currency, unit, payment_currency="KRW"):
        """
        시장가 매수
        :param order_currency   : BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN/TRX/ELF/MITH/MCO/OMG/KNC
        :param payment_currency : KRW
        :param unit             : 주문수량
        :return                 : 성공 orderID / 실패 메시지
        """
        unit = Bithumb._convert_unit(unit)
        resp = self.api.market_buy(order_currency=order_currency,
                                    payment_currency=payment_currency,
                                    units=unit)
        if resp['status'] == '0000':
            return resp
        else:
            Bithumb.raise_wrong_status_exception(resp)
        
    def sell_market_order(self, order_currency, unit, payment_currency="KRW"):
        """
        시장가 매도
        :param order_currency   : BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN/TRX/ELF/MITH/MCO/OMG/KNC
        :param payment_currency : KRW
        :param unit             : 주문수량
        :return                 : 성공 orderID / 실패 메시지
        """
        unit = Bithumb._convert_unit(unit)
        resp = self.api.market_sell(order_currency=order_currency,
                                    payment_currency=payment_currency,
                                    units=unit)
        if resp['status'] == '0000':
            return resp
        else:
            Bithumb.raise_wrong_status_exception(resp)