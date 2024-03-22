import logging.config
import json
import sqlite3
import tracemalloc
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

tracemalloc.start()

# Defining a dictionary to store user balances
user_balances = {}

# Defining a logger
logger = logging.getLogger(__name__)

def add_expense_to_database(user_id, expense_type, amount, date, description):
    conn = sqlite3.connect('D:\Coding\PythonCoding\ExpenseTracker\ExpenseTrackerBot\expense_storage.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses_table (user_id, expense_type, amount, date, description) VALUES (?, ?, ?, ?, ?)", (user_id, expense_type, amount, date, description))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Welcome to the Expense Tracking Bot, {username}!")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text="List of available commands:\n/start - Start Expense Tracker\n/help - View the list of available commands\n/setbalance [number] - Set your current balance\n/balance - View your current balance\n/updatebalance [+/-number] - Update your current balance")

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

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text("Please enter the amount of the expense:")

    context.user_data['state'] = 'amount'

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = context.user_data.get('state')

    if state == 'amount':
        amount = update.message.text

        context.user_data['amount'] = amount
        await update.message.reply_text("Please enter the type of the expense:")
        context.user_data['state'] = 'expense_type'
    elif state == 'expense_type':
        e_type = update.message.text
        context.user_data['expense_type'] = e_type

        await update.message.reply_text("Please enter the date of the expense (YYYY-MM-DD):")
        context.user_data['state'] = 'date'
    elif state == 'date':
        date = update.message.text
        context.user_data['date'] = date
        
        await update.message.reply_text("Please enter a description of the expense:")
        context.user_data['state'] = 'description'
    elif state == 'description':
        description = update.message.text
        context.user_data['description'] = description
        
        add_expense_to_database(user_id, context.user_data['expense_type'], context.user_data['amount'], context.user_data['date'], context.user_data['description'])
        
        await update.message.reply_text("Expense added successfully!")
        logger.info(f"User {user_id} added an expense of type - {context.user_data['expense_type']} with an amount {context.user_data['amount']} on {context.user_data['date']} stating a following description:\n\t{context.user_data['description']}")
        context.user_data.clear()

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print('Starting bot...')
    application = ApplicationBuilder().token('7179677090:AAE6WIcnko1KOEhAYHVxVsZepFUII5mItzw').build()
    
    application.add_handler(CommandHandler("addexpense", add_expense))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler('setbalance', set_balance))
    application.add_handler(CommandHandler('balance', balance))
    application.add_handler(CommandHandler('updatebalance', update_balance))

    application.add_handler(MessageHandler(filters.TEXT, message_handler))
    application.add_error_handler(error)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)
