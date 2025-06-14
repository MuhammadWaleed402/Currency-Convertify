💱 CurrencyConvertify

Overview
A fast and reliable real-time currency converter Project. It supports multiple APIs, offline fallback, conversion history, and trend analysis   all via a clean command-line interface.

🚀 Features
Real-time currency conversion (multi-API support)

Offline fallback with built-in rates

Conversion history & trend analysis

Supports 20+ major currencies

Fast caching (5-min refresh)

Lightweight and dependency-minimal

Simple CLI for easy interaction

⚙️ How It Works
Exchange Rate Sources

Primary: APIs (exchangerate-api, fixer.io, open.er-api.com)

Secondary: Libraries (forex-python, currency-converter)

Fallback: Built-in static rates

Caching

Rates cached for 5 mins

Persisted across sessions

Conversion Engine

Auto rate inversion

Handles all currency pairs

Precision configurable

History System

Saves past conversions with timestamps

Supports trend analysis & export

🛠️ Run Instructions

Requirements: Python 3.6+

(Optional: pip install forex-python currency-converter requests)

python "currency_converter.py"

Works with or without external libraries using fallback rates.
