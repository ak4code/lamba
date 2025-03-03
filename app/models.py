from pydantic import BaseModel, Field


class KlineResponse(BaseModel):
    """Модель ответа запроса свечей API Bybit"""

    class Result(BaseModel):
        """Модель результата ответа"""

        symbol: str
        category: str
        list: list

        @classmethod
        def from_dict(cls, data: dict):
            """Создаёт экземпляр Result из словаря"""
            return cls(
                symbol=data['symbol'],
                category=data['category'],
                list=data['list'],
            )

    code: int = Field(alias='retCode')
    message: str = Field(alias='retMsg')
    ext_info: dict = Field(alias='retExtInfo')
    result: Result


class Position(BaseModel):
    """Модель позиции"""

    side: str
    qty: str
    entry_price: float
    profit_price: float


class OrderPayload(BaseModel):
    """Модель тела ордера"""

    category: str = Field(default='linear')
    symbol: str
    side: str
    orderType: str = Field(default='Market')
    qty: str
