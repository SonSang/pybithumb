from pybithumb.core import *


class Bithumb:
    def __init__(self, conkey, seckey):
        self.api = PrivateApi(conkey, seckey)

    @staticmethod
    def get_tickers():
        resp = PublicApi.ticker("ALL")
        return resp['data'].keys()

    @staticmethod
    def get_market_detail(currency):
        """
        거래소 마지막 거래 정보 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : (24시간저가, 24시간고가, 24시간평균거래금액, 24시간거래량)
        """
        try:
            resp = None
            resp = PublicApi.ticker(currency)
            low = resp['data']['min_price']
            high = resp['data']['max_price']
            avg = resp['data']['average_price']
            volume = resp['data']['units_traded']
            return float(low), float(high), float(avg), float(volume)
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    @staticmethod
    def get_current_price(currency):
        """
        최종 체결 가격 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : price
        """
        try:
            resp = None
            resp = PublicApi.ticker(currency)

            if currency is not "ALL":
                return resp['data']['closing_price']
            else:
                return resp["data"]
            #resp = PublicApi.transaction_history(currency)
            #return resp['data'][0]['price']

        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    @staticmethod
    def get_orderbook(currency):
        """
        매수/매도 호가 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : 매수/매도 호가
        """
        try:
            resp = None
            resp = PublicApi.orderbook(currency)
            return resp['data']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_trading_fee(self):
        """
        거래 수수료 조회
        :return: 수수료
        """
        try:
            resp = None
            resp = self.api.account()
            return float(resp['data']['trade_fee'])
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_balance(self, currency):
        """
        거래소 회원의 잔고 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : (보유코인, 사용중코인, 보유원화, 사용중원화)
        """
        try:
            resp = None
            resp = self.api.balance(currency=currency)
            specifier = currency.lower()
            return (float(resp['data']["total_" + specifier]), float(resp['data']["in_use_" + specifier]),
                    float(resp['data']["total_krw"]), float(resp['data']["in_use_krw"]))
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def buy_limit_order(self, currency, price, unit):
        """
        매수 주문
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param price   : 주문 가격
        :param unit    : 주문 수량
        :return        : (주문Type, currency, 주문ID)
        """
        try:
            unit = "{0:.4f}".format(unit)
            resp = None
            resp = self.api.place(type="bid", price=price, units=unit, order_currency=currency)
            return "bid", currency, resp['order_id']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def sell_limit_order(self, currency, price, unit):
        """
        매도 주문
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param price   : 주문 가격
        :param unit    : 주문 수량
        :return        : (주문Type, currency, 주문ID)
        """
        try:
            resp = None
            unit = "{0:.4f}".format(unit)
            resp = self.api.place(type="ask", price=price, units=unit, order_currency=currency)
            return "ask", currency, resp['order_id']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_outstanding_order(self, order_desc):
        """
        거래 미체결 수량 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래 미체결 수량
        """
        try:
            resp = None
            resp = self.api.orders(type=order_desc[0], currency=order_desc[1], order_id=order_desc[2])
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            if resp['status'] == '5600':
                return 0
            return resp['data'][0]['units_remaining']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def get_order_completed(self, order_desc):
        """
        거래 완료 정보 조회
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 거래정보
        """
        try:
            resp = None
            resp = self.api.order_detail(type=order_desc[0], currency=order_desc[1], order_id=order_desc[2])
            # HACK : 빗썸이 데이터를 리스트에 넣어줌
            return resp['data'][0]
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def cancel_order(self, order_desc):
        """
        매수/매도 주문 취소
        :param order_desc: (주문Type, currency, 주문ID)
        :return          : 성공: True / 실패: False
        """
        try:
            resp = None
            resp = self.api.cancel(type=order_desc[0], currency=order_desc[1], order_id=order_desc[2])
            return resp['status'] == '0000'
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def buy_market_order(self, currency, unit):
        """
        시장가 매수
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param unit    : 주문수량
        :return        : 성공 orderID / 실패 메시지
        """
        try:
            resp = None
            resp = self.api.market_buy(currency=currency, units=unit)
            return resp['order_id']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

    def sell_market_order(self, currency, unit):
        """
        시장가 매도
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :param unit    : 주문수량
        :return        : 성공 orderID / 실패 메시지
        """
        try:
            resp = None
            resp = self.api.market_sell(currency=currency, units=unit)
            return resp['order_id']
        except Exception as x:
            print(x.__class__.__name__, resp)
            return None

if __name__ == "__main__":
    print(Bithumb.get_current_price("BTC"))
    print(Bithumb.get_current_price("ALL"))