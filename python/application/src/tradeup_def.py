import sys
import path
sys.path.insert(0, path.PATH_SHARE)

class Tradeup:
    def __init__(self):
        self.inputEntries: list[TradeupInputEntry] = list()
        self.outputEntries: list[TradeupOutputEntry] = list()
        self.favourite: bool = False
        self.dateFound: str = ""
        self.deviceUsed: str = ""
        self.tradeupCategory: int = 0
        self.tradeupGrade: int = 0
        self.averageInputFloat: float = 0.0
        self.totalInputCost: float = 0.0
        self.totalOutputs: float = 0
        self.chanceToProfit: float = 0.0
        self.profitability: float = 0.0
        self.chanceToProfitSteamTax: float = 0.0
        self.profitabilitySteamTax: float = 0.0
        self.tradeupHash: str = ""

class TradeupInputEntry:
    def __init__(self):
        self.permID: int = 0
        self.weaponName: str = ""
        self.skinName: str = ""
        self.price: float = 0.0
        self.category: int = 0
        self.grade: int = 0
        self.wear: int = 0
        self.floatVal: float = 0.0

class TradeupOutputEntry:
    def __init__(self):
        self.permID: int = 0
        self.weaponName: str = ""
        self.skinName: str = ""
        self.price: float = 0.0
        self.category: int = 0
        self.grade: int = 0
        self.wear: int = 0
        self.floatVal: float = 0.0
        self.outputAmount: int = 0
        self.tradeupChance: float = 0.0
        self.moneyGain: float = 0.0
        self.moneyGainSteamTax: float = 0.0