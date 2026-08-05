class PortfolioService:
    def summary(self, positions):
        return {'value': 0.0, 'performance': 0.0, 'beta': 1.0, 'diversification': 'LOW'}

service = PortfolioService()
