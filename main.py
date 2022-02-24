import logging
import os
import signal
from dotenv import load_dotenv

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handerls import *


def receive_signal(signal_number, frame):
  pass


if __name__ == "__main__":
  signal.signal(signal.SIGHUP, receive_signal)
  load_dotenv()
  create_files_if_not_exist()

  updater = Updater(token=os.getenv('TELEGRAM_BOT_API_TOKEN'), use_context=True)
  dispatcher = updater.dispatcher
  logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

  start_handler = CommandHandler("start", start)
  rebase_handler = CommandHandler("rebase", rebase)
  set_handler = CommandHandler("set", set_adding)
  print_handler = CommandHandler("print", print_all)
  print_counter_handler = CommandHandler("printcounter", print_counter)
  add_handler = CommandHandler("add", add)
  remove_handler = CommandHandler("remove", remove)
  switch_handler = CommandHandler("switch", switch)
  help_handler = CommandHandler("help", help_text)
  message_handler = MessageHandler(Filters.text, message)

  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(rebase_handler)
  dispatcher.add_handler(set_handler)
  dispatcher.add_handler(print_handler)
  dispatcher.add_handler(print_counter_handler)
  dispatcher.add_handler(add_handler)
  dispatcher.add_handler(remove_handler)
  dispatcher.add_handler(switch_handler)
  dispatcher.add_handler(help_handler)
  dispatcher.add_handler(message_handler)

  updater.start_polling()
  updater.idle()
