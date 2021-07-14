# Import requests and beautifulsoup for scraping
import requests
from bs4 import BeautifulSoup

# package for sending email reminder
import smtplib, ssl
from email.message import EmailMessage

# package for getting datetime, timezone, and interval for update
from datetime import datetime
import pytz
import time


def send_email(
    ticker: str, price: float, og_price: float, email_add: str, ps: str
):
    """The function to send out a reminder email if the stock price has rise
        by 3% or drop by 10% from the purchased price

    Args:
        ticker (str): the ticker code for the stock
        price (float): The scraped real time stock price from yahoo finance
        og_price (float): The purhcased price for the tracking stock
        email_add (str): The email address for both sender and receipient
                          as it's sending reminder to ownself
        ps (str): The password for the email account

    Return:
        None
        Sent out the reminder email and print a susscessful message
    """

    if price > og_price:
        trend = "rise"
    else:
        trend = "drop"

    # The email subject, sender, recipient, and content
    msg = EmailMessage()
    msg["Subject"] = (
        f"Price of {ticker} {trend} from purchased price {og_price}"
    )
    msg["From"] = email_add
    msg["To"] = email_add
    msg.set_content(
        f"Price of {ticker} {trend} from purchased price {og_price}"
    )

    context = ssl.create_default_context()

    # set up SMTP Host, Login info and password, send out the email.
    # If you want to email address other than gmail, change the SMTP host here.
    with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
        smtp.starttls(context=context)
        smtp.login(msg["From"], ps)
        smtp.send_message(msg)
        smtp.quit()

    print(f"email reminder for {ticker} is sent")


def get_stock_price(ticker: str):
    """Get real-time stock price from yahoo finance

    Args:
        ticker (str): the ticker code for the stock
    Returns:
        float
        the price of a given stock
    """

    # set up agent for scraping
    ag = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/71.0.3578.98 Safari/537.36"
        )
    }

    # the yahoo finance url for the given ticker
    url = f"https://hk.finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch"

    response = requests.get(url, headers=ag, timeout=30)
    soup = BeautifulSoup(response.text, "lxml")

    # extract the price and convert it back to a float
    price = float(
        soup.find(
            "span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}
        ).text
    )
    return price


def main(
    ticker_list: list, og_price_list: list, email_add: str, ps: str, tz: str
):
    """Sent reminder email to yourself when the price the
    stocks you purchased rise by 5% or drop by 10%

    Args:
        ticker_list (list): the list of ticker code
        og_price_list (list): the purchase price of stocks in the same order of the ticker_list
        email_add (str): The email address for both sender and receipient (same as it's sending to yourself)
        ps (str): The password for the email account
        tz (str): the timezone of the stock market you invested (e.g. "Asia/Hong_Kong" for Hong Kong).
                  You can check timezon names with pytz.all_timezones
    """
    # Get timezone with pytz from given input
    timezone = pytz.timezone(tz)

    # infinite loop within the operating hour of the specific stock market (usually 9am - 4pm locate time)
    while (datetime.now(tz=timezone).hour >= 9) and (
        datetime.now(tz=timezone).hour <= 16
    ):
        # check each purchased stock and send reminder email if condition met
        for x in zip(ticker_list, og_price_list):
            price = get_stock_price(x[0])
            # condition now set at 5% rise or 10% drop from purchased price
            if price > (x[1] * 1.05) or price < (x[1] * 0.9):
                send_email(x[0], price, x[1], email_add, ps)
            else:
                print(f"{x[0]}:no update")

        # the interval of the checking - currently set at 1 minutes (60 sec)
        time.sleep(60)
    else:
        print("stock market closed")


if __name__ == "__main__":
    main(
        ["1810.HK", "3032.HK"],
        [26.9, 7.55],
        "xxxx@gmail.com",  # This is a dummy gmailplease use your own email address before running the script
        "yyyyyyyyy",  # please use your own email password before running the script
        "Asia/Hong_Kong",
    )
