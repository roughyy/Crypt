from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

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
    import yfinance as yf

    symbols = (
        "btc-usd",
        "eth-usd",
        "usdt-usd",
        "bnb-usd",
        "xrp-usd",
        "ada-usd",
        "doge-usd",
        "matic-usd",
        "sol-usd",
    )

    try:
        context = []
        for i in symbols:
            context.append(yf.Ticker(i).info)

        return render(request, "core/search.html", {"context": context})

    except Exception as e:
        messages.error(request, f"Something Went Wrong: {str(e)}")

    return render(request, "core/search.html")


def detail(request):
    import yfinance as yf
    import json
    import datetime
    from django.contrib import messages

    if request.method == "POST":
        symbol = request.POST["symbol"]
        try:
            # Create a Ticker object for the stock
            ticker = yf.Ticker(symbol)

            # Retrieve historical data about the stock
            historical_data = ticker.history(period="1mo")
            coin_info = ticker.info

            # Extract the Close prices from the historical data
            close_prices = historical_data["Close"].values.tolist()
            num_days = len(close_prices)
            start_date = datetime.date.today() - datetime.timedelta(days=num_days)
            dates = [start_date + datetime.timedelta(days=i) for i in range(num_days)]
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

        except Exception as e:
            # Handle the error
            return render(
                request, "core/detail.html", {"error_message": "Something went wrong"}
            )

    else:
        return render(
            request, "core/detail.html", {"error_message": "Enter a Stock Code"}
        )


def upload(request):
    return render(request, "core/upload.html")


def profile(request):
    return render(request, "core/profile.html")


# non page function:


def populateDatabase(request):
    return render(request)


def cryptocurrenciesDailyUpdate(request):
    return render(request)
