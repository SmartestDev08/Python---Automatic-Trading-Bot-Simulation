import requests
import os
from dotenv import load_dotenv
import datetime

# This project uses RealStonks's RapidAPI
# The price is regarding Google
# https://www.nasdaq.com/market-activity/stocks/googl
# This bot only grabs data once per day, whenever the file is executed

def get_todays_info():
    def fetch_todays_info():
        load_dotenv()

        url = "https://realstonks.p.rapidapi.com/GOOGL"

        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST")
        }

        response = requests.get(url, headers=headers)
        response = response.json()

        return response
    
    def has_been_fetched_already():
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")
        
        content = open("data/todaysPrice.txt", "r").read()

        return date in content
    
    def get_todays_fetched_info():
        data = {}
        
        #date = datetime.datetime.now()
        #date = date.strftime("%d-%m-%Y")
        #data["date"] = date

        with open("data/todaysPrice.txt", "r") as f:
            for i, line in enumerate(f.readlines()):
                line = line.replace("\n", "")

                if i != 0:
                    label, value = line.split(" ")
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                    data[label] = value
                else:
                    data["date"] = line
                    
        
        return data

    def record_last_days_info():
        info = get_todays_fetched_info()
        with open("data/pricesRecord.txt", "a") as f:
            for label in info:
                if label != "date":
                    f.write(f"{label} {info[label]}\n")
                else:
                    f.write(f"{info[label]}\n")
            
            f.close()
        
        return
    
    def write_todays_new_info(info):
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")

        with open("data/todaysPrice.txt", "w") as f:
            f.write(f"{date}\n")
            for label in info:
                f.write(f"{label} {info[label]}\n")
            f.close()
        
        return

    if has_been_fetched_already():
        info = get_todays_fetched_info()
        return info
    else:
        record_last_days_info()
        info = fetch_todays_info()
        write_todays_new_info(info)
        return info

def save_transaction(action, lost, won, new_data):
    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")
    data = {
        "Action": action,
        "Lost": lost,
        "Won": won,
        "NewData": new_data
    }

    with open("data/transactions.txt", "a") as f:
        f.write(f"{date}\n")
        for label in data:
            value = data[label]
            f.write(f"{label}: {value}\n")
        
        f.close()
    
    return True

def buy(money_spent):
    info = get_todays_info()
    stock_price = info["price"]

    current_data = {}
    with open("data/status.txt", "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")

            label, value = line.split(" ")

            try:
                value = float(value)
            except ValueError:
                pass

            current_data[label] = value
    
    stocks_bought = money_spent / stock_price
    new_data = {
        "Money": current_data["Money"] - money_spent,
        "Stocks": current_data["Stocks"] + stocks_bought
    }

    with open("data/status.txt", "w") as f:
        for label in new_data:
            value = new_data[label]

            f.write(f"{label} {value}\n")
    
    save_transaction("buy", money_spent, stocks_bought, new_data)
    return True

def sell(stocks_sold):
    info = get_todays_info()
    stock_price = info["price"]

    current_data = {}
    with open("data/status.txt", "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")

            label, value = line.split(" ")

            try:
                value = float(value)
            except ValueError:
                pass

            current_data[label] = value
    
    money_gained = stocks_sold * stock_price
    new_data = {
        "Money": current_data["Money"] + money_gained,
        "Stocks": current_data["Stocks"] - stocks_sold
    }

    with open("data/status.txt", "w") as f:
        for label in new_data:
            value = new_data[label]

            f.write(f"{label} {value}\n")
    
    save_transaction("sell", stocks_sold, money_gained, new_data)
    return True

todays_info = get_todays_info()
print(todays_info)

buy(100)
sell(0.1)