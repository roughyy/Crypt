import pandas as pd
from prophet import Prophet
import json
from django.contrib.auth.models import User
from .models import PersonalPrediction
from .models import Cryptocurrencies


def forecast_prophet(dates, prices, n_days, Prediction_id=None):
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
    predicted_dates = [date.strftime("%Y-%m-%d") for date in predicted_dates]
    predicted_prices = [round(price, 7) for price in predicted_prices]

    if Prediction_id is not None:
        # Save predicted data to PersonalPrediction.predictedData
        predicted_data = [
            {"Date": date, "Close": price}
            for date, price in zip(predicted_dates, predicted_prices)
        ]
        predicted_data_json = json.dumps(predicted_data)
        PersonalPrediction.objects.filter(id=Prediction_id).update(
            predictedData=predicted_data_json
        )
    else:
        # Return the predicted values and dates
        return predicted_dates, predicted_prices

    return predicted_dates, predicted_prices


def forecast_lstm(dates, prices, n_days, coinId):
    predicted_dates = [1, 2, 3]
    predicted_prices = [3, 4, 5]
    return predicted_dates, predicted_prices
