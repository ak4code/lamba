import pandas as pd
import technic as ta


def get_ema_values(*, ohlc: pd.DataFrame, offset: int = -1) -> tuple[float, float]:
    """Получить текущее значение ema 50 и 200"""
    return (
        round(ta.tema(ohlc[4].astype('float'), 50).iloc[offset], 4),
        round(ta.tema(ohlc[4].astype('float'), 200).iloc[offset], 4),
    )


def get_rsi_value(*, ohlc: pd.DataFrame) -> float:
    """Получить текущее значение rsi"""
    return round(ta.trsi(ohlc[4].astype('float'), 14).iloc[-1], 4)
