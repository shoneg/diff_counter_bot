from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from constances import *
from file_manager import get_current_counter_id, get_counter


def send(update, context, text, reply_markup=None):
  context.bot.send_message(
    chat_id=update.effective_chat.id,
    text=text,
    reply_markup=reply_markup,
    parse_mode=ParseMode.MARKDOWN,
  )


def counter_to_string(counter: dict) -> str:
  return f'*{counter[NAME]}*:\nCounterID: `{counter[COUNTER_ID]}`\n*{SHOULD}: {counter[SHOULD]}*\n*{CURRENT}: {counter[CURRENT]}*\n\n_Standard-Tages-Additionen_:\n\
{MONDAY}: {counter[MONDAY]}\n{TUESDAY}: {counter[TUESDAY]}\n{WEDNESDAY}: {counter[WEDNESDAY]}\n{THURSDAY}: {counter[THURSDAY]}\n{FRIDAY}: {counter[FRIDAY]}\n{SATURDAY}: {counter[SATURDAY]}\n{SUNDAY}: {counter[SUNDAY]}'


def get_current_counter_from_update(update: Update, context: CallbackContext) -> dict:
  chat_id = update.effective_chat.id
  counter_id = get_current_counter_id(chat_id)
  if counter_id is None:
    send(update, context, "Du musst zuerst einen Counter erstellen und auswählen.")
    return None
  counter = get_counter(chat_id, counter_id)
  if counter is None:
    send(update, context, "Scheinbar gibt es deinen aktuell ausgewählten counter nicht mehr, vielleicht hast du ihn gelöscht? Du solltest einen neuen erstellen und auswählen.")
    return None
  return counter
