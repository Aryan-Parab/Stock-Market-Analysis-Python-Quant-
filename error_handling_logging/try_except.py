# def error():
#     try:
#         x = 10 / 0
#     except:
#         print("Something went wrong")

#     finally:
#         print("Execution completed")

# error()

# class APIerror(Exception):
#     pass

# def get_price():
#     raise APIerror("Failed to retrieve price")

# try:
#     get_price()

# except APIerror as e:
#     print("An API error occurred:", e)

from datetime import date
import logging
import os
name = 'cfg'
#logging.error( '%s raised and error',name) # %s is the placeholder where name value will be inserted


# this example shows how to log messages directly to the the file using Python's file handler
logger = logging.getLogger("SimpleLogger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log") # to send messages directly to the disk file
logger.addHandler(file_handler) # attaches the handler to the logger

# messages of different types of importance to the file
#print(logger.info("Thisis an info message"))
#print(logger.error("This is an error message"))

#----
# Steps on logging
# logging a variable
import logging
logging.basicConfig(level = logging.INFO, format = '%(levelname)s:%(message)s')
age = 25
#logging.info("The value of age is %d",age)

#--------------- CLAUDE CODE -----------------
# Basic logging code 

import logging

# Basic setup 
def log1():
    logging.basicConfig(level = logging.DEBUG) # basicConfiguration-> set up the logging system # logging.Debug -> show all logs from DEBUG and above
    logging.debug("THis is a debug message") # only shown in dev
    logging.info("Order placed successfully") # normal operation
    logging.warning("low data quality") # something odd
    logging.error("API CALL failed") # something broke
    logging.critical("Database connection failed") # System broken

#log1()

# Intermediate - log to a file with timestamps


def log2():
    logging.basicConfig(
    level=logging.DEBUG,format= "%(asctime)s | %(levelname)s | %(message)s",
    datefmt= "%Y-%m-%d %H:%M:%S", 
    handlers = [logging.FileHandler("trading.log"), logging.StreamHandler()])
    # stream handler => prints to your terminal + file handler -> write to a file on disk or create if needed

    logger = logging.getLogger(__name__) # name is written to specify the name of file.py so when logging 
    # for multiple files we know file has which logs

    logger.info("Bot Started and its status")
    logger.warning("We need to skip trades because of certain issue")
    logger.error("An error occurred while processing the trade")
    logger.critical("System failure - immediate attention required")

#log2()
#--------------xxxxxxxxxx--------- Live Trading logging ( Alter this to get optimum results.)
import logging
from logging.handlers import RotatingFileHandler

def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate=False
    # Clear any old handlers for duplication purposes
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                 datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter) # instance, not class

    file_handler = RotatingFileHandler("trading.log", maxBytes=5*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter) # instance , not class
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = set_logger('trading')

# Wrapping API CALLS
def run_signal(ticker, rsi):
    logger.debug(f"Calculating signal for {ticker} | rsi = {rsi:.3f}")
    if rsi>70:
        logger.info (f'Sell signal triggered for {ticker}, rsi = {rsi:.3f}')
    elif rsi<30:
        logger.info(f'Buy signal triggered for {ticker}, rsi = {rsi:.3f}')
    else:
        logger.info(f'No signal triggered for {ticker}, rsi = {rsi:.3f}')

logger.error("An error occurred while processing the trade")
logger.critical("System failure - immediate attention required")


run_signal("AAPL", 75.5)
run_signal("TSLA", 25.1)
run_signal("MSFT", 50.0)

