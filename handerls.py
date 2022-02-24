from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import CallbackContext

from file_manager import *
from utils import send, counter_to_string, get_current_counter_from_update


def start(update, context):
  """
  Sends welcome message
  :param update:
  :param context:
  """
  send(update, context, "This is a german bot. If you don't speak german, don't use it!", )
  send(update, context, "An alle anderen: Schön dich kennenzulernen.\nIch bin der DiffCounter Bot.", )
  send(update, context, "Ein letzter Hinweis: Dieser Bot ist privat betrieben. Du solltest ihn nicht verwenden. Alles weitere läuft auf eigene Gefahr!", )


def rebase(update: Update, context: CallbackContext):
  counter = get_current_counter_from_update(update, context)
  if counter is None:
    return
  try:
    new_value = float(update.message.text[7:].replace(',', '.'))
  except ValueError:
    send(update, context, "Du musst auch schon eine Zahl zum setzen angeben")
    return
  counter[SHOULD] = new_value
  set_counter(counter)
  send(update, context, f"{SHOULD} wurde aktualisiert")


def set_adding(update: Update, context: CallbackContext):
  counter = get_current_counter_from_update(update, context)
  if counter is None:
    return
  try:
    new_adds = [*map(lambda val: float(val), update.message.text[5:].split(' '))]
  except ValueError:
    send(update, context, "Mind. ein Wert ist keine Zahl")
    return
  if len(new_adds) < 7:
    send(update, context, "Du musst für alle 7 Tage eine Wert eingaben (From: <Mo> <Di> …)")
    return
  counter[MONDAY] = new_adds[0]
  counter[TUESDAY] = new_adds[1]
  counter[WEDNESDAY] = new_adds[2]
  counter[THURSDAY] = new_adds[3]
  counter[FRIDAY] = new_adds[4]
  counter[SATURDAY] = new_adds[5]
  counter[SUNDAY] = new_adds[6]
  counter[LAST_UPDATE] = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
  set_counter(counter)
  send(update, context, "Der Counter wurde aktualisiert")


def print_all(update: Update, context: CallbackContext):
  counter = get_current_counter_from_update(update, context)
  if counter is None:
    return
  counter = update_should(counter)
  if counter is None:
    send(update, context, f"Beim Aktualisieren des {SHOULD}s ist etwas schiefgelaufen.")
  send(update, context, counter_to_string(counter))


def print_counter(update: Update, context: CallbackContext):
  chat_id = update.effective_chat.id
  counters = get_counter_of_chat(chat_id)
  ret = "*Name: id*\n"
  for name, counter_id in zip(counters.keys(), counters.values()):
    ret += f"{name}: {counter_id}\n"
  send(update, context, ret)


def add(update: Update, context: CallbackContext):
  new_counter = dict()
  name = update.message.text[5:]
  if len(name) <= 0:
    send(update, context, "Du solltest deinem Counter einen Namen geben")
    return
  new_counter[CHAT_ID] = update.effective_chat.id
  new_counter[COUNTER_ID] = None
  new_counter[CURRENT] = 0
  new_counter[FRIDAY] = 0
  new_counter[MONDAY] = 0
  new_counter[NAME] = name
  new_counter[SATURDAY] = 0
  new_counter[SHOULD] = 0
  new_counter[SUNDAY] = 0
  new_counter[THURSDAY] = 0
  new_counter[TUESDAY] = 0
  new_counter[WEDNESDAY] = 0
  new_counter[LAST_UPDATE] = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

  new_counter = set_counter(new_counter)
  send(update, context, f"Dein neuer Counter _{new_counter[NAME]}_ wurde erfolgreich erstellt. Seine ID lautet `{new_counter[COUNTER_ID]}`")
  send(update, context, "So sieht dein neuer Counter aktuell aus:\n" + counter_to_string(new_counter))
  if not set_current_counter_id(new_counter[CHAT_ID], new_counter[COUNTER_ID]):
    send(update, context, "Ich habe versucht für dich zu deinem neuen Counter zu wechseln. Dabei ist aber wohl etwas schief gegangen. Tut mir leid, probiere es am Besten einmal selbst.")
    return
  send(update, context, "Ich habe für dich zu deinem neuen Counter gewechselt.")


def remove(update: Update, context: CallbackContext):
  try:
    counter_id = int(update.message.text[7:])
  except ValueError:
    send(update, context, "Das ist keine ID")
  if not delete_counter(update.effective_chat.id, counter_id):
    send(update, context, "Du hast keinen Counter mit dieser ID")
  send(update, context, "Dein Counter wurde gelöscht")


def switch(update: Update, context: CallbackContext):
  try:
    next_counter = int(update.message.text[7:])
  except ValueError:
    send(update, context, "Das ist keine ID")
    return
  if not set_current_counter_id(update.effective_chat.id, next_counter):
    send(update, context, "Scheinbar hast du gar keinen Counter mit dieser ID.")
    return
  send(update, context, "Der Counter wurde erfolgreich gewechselt.")


def help_text(update: Update, context: CallbackContext):
  send(update, context,
       "Wenn du einen Text, ohne Kommando, schickst, wird dieser Wert auf den Istwert addiert. Für die Logs kannst du die Endzeit (und das Enddatum setzen )setzen mit `ZeitZumAddieren [HH:MM [DD.MM[.YYYY]]]`")


def message(update: Update, context: CallbackContext):
  counter = get_current_counter_from_update(update, context)
  if counter is None:
    return

  try:
    split_text = update.message.text.split(' ')
    add_value = float(split_text[0].replace(',', '.'))
  except ValueError:
    send(update, context, 'Du musst eine Zahl angeben')
    return

  root_time = datetime.datetime.now()
  if len(split_text) > 1:
    try:
      time_array = split_text[1].split(':')
      root_time = root_time.replace(hour=int(time_array[0]), minute=int(time_array[1]))
      if len(split_text) > 2:
        try:
          date_array = split_text[2].split('.')
          new_year = root_time.year
          if len(date_array) > 2:
            new_year = date_array[2]
          root_time = root_time.replace(day=int(date_array[0]), month=int(date_array[1]), year=int(new_year))
        except ValueError:
          send(update, context, 'Das angegebene Datum muss die Form `DD.MM` oder `DD.MM.YYYY` haben. Eine Angabe war keine Zahl.')
          return
        except IndexError:
          send(update, context, 'Das angegebene Datum muss die Form `DD.MM` oder `DD.MM.YYYY` haben. Eine Angabe Fehlt.')
          return
    except ValueError:
      send(update, context, 'Die angegebene Zeit muss die Form `HH:MM` haben. Eine Angabe war keine Zahl.')
      return
    except IndexError:
      send(update, context, 'Die angegebene Zeit muss die Form `HH:MM` haben. Eine Angabe Fehlt.')
      return

  log = pd.read_csv(f'logs/{counter[CHAT_ID]}_{counter[COUNTER_ID]}.csv', sep=';', decimal=',')
  # day = (root_time - timedelta(hours=add_value)).date().isoformat()
  if add_value < 6:
    counter[CURRENT] += add_value
    log.loc[len(log.index)] = [(root_time - timedelta(hours=add_value)).isoformat(), root_time.isoformat(), add_value]
  else:
    before_pause = (None, None)
    if add_value < 9:
      before_pause = (4., 4.5)
    else:
      before_pause = (5, 5.75)
    counter[CURRENT] += add_value - (before_pause[1] - before_pause[0])
    # add before_pause
    log.loc[len(log.index)] = [(root_time - timedelta(hours=add_value)).isoformat(), (root_time - timedelta(hours=add_value - before_pause[0])).isoformat(),
                               before_pause[0]]
    # add rest
    log.loc[len(log.index)] = [(root_time - timedelta(hours=add_value - before_pause[1])).isoformat(), root_time.isoformat(), add_value - before_pause[1]]

  if not set_counter(counter):
    send(update, context, "Beim Speichern ist ein Fehler aufgetreten")
    return
  log.to_csv(f'logs/{counter[CHAT_ID]}_{counter[COUNTER_ID]}.csv', index=False, sep=';', decimal=',')
  send(update, context, f"{CURRENT} wurde aktualisiert")
