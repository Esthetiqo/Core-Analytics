import time
from datetime import datetime, timedelta
from decimal import Decimal

import requests
from peewee import fn

from app.models import (
    BinanceIncome,
)
from config.settings import Context, HedgerContext
from services.config_service import load_config

# Cache dictionary to store the symbol, funding rate, and last update time
cache = {}


def real_time_funding_rate(symbol: str) -> Decimal:
    current_time = time.time()

    if symbol in cache and current_time - cache[symbol]["last_update"] < 600:
        return cache[symbol]["funding_rate"]

    url = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
    response = requests.get(url)
    funding_rate = Decimal(0)

    if response.status_code == 200:
        data = response.json()
        funding_rate = Decimal(data["lastFundingRate"])
        cache[symbol] = {"funding_rate": funding_rate, "last_update": current_time}
    else:
        print("An error occurred:", response.status_code)

    return funding_rate


def fetch_binance_income_histories_of_type(
    context: Context,
    hedger_context: HedgerContext,
    income_type,
    limit_days=7,
    asset_field="asset",
):
    # Get the latest timestamp from the database for the respective model
    latest_record = (
        BinanceIncome.select()
        .where(
            BinanceIncome.tenant == context.tenant, BinanceIncome.type == income_type
        )
        .order_by(BinanceIncome.timestamp.desc())
        .first()
    )

    # If there's a record in the database, use its timestamp as the starting point
    if latest_record:
        start_time = latest_record.timestamp + timedelta(minutes=1)
    else:
        start_time = load_config(context).deployTimestamp

    end_time = start_time + timedelta(days=limit_days)
    current_time = datetime.utcnow()

    while start_time < current_time:
        print(
            f"{context.tenant}: Fetching binance {income_type} income histories between {start_time} and {end_time}"
        )
        time.sleep(5)
        data = hedger_context.utils.binance_client.futures_income_history(
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000),
            limit=1000,
            incomeType=income_type,
        )
        if not data:
            start_time = end_time
            end_time = start_time + timedelta(days=limit_days)
            continue

        for item in data:
            BinanceIncome.create(
                tenant=context.tenant,
                asset=item[asset_field],
                amount=item["income"],
                type=item["incomeType"],
                hedger=hedger_context.name,
                timestamp=datetime.fromtimestamp(
                    item["time"] / 1000
                ),  # Convert from milliseconds
            )
        if len(data) == 1000:
            start_time = datetime.fromtimestamp(data[-1]["time"] / 1000)
        else:
            start_time = end_time
        end_time = start_time + timedelta(days=limit_days)


def fetch_binance_income_histories(context, hedger_context):
    fetch_binance_income_histories_of_type(
        context,
        hedger_context,
        "FUNDING_FEE",
    )
    fetch_binance_income_histories_of_type(
        context,
        hedger_context,
        "TRANSFER",
    )
    fetch_binance_income_histories_of_type(
        context,
        hedger_context,
        "INTERNAL_TRANSFER",
    )
