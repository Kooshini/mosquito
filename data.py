import MySQLdb
import itertools


class Data:

    def __init__(self):
        self.db = {'host': '127.0.0.1', 'name': 'crypto', 'user': 'root', 'pass': ''}

    def load_backtest_variants(self):
        data = []
        db = MySQLdb.connect(self.db['host'], self.db['user'], self.db['pass'],
                             self.db['name'])
        sql = "SELECT ticker as market_pair,sentiment, indicator_type, timeframe FROM `backtest_results` " \
              "GROUP BY sentiment, ticker, indicator_type, timeframe ORDER BY timeframe asc"

        try:
            c = db.cursor()
            c.execute(sql)
            for row in c.fetchall():
                data.append(row)
        except MySQLdb.OperationalError:
            print("Error loading alert data from the DB")
        finally:
            db.close()
            return data

    def load_backtest_epochs(self, market_pair, sentiment, timeframe, indicator_type, datetime):
        data = []
        db = MySQLdb.connect(self.db['host'], self.db['user'], self.db['pass'],
                             self.db['name'])
        sql = "SELECT UNIX_TIMESTAMP(alert_date) as timestamp FROM `alert_data` WHERE `market_pair` LIKE '%s' " \
              "AND `sentiment` LIKE '%s' AND `timeframe` LIKE '%s' AND `type` LIKE '%s' AND " \
              "`alert_date` BETWEEN DATE_SUB('%s', INTERVAL 120 MINUTE) AND " \
              "DATE_ADD('%s', INTERVAL 120 MINUTE) ORDER BY `target_date` DESC" \
              % (market_pair, sentiment, timeframe, indicator_type, datetime, datetime)
        try:
            c = db.cursor()
            c.execute(sql)
            data = list(itertools.chain.from_iterable(c.fetchall()))
        except MySQLdb.OperationalError:
                print("Error loading alert data from the DB")
        finally:
                db.close()
                epochs = {'market_pair': market_pair, 'sentiment': sentiment, 'timeframe': timeframe, 'epochs': data}
                return epochs
