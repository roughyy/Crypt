from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.urls import reverse


# Create your views here.


def termsandconditions(request):
    return render(request, "core/termsandconditions.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/")

            else:
                messages.info(request, " Username or Password is incorrect")

    return render(request, "core/login.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    else:
        form = CreateUserForm()

        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()

                messages.success(request, "Account has been sucessfully created")

                return redirect("/login/")

        else:
            form = CreateUserForm()

        context = {"form": form}
    return render(request, "core/signup.html", context)


def logoutUser(request):
    logout(request)
    return redirect("core:login")


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


@login_required(login_url="core:login")
def search(request):
    from .models import Cryptocurrencies
    import yfinance as yf

    try:
        queryset = Cryptocurrencies.objects.all().values()
        for currency in queryset:
            currentPrice = yf.download(currency["symbol"], interval="1m")["Close"][-1]
            Cryptocurrencies.objects.filter(symbol=currency["symbol"]).update(
                lastPrice=currentPrice
            )
            Cryptocurrencies.objects.filter(symbol=currency["symbol"]).values()
            historicalData = (
                Cryptocurrencies.objects.filter(symbol=currency["symbol"])
                .get()
                .get_historicalData()
            )
            lastPrice = list(historicalData["Close"])
            lastPrice = lastPrice[-2]
            currency["PercentChange"] = ((currentPrice - lastPrice) / lastPrice) * 100
        context = {"queryset": queryset}
        return render(request, "core/search.html", context)

    except Exception as e:
        messages.error(request, f"Something Went Wrong: {str(e)}")

    return render(request, "core/search.html")


@login_required(login_url="core:login")
def detail(request):
    import yfinance as yf
    import json
    from django.contrib import messages
    from .models import (
        Cryptocurrencies,
        CoinCategory,
        LSTMModel,
        ProphetModel,
        NHitsModel,
    )
    from datetime import datetime
    import pandas as pd

    if request.method == "POST":
        symbol = request.POST["symbol"]

        if Cryptocurrencies.objects.filter(symbol=symbol).exists():
            coin = Cryptocurrencies.objects.filter(symbol=symbol).get()
            lstmInfo = LSTMModel.objects.filter(name=coin.lstmId).get()
            prophetInfo = ProphetModel.objects.filter(name=coin.prophetId).get()
            nhitsInfo = NHitsModel.objects.filter(name=coin.nhitsId).get()
            currentDate = timezone.now().date()
            lastUpdated = coin.updateDateTime.date()

            if lastUpdated == currentDate:
                historical_data = coin.get_historicalData()
                historical_data = historical_data.reset_index()[["Date", "Close"]]
                historical_data["Date"] = historical_data["Date"].apply(
                    lambda x: datetime.strftime(x, "%Y-%m-%d")
                )
                dates = list(historical_data["Date"])
                prices = list(historical_data["Close"])
                coin_info = coin

                context = {
                    "dates": json.dumps(dates),
                    "prices": json.dumps(prices),
                    "info": coin_info,
                    "coinId": coin_info.id,
                    "lstmInfo": lstmInfo,
                    "prophetInfo": prophetInfo,
                    "nhitsInfo": nhitsInfo,
                }
            else:
                data = yf.download(symbol)
                data = data.reset_index()[["Date", "Close"]]
                data["Date"] = data["Date"].apply(
                    lambda x: datetime.strftime(x, "%Y-%m-%d")
                )
                data_json = data.to_json(orient="records")
                Cryptocurrencies.objects.filter(symbol=symbol).update(
                    historicalData=data_json
                )
                historical_data = data
                dates = list(historical_data["Date"])
                prices = list(historical_data["Close"])
                coin_info = coin

                context = {
                    "dates": json.dumps(dates),
                    "prices": json.dumps(prices),
                    "info": coin_info,
                    "coinId": coin_info.id,
                    "lstmInfo": lstmInfo,
                    "prophetInfo": prophetInfo,
                    "nhitsInfo": nhitsInfo,
                }

            return render(request, "core/detail.html", context=context)
        else:
            try:
                import datetime

                # Create a Ticker object for the stock
                ticker = yf.Ticker(symbol)

                # Retrieve historical data about the stock
                historical_data = yf.download(symbol)
                lastPrice = yf.download(symbol, interval="1m")["Close"][-1]
                coin_info = ticker.info
                coin_info["lastPrice"] = lastPrice

                if "longName" in coin_info:
                    coin_info.update({"coinName": coin_info["longName"]})
                else:
                    coin_info.update({"coinName": coin_info["name"]})

                # Extract the Close prices from the historical data
                close_prices = historical_data["Close"].values.tolist()
                num_days = len(close_prices)
                start_date = datetime.datetime.today() - datetime.timedelta(
                    days=num_days
                )
                dates = [
                    start_date + datetime.timedelta(days=i) for i in range(num_days)
                ]
                data = list(zip(dates, close_prices))

                # Create a list of dates and close prices
                dates = [d.strftime("%Y-%m-%d") for d, _ in data]
                prices = [p for _, p in data]

                # Create a context dictionary to pass data to the template
                context = {
                    "dates": json.dumps(dates),
                    "prices": json.dumps(prices),
                    "info": coin_info,
                    "coinId": None,
                }

                return render(request, "core/detail.html", context=context)

            except:
                return render(
                    request, "core/PageNotFound.html", {"message": "Symbol not found"}
                )

    else:
        messages.error(request, "Enter a Stock Code")
        return render(
            request, "core/detail.html", {"error_message": "Enter a Stock Code"}
        )


@login_required(login_url="core:login")
def upload(request):
    from .models import PersonalPrediction
    from .forms import UploadFile

    if request.method == "POST":
        form = UploadFile(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["file"]
            if not csv_file.name.endswith(".csv"):
                return HttpResponse("File is not a CSV")

            # Create a new PersonalPrediction object and save it
            personal_prediction = PersonalPrediction(
                userId=request.user, CSVFile=csv_file
            )
            personal_prediction.save()

            # Redirect to the page with the new PersonalPrediction object's ID as parameter
            return redirect("core:CustomPrediction", personal_prediction.id)
    else:
        form = UploadFile()

    return render(request, "core/upload.html", {"form": form})


@login_required(login_url="core:login")
def CustomPrediction(request, personal_prediction_id):
    from .models import PersonalPrediction
    import pandas as pd
    import json
    from datetime import datetime

    if request.user.is_authenticated:
        personal_prediction = PersonalPrediction.objects.get(id=personal_prediction_id)

        if personal_prediction.userId == request.user:
            data = personal_prediction.CSVFile
            df = pd.read_csv(data, sep=";")
            dates = df["timestamp"].tolist()
            dates = [
                datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
                for date in dates
            ]
            prices = df["close"].tolist()
            last_price = prices[-1]

            context = {
                "dates": json.dumps(dates),
                "prices": json.dumps(prices),
                "last_price": last_price,
                "predictionId": personal_prediction_id,
                "info": personal_prediction,
            }
            return render(request, "core/CustomPrediction.html", context=context)

    return render(
        request,
        "core/PageNotFound.html",
        {"message": "You're not authorize to view this page"},
    )


@login_required(login_url="core:login")
def result(request):
    from .forecast import forecast_prophet, forecast_lstm, forecast_NHits
    from datetime import datetime
    import json
    from .models import Cryptocurrencies, PersonalPrediction
    from django.shortcuts import get_object_or_404

    if request.method == "POST":
        prediction_id = request.POST.get("predictionId")
        coin_id = request.POST.get("coinId")
        info = None
        if prediction_id is not None and prediction_id != "":
            prediction_id = int(prediction_id)
            info = get_object_or_404(PersonalPrediction, id=prediction_id)
            print(info)
        else:
            prediction_id = None

        if coin_id is not None and coin_id != "" and coin_id != "None":
            coin_id = int(coin_id)
            info = get_object_or_404(Cryptocurrencies, id=coin_id)
            print(info)
        else:
            coin_id = None

        dates = (
            request.POST.get("dates", "")
            .replace("[", "")
            .replace("]", "")
            .replace("&quot;", "")
            .split(",")
        )
        prices = (
            request.POST.get("prices", "")
            .replace("[", "")
            .replace("]", "")
            .replace("&quot;", "")
            .split(",")
        )
        algorithm = request.POST.get("algorithm")
        n_days = int(request.POST.get("n_days", 0))

        # Convert datetime strings to a standard format
        dates = [
            datetime.strptime(date.strip().strip('"'), "%Y-%m-%d") for date in dates
        ]

        # Call the appropriate forecast function based on the selected algorithm
        if algorithm == "Prophet":
            predicted_dates, predicted_prices = forecast_prophet(
                dates, prices, n_days, Prediction_id=prediction_id, coin_id=coin_id
            )
        elif algorithm == "Lstm":
            predicted_dates, predicted_prices = forecast_lstm(
                dates, prices, coinId=coin_id
            )
        elif algorithm == "NHits":
            predicted_dates, predicted_prices = forecast_NHits(
                dates, prices, coinId=coin_id
            )
        else:
            return render(
                request, "core/PageNotFound.html", {"message": "Something Went Wrong"}
            )

        # Assuming predicted_dates is a list of strings
        dates = [date.strftime("%Y-%m-%d") for date in dates]

        context = {
            "dates": json.dumps(dates),
            "prices": json.dumps(prices),
            "predicted_dates": json.dumps(predicted_dates),
            "predicted_prices": json.dumps(predicted_prices),
            "last_price": float(prices[-1]),
            "last_predicted_price": float(predicted_prices[-1]),
            "info": info,
        }

        return render(request, "core/result.html", context)

    # Handle GET requests
    return render(
        request, "core/PageNotFound.html", {"message": "Invalid Request Method"}
    )


@login_required(login_url="core:login")
def dashboard(request):
    from .models import PersonalPrediction
    import json
    import datetime
    import pandas as pd

    if request.user.is_authenticated:
        list_predictions = (
            PersonalPrediction.objects.filter(userId=request.user.id)
            .exclude(predictedData=None)
            .order_by("-id")
        )

        if not list_predictions:
            return render(request, "core/PageNotFound.html", {"message": "No Data"})

        for prediction in list_predictions:
            if prediction.predictedData:
                predicted_data = prediction.get_predictedData()
                predicted_data = pd.DataFrame(predicted_data)
                predicted_dates = (
                    predicted_data["Date"].dt.strftime("%Y-%m-%d").tolist()
                )
                predicted_prices = predicted_data["Close"].tolist()
                prediction.predicted_dates = json.dumps(predicted_dates)
                prediction.predicted_prices = json.dumps(predicted_prices)

                # Retrieve the last price from the CSV file
                csv_data = pd.read_csv(prediction.CSVFile, sep=";")
                last_csv_price = csv_data["close"].iloc[-1]
                last_csv_date = csv_data["timestamp"].iloc[-1]
                last_csv_date = last_csv_date.split("T")[0]

                # Retrieve the last price from the predicted data
                last_predicted_price = predicted_prices[-1]
                last_predicted_date = (
                    predicted_data["Date"].iloc[-1].strftime("%Y-%m-%d")
                )

                # Assign additional fields to the prediction object
                prediction.last_csv_price = last_csv_price
                prediction.last_csv_date = last_csv_date
                prediction.last_predicted_price = last_predicted_price
                prediction.last_predicted_date = last_predicted_date

        latest_prediction = list_predictions.first()

        if latest_prediction and latest_prediction.predictedData:
            # Get the predicted data
            predicted_data = latest_prediction.get_predictedData()
            predicted_data = pd.DataFrame(predicted_data)
            data = latest_prediction.CSVFile
            data = pd.read_csv(data.path, sep=";")
            dates = data["timestamp"].tolist()
            dates = [
                datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                    "%Y-%m-%d"
                )
                for date in dates
            ]
            prices = data["close"].tolist()

            # Slice the arrays if needed to include only the last 60 data points
            if len(dates) > 60:
                dates = dates[-60:]
                prices = prices[-60:]

            # Split the predicted data into lists of dates and prices
            predicted_dates = predicted_data["Date"].dt.strftime("%Y-%m-%d").tolist()
            predicted_prices = predicted_data["Close"].tolist()

            # Format the dates consistently
            formatted_dates = [date for date in dates]
            formatted_predicted_dates = [date for date in predicted_dates]

            # Combine the dates arrays
            combined_dates = formatted_dates + formatted_predicted_dates

            print(list_predictions)

            # Add necessary fields to the context
            context = {
                "list_predictions": list_predictions,
                "latest_prediction": latest_prediction,
                "file_name": latest_prediction.CSVFile.name,
                "prices": json.dumps(prices),
                "dates": json.dumps(formatted_dates),
                "predicted_dates": json.dumps(formatted_predicted_dates),
                "combined_dates": json.dumps(combined_dates),
                "predicted_prices": json.dumps(predicted_prices),
            }
        else:
            # No latest prediction found
            context = {
                "list_predictions": list_predictions,
            }

        return render(request, "core/dashboard.html", context=context)

    return render(request, "core/dashboard.html")


def pastPrediction(request, personal_prediction_id):
    from .models import PersonalPrediction
    from django.contrib.auth.models import User
    import json
    import datetime
    import pandas as pd

    if request.user.is_authenticated:
        personal_prediction = PersonalPrediction.objects.get(id=personal_prediction_id)
        user = User.objects.get(username=personal_prediction.userId)
        print(request.user.username)
        print(personal_prediction.userId)
        if request.user.id != user.id:
            return render(
                request,
                "core/PageNotFound.html",
                {"message": "You are not authorized to view this page"},
            )
        else:
            # Get the predicted data
            predicted_data = personal_prediction.get_predictedData()
            predicted_data = pd.DataFrame(predicted_data)
            data = personal_prediction.CSVFile
            data = pd.read_csv(data.path, sep=";")
            dates = data["timestamp"].tolist()
            dates = [
                datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                    "%Y-%m-%d"
                )
                for date in dates
            ]
            prices = data["close"].tolist()

            # Slice the arrays if needed to include only the last 60 data points
            if len(dates) > 120:
                dates = dates[-60:]
                prices = prices[-60:]

            # Split the predicted data into lists of dates and prices
            predicted_dates = predicted_data["Date"].dt.strftime("%Y-%m-%d").tolist()
            predicted_prices = predicted_data["Close"].tolist()

            # Format the dates consistently
            formatted_dates = [date for date in dates]
            formatted_predicted_dates = [date for date in predicted_dates]

            # Combine the dates arrays
            combined_dates = formatted_dates + formatted_predicted_dates

            # Add necessary fields to the context
            context = {
                "file_name": personal_prediction.CSVFile.name,
                "prices": json.dumps(prices),
                "dates": json.dumps(formatted_dates),
                "last_csv_price": prices[-1],
                "last_predicted_price": predicted_prices[-1],
                "predicted_dates": json.dumps(formatted_predicted_dates),
                "combined_dates": json.dumps(combined_dates),
                "predicted_prices": json.dumps(predicted_prices),
            }

            return render(request, "core/pastPrediction.html", context=context)

    return render(request, "core/pastPrediction.html")


from django.http import HttpResponseNotFound


def PageNotFound(request, message):
    return HttpResponseNotFound(
        render(request, "core/PageNotFound.html", {"message": message})
    )


# Debug functions


@user_passes_test(lambda u: u.is_staff)
def debug(request):
    return render(request, "core/debug.html")


@user_passes_test(lambda u: u.is_staff)
def populateCryptocurrenciesData(request):
    import yfinance as yf
    from .models import Cryptocurrencies, CoinCategory

    symbols = (
        "BTC-USD",
        "ETH-USD",
        "USDT-USD",
        "BNB-USD",
        "USDC-USD",
        "XRP-USD",
        "ADA-USD",
        "Doge-USD",
        "Matic-USD",
        "SOL-USD",
    )
    try:
        with transaction.atomic():
            for symbol in symbols:
                currency = yf.Ticker(symbol)
                name = currency.info["name"]
                coinSymbol = currency.info["symbol"]
                lastPrice = yf.download(symbol, interval="1m")["Close"][-1]

                if Cryptocurrencies.objects.filter(symbol=coinSymbol).exists():
                    continue

                categoryId = CoinCategory.objects.get(category="Regular")
                coin = Cryptocurrencies()
                coin.coinName = name
                coin.symbol = coinSymbol
                coin.lastPrice = lastPrice
                coin.categoryId = categoryId
                coin.save()

        messages.info(request, "Crypto Data Has been populated")

    except Exception as e:
        messages.error(request, f"Something Went Wrong: {str(e)}")

    return redirect("core:debug")


@user_passes_test(lambda u: u.is_staff)
def populateCryptocurrenciesHistoricalData(request):
    import yfinance as yf
    from .models import Cryptocurrencies
    from datetime import datetime

    symbols = (
        "BTC-USD",
        "ETH-USD",
        "USDT-USD",
        "BNB-USD",
        "USDC-USD",
        "XRP-USD",
        "ADA-USD",
        "Doge-USD",
        "Matic-USD",
        "SOL-USD",
    )
    try:
        for symbol in symbols:
            data = yf.download(symbol)
            data = data.reset_index()[["Date", "Close"]]
            data["Date"] = data["Date"].apply(
                lambda x: datetime.strftime(x, "%Y-%m-%d")
            )
            data_json = data.to_json(orient="records")
            Cryptocurrencies.objects.filter(symbol=symbol).update(
                historicalData=data_json, updateDateTime=datetime.now()
            )
            messages.info(request, "Crypto historical data has been populated")

    except Exception as e:
        messages.error(request, f"Something Went Wrong: {str(e)}")

    return redirect("core:debug")
