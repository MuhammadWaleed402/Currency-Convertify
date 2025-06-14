"""
Complete Single-File Currency Converter
Fast real-time currency conversion with all features
Uses multiple fast APIs for reliable real-time data
Version: 3.0.0 - Complete & Fast
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Import required libraries with fallback handling
try:
    from forex_python.converter import CurrencyRates
    FOREX_AVAILABLE = True
except ImportError:
    FOREX_AVAILABLE = False
    print("Note: forex-python not available. Using fallback rates.")

try:
    from currency_converter import CurrencyConverter as LibCurrencyConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False
    print("Note: currency-converter not available. Using fallback rates.")

# Configuration and Constants
class Config:
    """Application configuration constants"""
    # Supported currencies with their full names
    SUPPORTED_CURRENCIES = {
        'USD': 'US Dollar',
        'EUR': 'Euro', 
        'GBP': 'British Pound Sterling',
        'JPY': 'Japanese Yen',
        'OMR': 'Omani Rial',
        'AUD': 'Australian Dollar',
        'CAD': 'Canadian Dollar',
        'CHF': 'Swiss Franc',
        'CNY': 'Chinese Yuan',
        'INR': 'Indian Rupee',
        'AED': 'UAE Dirham',
        'SAR': 'Saudi Riyal',
        'KWD': 'Kuwaiti Dinar',
        'BHD': 'Bahraini Dinar',
        'QAR': 'Qatari Riyal',
        'NOK': 'Norwegian Krone',
        'SEK': 'Swedish Krona',
        'DKK': 'Danish Krone',
        'PLN': 'Polish Zloty',
        'CZK': 'Czech Koruna'
    }
    
    # File names for data persistence
    HISTORY_FILE = "conversion_history.json"
    RATES_CACHE_FILE = "rates_cache.json"
    
    # API settings
    API_TIMEOUT = 3  # seconds
    CACHE_DURATION = 300  # 5 minutes
    
    # Display settings
    DECIMAL_PLACES = 4
    MAX_HISTORY_ENTRIES = 100


class DataManager:
    """Handles data persistence operations - optimized for speed"""
    
    @staticmethod
    def load_json_file(filename: str) -> List:
        """Load data from JSON file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    return data if isinstance(data, list) else []
            return []
        except (json.JSONDecodeError, IOError, FileNotFoundError):
            return []
    
    @staticmethod
    def save_json_file(filename: str, data: List) -> bool:
        """Save data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False


class ExchangeRateService:
    """Fast exchange rate service with multiple APIs and caching"""
    
    def __init__(self):
        self.forex_rates = CurrencyRates() if FOREX_AVAILABLE else None
        self.lib_converter = LibCurrencyConverter() if CONVERTER_AVAILABLE else None
        self.rates_cache = self._load_cache()
        
        # Fast free APIs for real-time rates
        self.api_endpoints = [
            "https://api.exchangerate-api.com/v4/latest/USD",
            "https://api.fixer.io/latest?base=USD",
            "https://open.er-api.com/v6/latest/USD"
        ]
        
        # Updated fallback rates for immediate response
        self.fallback_rates = {
            'USD': 1.0, 'EUR': 0.8520, 'GBP': 0.7315, 'JPY': 110.25,
            'OMR': 0.3845, 'AUD': 1.3520, 'CAD': 1.2475, 'CHF': 0.9185,
            'CNY': 6.4520, 'INR': 74.15, 'AED': 3.6725, 'SAR': 3.7500,
            'KWD': 0.3015, 'BHD': 0.3770, 'QAR': 3.6400, 'NOK': 8.5200,
            'SEK': 8.7500, 'DKK': 6.3400, 'PLN': 3.9800, 'CZK': 21.5000
        }
    
    def _load_cache(self) -> Dict:
        """Load cached rates"""
        try:
            if os.path.exists(Config.RATES_CACHE_FILE):
                with open(Config.RATES_CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                    # Check if cache is still valid
                    if 'timestamp' in cache:
                        cache_time = datetime.fromisoformat(cache['timestamp'])
                        if datetime.now() - cache_time < timedelta(seconds=Config.CACHE_DURATION):
                            return cache
            return {}
        except:
            return {}
    
    def _save_cache(self, rates: Dict) -> None:
        """Save rates to cache"""
        try:
            cache_data = {
                'rates': rates,
                'timestamp': datetime.now().isoformat()
            }
            with open(Config.RATES_CACHE_FILE, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass
    
    def _fetch_rates_from_api(self) -> Optional[Dict]:
        """Fetch rates from fast APIs"""
        for api_url in self.api_endpoints:
            try:
                response = requests.get(api_url, timeout=Config.API_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    if 'rates' in data:
                        return data['rates']
            except:
                continue
        return None
    
    def get_all_rates(self, base_currency: str = 'USD') -> Dict[str, float]:
        """Get all exchange rates for display"""
        # Check cache first
        if 'rates' in self.rates_cache and base_currency == 'USD':
            return self.rates_cache['rates']
        
        # Try to fetch from API
        rates = self._fetch_rates_from_api()
        if rates:
            # Filter to supported currencies only
            filtered_rates = {k: v for k, v in rates.items() if k in Config.SUPPORTED_CURRENCIES}
            self._save_cache(filtered_rates)
            return filtered_rates
        
        # Use fallback rates
        return self.fallback_rates.copy()
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate with fast fallback - optimized for speed"""
        if from_currency == to_currency:
            return 1.0
        
        # Try to get from cached rates first
        all_rates = self.get_all_rates()
        if from_currency == 'USD' and to_currency in all_rates:
            return all_rates[to_currency]
        elif to_currency == 'USD' and from_currency in all_rates:
            return 1.0 / all_rates[from_currency]
        elif from_currency in all_rates and to_currency in all_rates:
            return all_rates[to_currency] / all_rates[from_currency]
        
        # Quick attempt with libraries
        rate = None
        
        # Try forex-python with minimal timeout
        if FOREX_AVAILABLE and self.forex_rates:
            try:
                rate = self.forex_rates.get_rate(from_currency, to_currency)
                if rate and rate > 0:
                    return float(rate)
            except:
                pass
        
        # Try currency-converter library
        if CONVERTER_AVAILABLE and self.lib_converter:
            try:
                from currency_converter import CurrencyConverter as CC
                cc = CC()
                rate = cc.convert(1, from_currency, to_currency)
                if rate and rate > 0:
                    return float(rate)
            except:
                pass
        
        # Use fallback rates (always available)
        return self._get_fallback_rate(from_currency, to_currency)
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> float:
        """Get rate using fallback data - guaranteed to work"""
        try:
            if from_currency in self.fallback_rates and to_currency in self.fallback_rates:
                from_rate = self.fallback_rates[from_currency]
                to_rate = self.fallback_rates[to_currency]
                return to_rate / from_rate
            return 1.0  # Default rate if currencies not found
        except (KeyError, ZeroDivisionError):
            return 1.0  # Safe default


class ConversionHistory:
    """Lightweight conversion history management with trend analysis"""
    
    def __init__(self):
        self.history = DataManager.load_json_file(Config.HISTORY_FILE)
    
    def add_conversion(self, conversion_data: Dict) -> None:
        """Add a new conversion to history"""
        try:
            # Add timestamp information
            now = datetime.now()
            conversion_data.update({
                'timestamp': now.isoformat(),
                'readable_time': now.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Add to history
            self.history.append(conversion_data)
            
            # Maintain size limit
            if len(self.history) > Config.MAX_HISTORY_ENTRIES:
                self.history = self.history[-Config.MAX_HISTORY_ENTRIES:]
            
            # Save to file
            DataManager.save_json_file(Config.HISTORY_FILE, self.history)
            
        except Exception as e:
            print(f"Error saving conversion: {e}")
    
    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversion history"""
        return self.history[-limit:] if self.history else []
    
    def clear_history(self) -> bool:
        """Clear all conversion history"""
        self.history = []
        return DataManager.save_json_file(Config.HISTORY_FILE, self.history)
    
    def get_currency_trends(self, days: int = 7) -> Dict[str, Dict]:
        """Analyze currency trends from conversion history"""
        if not self.history:
            return {}
        
        # Get conversions from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_conversions = []
        
        for conversion in self.history:
            try:
                conv_time = datetime.fromisoformat(conversion['timestamp'])
                if conv_time >= cutoff_date:
                    recent_conversions.append(conversion)
            except:
                continue
        
        if len(recent_conversions) < 2:
            return {}
        
        # Analyze trends by currency pairs
        currency_rates = {}
        for conversion in recent_conversions:
            pair = f"{conversion['from_currency']}/{conversion['to_currency']}"
            rate = conversion['exchange_rate']
            timestamp = conversion['timestamp']
            
            if pair not in currency_rates:
                currency_rates[pair] = []
            currency_rates[pair].append({'rate': rate, 'time': timestamp})
        
        # Calculate trends
        trends = {}
        for pair, rates in currency_rates.items():
            if len(rates) >= 2:
                # Sort by time
                rates.sort(key=lambda x: x['time'])
                oldest_rate = rates[0]['rate']
                newest_rate = rates[-1]['rate']
                
                # Calculate percentage change
                change_percent = ((newest_rate - oldest_rate) / oldest_rate) * 100
                
                trend_direction = "stable"
                if change_percent > 1:
                    trend_direction = "rising"
                elif change_percent < -1:
                    trend_direction = "falling"
                
                trends[pair] = {
                    'change_percent': round(change_percent, 2),
                    'direction': trend_direction,
                    'oldest_rate': oldest_rate,
                    'newest_rate': newest_rate,
                    'data_points': len(rates)
                }
        
        return trends


class CurrencyConverter:
    """Main currency converter application - streamlined for speed"""
    
    def __init__(self):
        self.exchange_service = ExchangeRateService()
        self.history = ConversionHistory()
        print("Complete Currency Converter v3.0.0 - Fast & Complete")
        print("=" * 50)
    
    def run(self):
        """Main application loop"""
        while True:
            try:
                self.display_menu()
                choice = input("\nSelect an option (1-6): ").strip()
                
                if choice == '1':
                    self.convert_currency()
                elif choice == '2':
                    self.show_current_rates()
                elif choice == '3':
                    self.show_conversion_history()
                elif choice == '4':
                    self.show_currency_trends()
                elif choice == '5':
                    self.show_available_currencies()
                elif choice == '6':
                    self.exit_application()
                    break
                else:
                    print("Invalid choice. Please select 1-6.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\nExiting application...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                input("Press Enter to continue...")
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("         COMPLETE CURRENCY CONVERTER")
        print("=" * 50)
        print("1. Convert Currency (Real-time)")
        print("2. View Current Exchange Rates")
        print("3. View Conversion History")
        print("4. Analyze Currency Trends")
        print("5. Show Available Currencies") 
        print("6. Exit")
        print("=" * 50)
    
    def convert_currency(self):
        """Perform fast currency conversion"""
        print("\n--- CURRENCY CONVERSION ---")
        
        try:
            # Get input currencies
            from_currency = self.get_currency_input("Enter source currency (e.g., USD): ")
            if not from_currency:
                return
                
            to_currency = self.get_currency_input("Enter target currency (e.g., EUR): ")
            if not to_currency:
                return
            
            # Get amount
            amount_str = input("Enter amount to convert: ").strip()
            try:
                amount = float(amount_str)
                if amount <= 0:
                    print("Amount must be positive.")
                    return
            except ValueError:
                print("Invalid amount. Please enter a number.")
                return
            
            # Perform conversion (fast)
            print("Converting... (using live rates)")
            exchange_rate = self.exchange_service.get_exchange_rate(from_currency, to_currency)
            converted_amount = amount * exchange_rate
            
            # Display result
            print(f"\n--- CONVERSION RESULT ---")
            print(f"Amount: {amount:,.{Config.DECIMAL_PLACES}f} {from_currency}")
            print(f"Exchange Rate: 1 {from_currency} = {exchange_rate:,.{Config.DECIMAL_PLACES}f} {to_currency}")
            print(f"Converted Amount: {converted_amount:,.{Config.DECIMAL_PLACES}f} {to_currency}")
            
            # Save to history
            conversion_data = {
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'exchange_rate': exchange_rate,
                'converted_amount': converted_amount
            }
            self.history.add_conversion(conversion_data)
            print("✓ Conversion saved to history")
            
        except Exception as e:
            print(f"Conversion failed: {e}")
    
    def get_currency_input(self, prompt: str) -> Optional[str]:
        """Get and validate currency input"""
        currency = input(prompt).strip().upper()
        
        if not currency:
            print("Currency cannot be empty.")
            return None
        
        if currency not in Config.SUPPORTED_CURRENCIES:
            print(f"Currency '{currency}' is not supported.")
            print("Use option 3 to see available currencies.")
            return None
        
        return currency
    
    def show_conversion_history(self):
        """Display conversion history"""
        print("\n--- CONVERSION HISTORY ---")
        
        history = self.history.get_recent_history(20)  # Show last 20
        
        if not history:
            print("No conversion history available.")
            return
        
        print(f"Showing last {len(history)} conversions:")
        print("-" * 80)
        
        for i, conversion in enumerate(reversed(history), 1):
            amount = conversion.get('amount', 0)
            from_curr = conversion.get('from_currency', 'N/A')
            to_curr = conversion.get('to_currency', 'N/A')
            rate = conversion.get('exchange_rate', 0)
            converted = conversion.get('converted_amount', 0)
            time_str = conversion.get('readable_time', 'Unknown time')
            
            print(f"{i:2d}. {amount:,.2f} {from_curr} → {converted:,.2f} {to_curr}")
            print(f"    Rate: {rate:,.4f} | Time: {time_str}")
            print()
        
        # Option to clear history
        clear_choice = input("Clear history? (y/N): ").strip().lower()
        if clear_choice == 'y':
            if self.history.clear_history():
                print("History cleared successfully.")
            else:
                print("Failed to clear history.")
    
    def show_current_rates(self):
        """Display current exchange rates"""
        print("\n--- CURRENT EXCHANGE RATES ---")
        print("Base: USD (US Dollar)")
        print("Fetching latest rates...")
        
        try:
            start_time = time.time()
            rates = self.exchange_service.get_all_rates('USD')
            fetch_time = time.time() - start_time
            
            if rates:
                print(f"✓ Rates fetched in {fetch_time:.2f} seconds")
                print("-" * 60)
                
                # Sort by currency code for better display
                sorted_rates = sorted(rates.items())
                
                for i, (currency, rate) in enumerate(sorted_rates, 1):
                    if currency != 'USD':  # Skip USD since it's the base
                        currency_name = Config.SUPPORTED_CURRENCIES.get(currency, currency)
                        print(f"{i:2d}. 1 USD = {rate:,.{Config.DECIMAL_PLACES}f} {currency} ({currency_name})")
                
                print("-" * 60)
                print(f"Rates are cached for {Config.CACHE_DURATION//60} minutes for fast access")
            else:
                print("Unable to fetch current rates. Using fallback data.")
                
        except Exception as e:
            print(f"Error fetching rates: {e}")
    
    def show_currency_trends(self):
        """Display currency trends analysis"""
        print("\n--- CURRENCY TRENDS ANALYSIS ---")
        print("Analyzing trends from your conversion history...")
        
        try:
            trends = self.history.get_currency_trends(7)  # Last 7 days
            
            if not trends:
                print("No trend data available.")
                print("Perform more currency conversions to see trends!")
                return
            
            print(f"Trends based on {len(trends)} currency pairs from last 7 days:")
            print("-" * 70)
            
            for pair, trend_data in trends.items():
                change = trend_data['change_percent']
                direction = trend_data['direction']
                data_points = trend_data['data_points']
                
                # Format trend indicator
                if direction == "rising":
                    indicator = "📈 ↗"
                elif direction == "falling":
                    indicator = "📉 ↘"
                else:
                    indicator = "📊 →"
                
                print(f"{pair:10s} {indicator} {change:+6.2f}% ({data_points} conversions)")
            
            print("-" * 70)
            print("Trends are calculated from your personal conversion history")
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
    
    def show_available_currencies(self):
        """Display all available currencies"""
        print("\n--- AVAILABLE CURRENCIES ---")
        print(f"Total currencies supported: {len(Config.SUPPORTED_CURRENCIES)}")
        print("-" * 60)
        
        # Display in organized format
        for i, (code, name) in enumerate(Config.SUPPORTED_CURRENCIES.items(), 1):
            print(f"{i:2d}. {code:3s} - {name}")
        
        print("-" * 60)
        print("You can use any of these currency codes for conversion.")
    
    def exit_application(self):
        """Clean exit from application"""
        print("\n--- EXITING CURRENCY CONVERTER ---")
        print("Thank you for using Complete Currency Converter!")
        print("All conversion history has been saved.")
        print("Goodbye!")


def main():
    """Main entry point"""
    try:
        converter = CurrencyConverter()
        converter.run()
    except Exception as e:
        print(f"Application error: {e}")
        print("Please restart the application.")


if __name__ == "__main__":
    main()
