import os

from celery import shared_task

from app.utils.logger import get_logger

logger = get_logger(name=__name__)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def execute_strategy_task():
    """
    Асинхронная задача для выполнения стратегии.
    """
    try:
        import redis

        from app.strategies import trend_duration

        pool = redis.ConnectionPool.from_url(os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'))
        r_con = redis.Redis(connection_pool=pool)
        trend_duration.strategy(redis_client=r_con)
    except Exception as error:
        logger.error(f'Произошла ошибка: {error}')
        raise error
