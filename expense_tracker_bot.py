import logging.config
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Loading logging configuration from JSON file
def setup_logging(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    except FileNotFoundError:
        # Log an error message if the config file is not found
        print(f"Error: Logging configuration file '{config_file}' not found.")
        return
    except json.JSONDecodeError:
        # Log an error message if the config file is invalid JSON
        print(f"Error: Invalid JSON format in logging configuration file '{config_file}'.")
        return
    except Exception as e:
        # Log any other unexpected errors
        print(f"Error: An unexpected error occurred: {e}")
        return

# Loading logging configuration
setup_logging('D:\Coding\PythonCoding\ExpenseTracker\ExpenseTrackerBot\logging_config.json')

# Defining a dictionary to store user balances
user_balances = {}

# Defining a logger
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Welcome to the Expense Tracking Bot, {username}!")

# Defining /setbalance command handler
async def set_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        balance = float(context.args[0])
        if balance < 0:
            await update.message.reply_text("Balance cannot be negative.")
            return
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid balance.")
        return

    # Setting the balance for the user
    user_id = update.effective_user.id
    user_balances[user_id] = balance
    await update.message.reply_text(f"Your balance has been set to {balance:.0f}.")
    logger.info(f"User {user_id} set balance to {balance}")

# Defining /balance command handler
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_balances:
        await update.message.reply_text("You haven't set your balance yet. Use /setbalance command to set it.")
    
    balance = user_balances[user_id]
    await update.message.reply_text(f"Your balance is currently {balance:.0f} tenge.")

# Defining /updatebalance command handler
async def update_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        update_amount = float(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid balance.")
        return

    # Setting the balance for the user
    user_id = update.effective_user.id
    if user_id not in user_balances:
        await update.message.reply_text("You haven't set your balance yet. Use /setbalance command to set it.")
    user_balances[user_id] += update_amount
    await update.message.reply_text(f"You successfully changed your balance by {update_amount:.0f}")
    logger.info(f"User {user_id} updated balance by {update_amount}")


if __name__ == '__main__':
    application = ApplicationBuilder().token('7179677090:AAE6WIcnko1KOEhAYHVxVsZepFUII5mItzw').build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler('setbalance', set_balance))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('updatebalance', update_balance))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)
