"""Basic test untuk memastikan semua modul bisa di-import"""
import sys

def test_imports():
    print("Testing imports...")

    try:
        import pandas as pd
        print("✓ pandas OK")
    except ImportError as e:
        print(f"✗ pandas FAILED: {e}")
        return False

    try:
        import numpy as np
        print("✓ numpy OK")
    except ImportError as e:
        print(f"✗ numpy FAILED: {e}")
        return False

    try:
        import ta
        print("✓ ta OK")
    except ImportError as e:
        print(f"✗ ta FAILED: {e}")
        return False

    try:
        import plotly
        print("✓ plotly OK")
    except ImportError as e:
        print(f"✗ plotly FAILED: {e}")
        return False

    try:
        import yfinance
        print("✓ yfinance OK")
    except ImportError as e:
        print(f"✗ yfinance FAILED: {e}")
        return False

    try:
        import streamlit
        print("✓ streamlit OK")
    except ImportError as e:
        print(f"✗ streamlit FAILED: {e}")
        return False

    try:
        from rich.console import Console
        print("✓ rich OK")
    except ImportError as e:
        print(f"✗ rich FAILED: {e}")
        return False

    try:
        import click
        print("✓ click OK")
    except ImportError as e:
        print(f"✗ click FAILED: {e}")
        return False

    return True

def test_modules():
    print("\nTesting custom modules...")

    try:
        from config import IDX_STOCKS, ALPHA_VANTAGE_API_KEY
        print(f"✓ config OK ({len(IDX_STOCKS)} stocks)")
    except Exception as e:
        print(f"✗ config FAILED: {e}")
        return False

    try:
        from data_fetcher import StockDataFetcher
        print("✓ data_fetcher OK")
    except Exception as e:
        print(f"✗ data_fetcher FAILED: {e}")
        return False

    try:
        from technical_analysis import TechnicalAnalyzer
        print("✓ technical_analysis OK")
    except Exception as e:
        print(f"✗ technical_analysis FAILED: {e}")
        return False

    try:
        from fundamental_analysis import FundamentalAnalyzer
        print("✓ fundamental_analysis OK")
    except Exception as e:
        print(f"✗ fundamental_analysis FAILED: {e}")
        return False

    return True

def main():
    print("=" * 50)
    print("  STOCK ANALYZER INDONESIA - BASIC TEST")
    print("=" * 50)
    print()

    imports_ok = test_imports()
    modules_ok = test_modules()

    print("\n" + "=" * 50)
    if imports_ok and modules_ok:
        print("  ✅ ALL TESTS PASSED!")
        print("\n  Ready to run:")
        print("  - CLI: python cli.py --help")
        print("  - Web: streamlit run app.py")
    else:
        print("  ❌ SOME TESTS FAILED")
        print("\n  Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    print("=" * 50)

    return 0 if (imports_ok and modules_ok) else 1

if __name__ == '__main__':
    sys.exit(main())
