import configargparse
import datetime
from .base import Base
import core.common as common
from .enums import TradeState
from core.bots.enums import BuySellMode
from core.tradeaction import TradeAction
from lib.indicators.stoploss import StopLoss
from data import Data
from datetime import datetime
import pytz


class Tcg(Base):
    """
    Tcg strategy
    About: Buy when close_price > ema20, sell when close_price < ema20 and below death_cross
    """
    arg_parser = configargparse.get_argument_parser()

    def __init__(self):
        args = self.arg_parser.parse_known_args()[0]
        super(Tcg, self).__init__()
        self.name = 'tcg'
        self.min_history_ticks = 30
        self.pair = self.parse_pairs(args.pairs)[0]
        self.buy_sell_mode = BuySellMode.all
        self.stop_loss = StopLoss(int(args.ticker_size))
        self.data = Data()

    def calculate(self, look_back, wallet, tickr):
        """
        Main strategy logic (the meat of the strategy)
        """
        (dataset_cnt, _) = common.get_dataset_count(look_back, self.group_by_field)

        # Wait until we have enough data
        if dataset_cnt < self.min_history_ticks:
            print('dataset_cnt:', dataset_cnt)
            return self.actions

        self.actions.clear()
        new_action = TradeState.none

        # Calculate indicators
        df = look_back.tail(self.min_history_ticks)
        close = df['close'].values

        df1 = df['id'].tail(n=1)

        val = df1.iloc[0]
        val = val.split('-')
        loop_time = int(val[2])

        market_pair = 'BTCUSD'
        sentiment = 'Bear'
        timeframe = '4h'
        indicator_type = 'Bear TCG Cross'
        loop_datetime = datetime.fromtimestamp(loop_time, tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

        alerts = self.data.load_backtest_epochs(market_pair, sentiment, timeframe, indicator_type, loop_datetime)

        for alert_time in alerts['epochs']:
            if alert_time in range(loop_time-1800, loop_time):
                print("+!+!+!+!+!++!+!+!+!++!+!++!+! ALERT HIT +!+!+!+!++!+!+! {} {} {} ".
                      format(alert_time, loop_time-1800, loop_time))
                print(datetime.fromtimestamp(alert_time).strftime('%c'))
                print(datetime.fromtimestamp(loop_time-1800).strftime('%c'))
                print(datetime.fromtimestamp(loop_time).strftime('%c'))

                new_action = TradeState.sell

        trade_price = self.get_price(new_action, df.tail(), self.pair)
        # print("trade price {}".format(trade_price)

        # Get stop-loss
        if new_action == TradeState.sell and self.stop_loss.calculate(close):
            print('-------- stop-loss detected,..buying!!!!!!!!!!!!!!!!!!!!!!!! ')
            new_action = TradeState.buy

        action = TradeAction(self.pair,
                             new_action,
                             amount=None,
                             rate=trade_price,
                             buy_sell_mode=self.buy_sell_mode)

        self.actions.append(action)
        return self.actions


