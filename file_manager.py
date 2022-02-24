import datetime
import json
from os.path import exists

import pandas as pd
from dateutil import parser

from constances import *


def create_files_if_not_exist() -> None:
  """
  Creates an empty csv file with all needed columns  if no files with its name exists
  """
  if not exists(COUNTER_FILE):
    counter_file = open(COUNTER_FILE, 'w')
    counter_file.write(f'{CHAT_ID};{COUNTER_ID};{NAME};{SHOULD};{CURRENT};{MONDAY};{TUESDAY};{WEDNESDAY};{THURSDAY};{FRIDAY};{SATURDAY};{SUNDAY};{LAST_UPDATE}')
    counter_file.close()
  if not exists(CURRENT_COUNTER_IDS):
    counter_ids_file = open(CURRENT_COUNTER_IDS, 'w')
    empty_dict = dict()
    counter_ids_file.write(str(json.dumps(empty_dict)))
    counter_ids_file.close()


def get_counter(chat_id: int, counter_id: int) -> dict:
  """
  searches a counter by its id and validates with chat_id
  :param chat_id: telegram chat_id
  :param counter_id: internal counter_id
  :return: None if no matching counter found, else the counter
  """
  counters = pd.read_csv(COUNTER_FILE, sep=';', decimal=',')
  counters = counters[counters[CHAT_ID] == chat_id]
  counters = counters[counters[COUNTER_ID] == counter_id]
  if len(counters) == 0:
    return None
  return counters.iloc[0].to_dict()


def get_counter_of_chat(chat_id: int) -> dict:
  """
  dict with all counters of a chat
  :param chat_id:
  :return: [COUNTER_ID] = NAME
  """
  counters = pd.read_csv(COUNTER_FILE, sep=';', decimal=',')
  counters = counters[counters[CHAT_ID] == chat_id]
  ret = dict()
  for i, counter in counters.iterrows():
    ret[counter[NAME]] = counter[COUNTER_ID]
  return ret


def set_counter(counter: dict) -> dict:
  """
  (over) writes a counter with the given ID as the given counter
  :param counter: the new counter
  :return: the written counter
  """
  counters = pd.read_csv(COUNTER_FILE, sep=';', decimal=',')
  if counter[COUNTER_ID] is None:
    new_id = 0
    while len(counters[counters[COUNTER_ID] == new_id]) > 0 or exists(f'logs/{counter[CHAT_ID]}_{new_id}.csv'):
      new_id += 1
    counter[COUNTER_ID] = new_id
    log_file = open(f'logs/{counter[CHAT_ID]}_{new_id}.csv', 'w')
    log_file.write(f'{START_TIME};{END_TIME};{DURATION}')
    log_file.close()
  else:
    counters = counters[counters[COUNTER_ID] != counter[COUNTER_ID]]

  counters = counters.append(counter, ignore_index=True)
  counters.to_csv(COUNTER_FILE, index=False, sep=';', decimal=',')
  return counter


def delete_counter(chat_id: int, counter_id: int) -> bool:
  """
  deletes a counter with given ID
  :param counter_id:
  :return: True, if deletion was successful, else False
  """
  if get_counter(chat_id, counter_id) is None:
    return None
  try:
    counters = pd.read_csv(COUNTER_FILE, sep=';', decimal=',')
    counters = counters.drop(counters[counters[COUNTER_ID] == counter_id].index[0])
    counters.to_csv(COUNTER_FILE, index=False, sep=';', decimal=',')
  except IndexError:
    return False
  else:
    return True


def get_current_counter_id(chat_id: int) -> int:
  """
  Returns the current chosen counter_id of the chat
  :param chat_id:
  :return: None, if there's no active counter for this chat
  """
  try:
    with open(CURRENT_COUNTER_IDS, 'r') as json_file:
      current_counter_ids = json.load(json_file)
      return current_counter_ids[str(chat_id)]
  except KeyError:
    return None


def set_current_counter_id(chat_id: int, counter_id: int) -> bool:
  """
  Setts the current chosen counter_id of the chat
  :param chat_id:
  :param counter_id:
  :return: True, if counter_id is matching with chat_id and setting was successful, else False
  """
  if get_counter(chat_id, counter_id) is None:
    return False
  json_file = open(CURRENT_COUNTER_IDS, 'r')
  current_counter_ids = json.load(json_file)
  json_file.close()
  json_file = open(CURRENT_COUNTER_IDS, 'w')
  current_counter_ids[chat_id] = counter_id
  json.dump(current_counter_ids, json_file)
  json_file.close()
  return True


def update_should(counter: dict) -> dict:
  last_update = parser.parse(counter[LAST_UPDATE])
  now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  if last_update < now:
    while last_update < now:
      last_update += datetime.timedelta(days=1)
      day = last_update.weekday()
      if day == 0:
        summand = counter[MONDAY]
      elif day == 1:
        summand = counter[TUESDAY]
      elif day == 2:
        summand = counter[WEDNESDAY]
      elif day == 3:
        summand = counter[THURSDAY]
      elif day == 4:
        summand = counter[FRIDAY]
      elif day == 5:
        summand = counter[SATURDAY]
      elif day == 6:
        summand = counter[SUNDAY]
      counter[SHOULD] += summand

    counter[LAST_UPDATE] = last_update.isoformat()
    if not set_counter(counter):
      return None
  return counter
