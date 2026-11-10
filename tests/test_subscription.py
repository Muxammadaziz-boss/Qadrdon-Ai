"""Obuna va kunlik limitlar testi."""

from datetime import date, timedelta
from db.models.subscription import Subscription


def test_subscription_daily_limit_reset():
    sub = Subscription(user_id=1, plan="free")
    sub.daily_messages_used = 50
    # Kechagi sana
    sub.last_reset_date = date.today() - timedelta(days=1)

    # Yangi kunda can_send_message chaqirilganda limit avtomatik 0 bo'lishi kerak
    assert sub.can_send_message is True
    assert sub.daily_messages_used == 0
    assert sub.last_reset_date == date.today()


def test_subscription_free_limit_enforced_same_day():
    sub = Subscription(user_id=1, plan="free")
    sub.daily_messages_used = 50
    sub.last_reset_date = date.today()

    # Shu kunda 50 ta ishlatilgan bo'lsa xabar yuborolmaydi
    assert sub.can_send_message is False


def test_subscription_premium_unlimited():
    sub = Subscription(user_id=1, plan="premium")
    sub.activate_plan("premium", days=30)
    sub.daily_messages_used = 1000
    assert sub.can_send_message is True

