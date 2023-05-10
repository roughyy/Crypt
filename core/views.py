from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse


import datetime

# Create your views here.


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


def detail(request):
    import yfinance as yf
    import json
    from django.contrib import messages
    from .models import Cryptocurrencies, CoinCategory
    from datetime import datetime

    if request.method == "POST":
        symbol = request.POST["symbol"]

        if Cryptocurrencies.objects.filter(symbol=symbol).exists():
            coin = Cryptocurrencies.objects.filter(symbol=symbol).get()
            currentDate = timezone.now().date()
            lastUpdated = coin.updateDateTime.date()

            if lastUpdated == currentDate:
                historical_data = coin.get_historicalData()
                dates = list(historical_data.index.strftime("%Y-%m-%d"))
                prices = list(historical_data["Close"])
                coin_info = coin

                context = {
                    "dates": json.dumps(dates),
                    "prices": json.dumps(prices),
                    "info": coin_info,
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


def CustomPrediction(request, personal_prediction_id):
    from .models import PersonalPrediction
    import pandas as pd
    import json
    from datetime import datetime

    if request.user.is_authenticated:
        personal_prediction = PersonalPrediction.objects.get(id=personal_prediction_id)
        previous_url = request.META.get("HTTP_REFERER", "/")

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
            }
            return render(request, "core/CustomPrediction.html", context=context)

    return render(
        request,
        "core/PageNotFound.html",
        {"message": "Your'e not authorize to view this page"},
    )


def profile(request):
    return render(request, "core/profile.html")


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
                historicalData=data_json, updateDateTime=datetime.datetime.now()
            )
            messages.info(request, "Crypto historical data has been populated")

    except Exception as e:
        messages.error(request, f"Something Went Wrong: {str(e)}")

    return redirect("core:debug")
