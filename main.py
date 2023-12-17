import requests
import os
from dotenv import load_dotenv
import datetime

# This project uses RealStonks's RapidAPI
# The price is regarding Google
# https://www.nasdaq.com/market-activity/stocks/googl
# This bot only grabs data once per day, whenever the file is executed

def get_todays_data():
    def fetch_todays_data():
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
        
        content = open("globalData/todaysPrice.txt", "r").read()

        return date in content
    
    def get_todays_fetched_data():
        data = {}
        
        #date = datetime.datetime.now()
        #date = date.strftime("%d-%m-%Y")
        #data["date"] = date

        with open("globalData/todaysPrice.txt", "r") as f:
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

    def record_last_days_data():
        data = get_todays_fetched_data()
        with open("globalData/pricesRecord.txt", "a") as f:
            for label in data:
                if label != "date":
                    f.write(f"{label} {data[label]}\n")
                else:
                    f.write(f"{data[label]}\n")
            
            f.close()
        
        return
    
    def write_todays_new_data(data):
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")

        with open("globalData/todaysPrice.txt", "w") as f:
            f.write(f"{date}\n")
            for label in data:
                f.write(f"{label} {data[label]}\n")
            f.close()
        
        return

    if has_been_fetched_already():
        data = get_todays_fetched_data()
        return data
    else:
        record_last_days_data()
        data = fetch_todays_data()
        write_todays_new_data(data)
        return data

def get_previous_days_data():
    data = []
    with open("globalData/pricesRecord.txt", "r") as f:
        current_day = {}
        for i, line in enumerate(f.readlines()):
            line = line.replace("\n", "")
            if len(line) > 2:
                if line.count("-") == 2 and i != 0:
                    data.append(current_day)
                    current_day = {}
                elif i != 0:
                    label, value = line.split(" ")
                    try:
                        value = float(value)
                    except ValueError:
                        pass

                    current_day[label] = value
        data.append(current_day)
    
    return data

def save_transaction(botName, action, lost, won, new_data):
    date = datetime.datetime.now()
    date = date.strftime("%d-%m-%Y")
    data = {
        "Action": action,
        "Lost": lost,
        "Won": won,
        "NewData": new_data
    }

    with open(f"individualData/{botName}/transactions.txt", "a") as f:
        f.write(f"{date}\n")
        for label in data:
            value = data[label]
            f.write(f"{label}: {value}\n")
        
        f.close()
    
    return True

def buy(botName, money_spent):
    data = get_todays_data()
    stock_price = data["price"]

    current_data = {}
    with open(f"individualData/{botName}/status.txt", "r") as f:
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

    with open(f"individualData/{botName}/status.txt", "w") as f:
        for label in new_data:
            value = new_data[label]

            f.write(f"{label} {value}\n")
    
    save_transaction(botName, "buy", money_spent, stocks_bought, new_data)
    return True

def sell(botName, stocks_sold):
    data = get_todays_data()
    stock_price = data["price"]

    current_data = {}
    with open(f"individualData/{botName}/status.txt", "r") as f:
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

    with open(f"individualData/{botName}/status.txt", "w") as f:
        for label in new_data:
            value = new_data[label]

            f.write(f"{label} {value}\n")
    
    save_transaction(botName, "sell", stocks_sold, money_gained, new_data)
    return True

def get_bot_data(botName):
    data = {}
    with open(f"individualData/{botName}/status.txt", "r") as f:
        for line in f.readlines():
            line = line.replace("\n", "")

            label, value = line.split(" ")
            value = float(value)

            data[label] = value
    
    return data

class BotActions():
    def __init__(self, previous_days_data, todays_data):
        self.previous_days_data = previous_days_data
        self.todays_data = todays_data
    
    def Bot1(self): # Super simple bot. It calculates the median price of the last 5 days. If price is below average, it buys 1/5, if above, it sells 1/5
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")
        bot_name = "Bot1"
        previous_days_data = self.previous_days_data
        todays_data = self.todays_data
        bot_data = get_bot_data(bot_name)
        
        last_transaction_date = None
        with open(f"individualData/{bot_name}/transactions.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")

                if line.count("-") == 2:
                    last_transaction_date = line
        
        if date != last_transaction_date:
            avg_recent_price = 0
            days_counted = 0

            for i, day_data in enumerate(previous_days_data):
                if i > 5:
                    break

                days_counted += 1
                avg_recent_price += day_data["price"]
            
            avg_recent_price /= days_counted
            current_price = todays_data["price"]
            transaction_done = "Nothing"
            
            if current_price < avg_recent_price:
                money_spent = bot_data["Money"] / 4
                if money_spent > 0:
                    transaction_done = f"Bought stocks with {money_spent} money"
                    buy(bot_name, money_spent)
            elif current_price > avg_recent_price:
                stocks_sold = bot_data["Stocks"] / 4
                if stocks_sold > 0:
                    transaction_done = f"Sold {stocks_sold} stocks"
                    sell(bot_name, stocks_sold)
            
            new_bot_data = get_bot_data(bot_name)
            return [transaction_done, new_bot_data]
        
        return ["Already did today's transaction", bot_data]

    def Bot2(self): # Very simple bot. It calculated the median price of the last 10 days. The amount it will sell / buy will depend on how much it changes.
        date = datetime.datetime.now()
        date = date.strftime("%d-%m-%Y")
        bot_name = "Bot2"
        previous_days_data = self.previous_days_data
        todays_data = self.todays_data
        bot_data = get_bot_data(bot_name)
        
        last_transaction_date = None
        with open(f"individualData/{bot_name}/transactions.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")

                if line.count("-") == 2:
                    last_transaction_date = line
        
        if date != last_transaction_date:
            avg_recent_price = 0
            days_counted = 0

            for i, day_data in enumerate(previous_days_data):
                if i > 10:
                    break

                days_counted += 1
                avg_recent_price += day_data["price"]
            
            avg_recent_price /= days_counted
            current_price = todays_data["price"]
            transaction_done = "Nothing"
            
            prices_difference = current_price - avg_recent_price

            if prices_difference < 0:
                prices_difference *= -1
                money_fraction = max(prices_difference / avg_recent_price, 1)
                money_spent = bot_data["Money"] * money_fraction
                
                if money_spent > 0:
                    transaction_done = f"Bought stocks with {money_spent} money"
                    buy(bot_name, money_spent)
            elif prices_difference > 0:
                stocks_fraction = max(prices_difference / avg_recent_price, 1)
                stocks_sold = bot_data["Stocks"] * stocks_fraction
                if stocks_sold > 0:
                    transaction_done = f"Sold {stocks_sold} stocks"
                    sell(bot_name, stocks_sold)
            
            new_bot_data = get_bot_data(bot_name)
            return [transaction_done, new_bot_data]
        
        return ["Already did today's transaction", bot_data]

todays_data = get_todays_data()
previous_days_data = get_previous_days_data()

actions = BotActions(previous_days_data, todays_data)
result_bot1 = actions.Bot1()
result_bot2 = actions.Bot2()

print("Bot 1:")
print(result_bot1)

print("Bot 2:")
print(result_bot2)
