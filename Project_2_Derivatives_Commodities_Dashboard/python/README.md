# Derivatives & Commodities Dashboard — Python

A spot/forward commodities monitoring dashboard with a recombining trinomial lattice for European, American and Bermudan option exercise.

## Run

Install with `pip install -r requirements.txt`, run `streamlit run app.py`, test with `python -m pytest -q`. Sample synthetic forward data is in `data/forward_curve_example.csv`; upload any CSV with `contract,days_to_maturity,forward`.

The reported curve slope is an annualized front-to-back relative difference, **not an investable return or roll yield**. The pricing tree assumes a lognormal spot, constant volatility/rates, no dividends or convenience yield by default, and discrete exercise dates. A futures-option pricing interpretation requires an appropriate carry model.

**CV:** Built a Python trinomial lattice pricer (European/American/Bermudan) and commodities term-structure analytics for contango/backwardation.
