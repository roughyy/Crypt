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


def forecast_lstm(dates, prices, coinId):
    lstm_info = Cryptocurrencies.objects.get(id=coinId).lstmId
    lstmId = lstm_info.id
    lstmModel = LSTMModel.objects.get(id=lstmId)
    model_path = str(lstmModel.machineLearningModel.path)
    print(model_path)
    model = torch.load(model_path)
    df = pd.DataFrame({"ds": dates, "y": prices})
    df["unique_id"] = 1.0
    df = df[["unique_id", "ds", "y"]]
    dataset, *_ = TimeSeriesDataset.from_dataframe(df)
    predictedPrice = model.predict(dataset=dataset)

    current_date = datetime.now().date()
    start_date = current_date + timedelta(days=1)
    dates = pd.date_range(start=start_date, periods=len(predictedPrice), freq="D")
    df_predicted = pd.DataFrame({"Dates": dates, "Predicted": predictedPrice.flatten()})
    lstmModel.update.predictedData(df_predicted.to_json())
    predicted_dates = df_predicted["Dates"].dt.strftime("%Y-%m-%d").tolist()
    predicted_prices = df_predicted["Predicted"].tolist()

    return predicted_dates, predicted_prices


def forecast_NHits(dates, prices, coinId):
    NHits_info = Cryptocurrencies.objects.get(id=coinId).lstmId
    NhitsId = NHits_info.id
    NHitsModel = NHitsModel.objects.get(id=NhitsId)
    model_path = str(NHitsModel.machineLearningModel.path)
    print(model_path)
    model = torch.load(model_path)
    df = pd.DataFrame({"ds": dates, "y": prices})
    df["unique_id"] = 1.0
    df = df[["unique_id", "ds", "y"]]
    dataset, *_ = TimeSeriesDataset.from_dataframe(df)
    predictedPrice = model.predict(dataset=dataset)

    current_date = datetime.now().date()
    start_date = current_date + timedelta(days=1)
    dates = pd.date_range(start=start_date, periods=len(predictedPrice), freq="D")
    df_predicted = pd.DataFrame({"Dates": dates, "Predicted": predictedPrice.flatten()})
    NHitsModel.update.predictedData(df_predicted.to_json())
    predicted_dates = df_predicted["Dates"].dt.strftime("%Y-%m-%d").tolist()
    predicted_prices = df_predicted["Predicted"].tolist()

    return predicted_dates, predicted_prices
