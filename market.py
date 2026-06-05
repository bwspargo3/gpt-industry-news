import requests


def fetch_rates():
    return {
        "10Y": 4.2,
        "2Y": 4.6,
    }


def build_snapshot():
    return fetch_rates()
