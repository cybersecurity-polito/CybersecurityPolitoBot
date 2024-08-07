#!/usr/bin/env python

"""
Cybersecurity Polito Bot

This Telegram bot is designed to respond to messages, provide email verification functionality, and send GitHub organization invitations.
Two tokens are required for this bot to work: a Telegram bot token and a GitHub token.

Main Features:
1. /start command: Initiates interaction with the bot.
2. /help command: Provides information on how to use the bot.
3. /invite command: Sends a GitHub organization invitation to the user's email address.

The bot starts and runs until Ctrl-C is pressed on the command line.
"""

import os
import logging
import re
import time
import requests
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_markdown_v2


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_message_en = (
        "🇬🇧 Welcome to the `cybersecurity\\-polito` GitHub organization bot\\!\n"
        "To join the organization, please link your student email \\(sXXXXXX@studenti\\.polito\\.it\\) "
        "to your existing GitHub account and use the /invite command to send your email in a message\\.\n"
        "Available commands:\n"
        "/start - Start interacting with the bot\n"
        "/help - Show this help message\n"
        "/invite - Request an invitation to the organization through your student email"
    )

    help_message_it = (
        "🇮🇹 Benvenuto nel bot dell'organizzazione GitHub `cybersecurity\\-polito`\\!\n"
        "Per unirti all'organizzazione, collega la tua email studentesca \\(sXXXXXX@studenti\\.polito\\.it\\) "
        "al tuo account GitHub esistente e utilizza il comando /invite per inviare la tua email in un messaggio\\.\n"
        "Comandi disponibili:\n"
        "/start - Inizia a interagire con il bot\n"
        "/help - Mostra questo messaggio di aiuto\n"
        "/invite - Richiedi un invito all'organizzazione tramite la tua email studentesca"

    await update.message.reply_markdown_v2(help_message_en + "\n\n" + help_message_it)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def validate_email(email: str) -> bool:
    """Validate the email address to match the format sXXXXXX@studenti.polito.it."""
    email_regex = r'^s\d{6}@studenti\.polito\.it$'
    return re.match(email_regex, email) is not None

def github_invite(email: str) -> bool:
    h = {
    'Content-type': 'application/json',
    'Accept' : 'application/vnd.github.v3+json'
    }
    org = 'cybersecurity-polito'
    username = 'no-mood'
    token = os.environ.get("GH_TOKEN") # This fine-grained token must have the "Members" organization permissions (write)
    team_ALL_id = 10300386 # Adding every member to the "ALL" team

    r = requests.post('https://api.github.com/orgs/' + org + '/invitations', headers=h, json={"email":email, "team_ids":[team_ALL_id]}, auth = (username, token))
    
    time.sleep(1)
    print(r.status_code, r.reason)
    print(r.text)
    if (r.status_code!=201):
        print("Error occurred: " + r.text)
        return False
    return True
        

async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if the user message is a valid email address."""    
    email = ' '.join(context.args)
    if validate_email(email):
        if github_invite(email):
           await update.message.reply_text("Invitation sent to " + email + ".")
           await update.message.reply_text("Please check your email or https://github.com/orgs/cybersecurity-polito/invitation to accept the invitation.")
        else:
           await update.message.reply_text("Error sending invitation to " + email + ".\nPlease contact the administrator.")        
    else:
       await update.message.reply_text("Email address is invalid. Format:\n/invite sXXXXXX@studenti.polito.it")

async def error_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the error message."""
    await update.message.reply_text("Invalid command. Please use /help for more information.")

def setup_handlers(application):
    """Setup the command and message handlers."""
    application.add_handler(CommandHandler("start", help_command)) # Using help_command instead of start
    application.add_handler(CommandHandler("invite", invite_command))
    application.add_handler(CommandHandler("help", help_command))
    #application.add_handler(CommandHandler(filters.COMMAND, help_command))
    
    # on non command i.e message - check the email on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, error_command))

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get("TG_TOKEN")
    application = Application.builder().token(token).build()

    # Setup handlers
    setup_handlers(application)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()