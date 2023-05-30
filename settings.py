from alpaca.data.timeframe import TimeFrame

class SymbolType:
    Crypto = 0
    Stock = 1
    
class Settings:
    def __init__(self):
        self.timeframe = TimeFrame.Minute
        self.symbol_type = SymbolType.Stock 
        self.symbols = []
        self.past_days = 0
        
    def is_crypto(self):
        return self.symbol_type == SymbolType.Crypto