import pandas as pd
from prophet import Prophet


def make_forecast(dates, prices, n_days):
    # Create a DataFrame with the dates and prices
    df = pd.DataFrame({"ds": dates, "y": prices})

    # Create a Prophet model and fit it to the data
    model = Prophet()
    model.fit(df)

    # Generate future dates to predict
    future = model.make_future_dataframe(periods=n_days)

    # Make the prediction
    forecast = model.predict(future)

    # Extract the predicted values and dates
    predicted_dates = forecast["ds"][-n_days:]
    predicted_prices = forecast["yhat"][-n_days:]

    # Return the predicted values and dates
    return predicted_dates, predicted_prices
