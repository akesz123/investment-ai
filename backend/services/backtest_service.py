class BacktestService:
    def run(self, strategy=None):
        return {'cagr': 0.0, 'sharpe': 0.0, 'sortino': 0.0, 'max_drawdown': 0.0, 'win_rate': 0.0}

service = BacktestService()
