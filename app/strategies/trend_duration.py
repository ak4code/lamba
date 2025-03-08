import pandas as pd
from pybit.unified_trading import HTTP
from redis import Redis

from app.config import settings
from app.models import KlineResponse, OrderPayload, Position
from app.utils.indicators import get_ema_values, get_rsi_value
from app.utils.logger import get_logger

logger = get_logger(name=__name__)

session = HTTP(
    testnet=False,
    api_key=settings.api_key,
    api_secret=settings.api_secret,
)
TREND_DURATION_KEY = f'trend_duration:{settings.symbol}'
WATCH_KEY = f'watch:{settings.symbol}'
POSITIONS_KEY = f'positions:{settings.symbol}'
BUY = 'Buy'
SELL = 'Sell'
BULL = 'bull'
BEAR = 'bear'


def get_profit_price(*, side: str, price: float) -> float:
    """Получить тейк профит цену"""
    if side == SELL:
        return price * (1 - (settings.profit_percent / 100))
    return price * (1 + (settings.profit_percent / 100))


def get_trailing_price(*, side: str, entry_price: float) -> float:
    """Получить тейк профит цену"""
    if side == SELL:
        return entry_price * (1 + (settings.trailing / 100))
    return entry_price * (1 - (settings.trailing / 100))


def entry_position(*, price: float, side: str, position: Position | None = None, redis_client: Redis):
    """Вход в позиции"""
    qty = str(round(settings.bid / price, 1))
    pyramiding = redis_client.llen(POSITIONS_KEY)
    if position is None:
        logger.info(f'Новая {side}: {settings.symbol} x {qty} по {price}$')
        place_order(OrderPayload(symbol=settings.symbol, side=side, qty=str(qty)))
        profit_price = get_profit_price(side=side, price=price)
        redis_client.rpush(
            POSITIONS_KEY,
            Position(side=side, qty=qty, entry_price=price, profit_price=profit_price).model_dump_json(),
        )
        return

    if (
        side == SELL
        and pyramiding < 3
        and position.side == side
        and price > get_trailing_price(side=side, entry_price=position.entry_price)
    ):
        logger.info(f'Усреднение {side}: {settings.symbol} x {qty} по {price}$')
        place_order(OrderPayload(symbol=settings.symbol, side=side, qty=str(qty)))
        profit_price = get_profit_price(side=side, price=price)
        redis_client.rpush(
            POSITIONS_KEY,
            position.model_dump_json(),
        )
        redis_client.rpush(
            POSITIONS_KEY,
            Position(side=side, qty=qty, entry_price=price, profit_price=profit_price).model_dump_json(),
        )
        return

    if (
        side == BUY
        and pyramiding < 3
        and position.side == side
        and price < get_trailing_price(side=side, entry_price=position.entry_price)
    ):
        logger.info(f'Усреднение {side}: {settings.symbol} x {qty} по {price}$')
        place_order(OrderPayload(symbol=settings.symbol, side=side, qty=str(qty)))
        profit_price = get_profit_price(side=side, price=price)
        redis_client.rpush(
            POSITIONS_KEY,
            position.model_dump_json(),
        )
        redis_client.rpush(
            POSITIONS_KEY,
            Position(side=side, qty=qty, entry_price=price, profit_price=profit_price).model_dump_json(),
        )
        return


def exit_position(price: float, position: Position | None) -> Position | None:
    """Выход из позиции"""
    if position and position.side == BUY and price > float(position.profit_price):
        return place_order(OrderPayload(symbol=settings.symbol, side=SELL, qty=str(position.qty)))
    if position and position.side == SELL and price < float(position.profit_price):
        return place_order(OrderPayload(symbol=settings.symbol, side=BUY, qty=str(position.qty)))
    return position


def place_order(payload: OrderPayload) -> None:
    """Разместить ордер"""
    try:
        order = session.place_order(**payload.model_dump())
        logger.info(f'Ордер успешно отправлен: {order=}')
        return
    except Exception as error:
        logger.error(f'Ошибка при отправке ордера: {error}')
        return


def strategy(*, redis_client: Redis):
    """Стратегия"""
    try:
        logger.warning(f'Запрос данных рынка по {settings.symbol} API Bybit.')
        response = session.get_kline(
            category=settings.category,
            symbol=settings.symbol,
            interval=settings.interval,
            limit=500,
        )
    except Exception as error:
        logger.error(f'Ошибка при запросе данных рынка: {error}')
        return
    klines = KlineResponse.model_validate(response)

    ohlc = pd.DataFrame(klines.result.list)
    ohlc = ohlc[::-1].reset_index(drop=True)

    close = float(ohlc[4].iloc[-1])
    logger.info(f'Цена закрытия: {close}')

    ema50, ema200 = get_ema_values(ohlc=ohlc)
    logger.info(f'Текущие показатели индикаторов: [EMA50: {ema50}, EMA200: {ema200}]')

    ema50_prev, ema200_prev = get_ema_values(ohlc=ohlc, offset=-2)
    logger.info(f'Предыддущие показатели индикаторов: [EMA50: {ema50}, EMA200: {ema200}]')

    rsi = get_rsi_value(ohlc=ohlc)
    logger.info(f'Показатели индикатора: [RSI: {rsi}]')

    trend_duration = redis_client.get(TREND_DURATION_KEY)
    if trend_duration is None:
        logger.warning('Счетчик не установлен. Обнуляем счетчик!')
        trend_duration = 0
        redis_client.set(TREND_DURATION_KEY, trend_duration)

    trend = BULL if ema50 > ema200 else BEAR
    trend_prev = BULL if ema50_prev > ema200_prev else BEAR

    is_change_trend = trend_prev != trend
    if is_change_trend:
        logger.error(f'Тренд изменился: {trend_prev} > {trend}. Обнуляем счетчик!')
        trend_duration = 0
        redis_client.set(TREND_DURATION_KEY, trend_duration)

    trend_duration = redis_client.incr(TREND_DURATION_KEY)
    logger.info(f'Текущее значение счетчика: {trend_duration}, тренд: {trend}')

    watch = redis_client.get(WATCH_KEY)
    if isinstance(watch, bytes):
        watch = watch.decode('utf-8')

    if trend == BULL and trend_duration % settings.duration_threshold == 0:
        logger.info('Включаем наблюдение для точки входа в SHORT')
        watch = SELL
        redis_client.set(WATCH_KEY, watch)

    if trend == BEAR and trend_duration % settings.duration_threshold == 0:
        logger.info('Включаем наблюдение для точки входа в LONG')
        watch = BUY
        redis_client.set(WATCH_KEY, watch)

    if watch == BUY and trend == BULL or watch == SELL and trend == BEAR:
        redis_client.delete(WATCH_KEY)
        return

    position = redis_client.rpop(POSITIONS_KEY)
    if position:
        position = Position.model_validate_json(position)

    if watch == SELL and rsi > 70 or watch == BUY and rsi < 30:
        entry_position(price=close, side=watch, position=position, redis_client=redis_client)
        return

    position = exit_position(price=close, position=position)
    if position:
        redis_client.rpush(POSITIONS_KEY, position.model_dump_json())
