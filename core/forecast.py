import pandas as pd
from prophet import Prophet
import json
from django.contrib.auth.models import User
from .models import PersonalPrediction
from .models import Cryptocurrencies, LSTMModel, ProphetModel, NHitsModel
from prophet.serialize import model_from_json
import torch
from neuralforecast.tsdataset import TimeSeriesDataset
from datetime import datetime, timedelta


def forecast_prophet(dates, prices, n_days, Prediction_id=None, coin_id=None):
    # Create a DataFrame with the dates and prices
    df = pd.DataFrame({"ds": dates, "y": prices})
    prophetId = None

    # Create a Prophet model and fit it to the data
    if coin_id is not None:
        model_info = Cryptocurrencies.objects.get(id=coin_id).prophetId
        prophetId = model_info.id
        model_file_path = model_info.machineLearningModel.path
        with open(model_file_path, "r") as fin:
            model = model_from_json(fin.read())

    else:
        model = Prophet(
            changepoint_prior_scale=1.0,
            seasonality_prior_scale=0.01,
            holidays_prior_scale=0.01,
            seasonality_mode="multiplicative",
            daily_seasonality=False,
            weekly_seasonality=False,
            yearly_seasonality=False,
        )
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
    elif coin_id is not None:
        # Save predicted data to Cryptocurrencies.predictedData
        predicted_data = [
            {"Date": date, "Close": price}
            for date, price in zip(predicted_dates, predicted_prices)
        ]
        predicted_data_json = json.dumps(predicted_data)
        ProphetModel.objects.filter(id=prophetId).update(
            predictedData=predicted_data_json
        )
    else:
        # Return the predicted values and dates
        return predicted_dates, predicted_prices

    return predicted_dates, predicted_prices


from contextlib import contextmanager
import pathlib


@contextmanager
def set_posix_windows():
    posix_backup = pathlib.PosixPath
    try:
        pathlib.PosixPath = pathlib.WindowsPath
        yield
    finally:
        pathlib.PosixPath = posix_backup


def forecast_lstm(dates, prices, coinId):
    lstm_info = Cryptocurrencies.objects.get(id=coinId).lstmId
    lstmId = lstm_info.id
    lstmModel = LSTMModel.objects.get(id=lstmId)
    model_path = str(lstmModel.machineLearningModel.path)
    print(model_path)

    with set_posix_windows():
        model = torch.load(model_path)

    df = pd.DataFrame({"ds": dates, "y": prices})
    df["unique_id"] = 1.0
    df = df[["unique_id", "ds", "y"]]
    dataset, *_ = TimeSeriesDataset.from_df(df)
    predictedPrice = model.predict(dataset=dataset)

    current_date = datetime.now().date()
    start_date = current_date + timedelta(days=1)
    dates = pd.date_range(start=start_date, periods=len(predictedPrice), freq="D")
    df_predicted = pd.DataFrame({"Date": dates, "Close": predictedPrice.flatten()})
    df_predicted["Date"] = df_predicted["Date"].dt.strftime(
        "%Y-%m-%d"
    )  # Convert to string format
    predicted_data = df_predicted.to_dict(orient="records")
    LSTMModel.objects.filter(id=lstmId).update(predictedData=json.dumps(predicted_data))

    predicted_dates = [data["Date"] for data in predicted_data]
    predicted_prices = [data["Close"] for data in predicted_data]

    return predicted_dates, predicted_prices


def forecast_NHits(dates, prices, coinId):
    NHits_info = Cryptocurrencies.objects.get(id=coinId).lstmId
    NhitsId = NHits_info.id
    nHitsModel = NHitsModel.objects.get(id=NhitsId)
    model_path = str(nHitsModel.machineLearningModel.path)

    with set_posix_windows():
        model = torch.load(model_path)

    df = pd.DataFrame({"ds": dates, "y": prices})
    df["unique_id"] = 1.0
    df = df[["unique_id", "ds", "y"]]
    dataset, *_ = TimeSeriesDataset.from_df(df)
    predictedPrice = model.predict(dataset=dataset)

    current_date = datetime.now().date()
    start_date = current_date + timedelta(days=1)
    dates = pd.date_range(start=start_date, periods=len(predictedPrice), freq="D")
    df_predicted = pd.DataFrame({"Date": dates, "Close": predictedPrice.flatten()})
    df_predicted["Date"] = df_predicted["Date"].dt.strftime(
        "%Y-%m-%d"
    )  # Convert to string format
    predicted_data = df_predicted.to_dict(orient="records")
    NHitsModel.objects.filter(id=NhitsId).update(
        predictedData=json.dumps(predicted_data)
    )

    predicted_dates = [data["Date"] for data in predicted_data]
    predicted_prices = [data["Close"] for data in predicted_data]

    return predicted_dates, predicted_prices
