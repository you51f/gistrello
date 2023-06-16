import logging
from telegram.ext import *
import requests
from aiogram import types, Bot, Dispatcher, executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from localStoragePy import localStoragePy


# Configurations
API_KEY = "5993779778:AAGJarQegqyvDpKrizpJKUP5k4yXP-_XSU4"

Trello_API_KEY = "a826ed46adf751059a0fa055d4fa84b6"
Trello_Token = "ATTAcdc839c19e3f66b7ffe5e49d6678e501572cc50847da0254e60ed10e771fa4f04EA5C9CF"

bot = Bot(token=API_KEY)
dp = Dispatcher(bot)


# Static Buttons
addboard = InlineKeyboardButton(text='Add Board', callback_data='add_board')
editboard = InlineKeyboardButton(text='Edit Board', callback_data='edit_board')
board_key_board_inline = InlineKeyboardMarkup().add(addboard, editboard)

# Global variables
operation = "cancel"
boardId = ""
listId = ""

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('Starting Bot...')


# Boards handler
@dp.message_handler(commands=['boards'])
async def boards_command(message: types.Message):
    boards = "Boards:"
    response = requests.get(
        f'https://api.trello.com/1/members/me/boards?fields=name,url&key={Trello_API_KEY}&token={Trello_Token}').json()
    for board in response:
        boards += f'\n- {board["name"]}'
    await message.reply(boards, reply_markup=board_key_board_inline)
    # print(boards)


# Create cards handler
@dp.message_handler(commands=['new'])
async def cards_command(message: types.Message):
    global operation
    operation = "choose_board"
    board_key_board_inline = InlineKeyboardMarkup()
    # print(x)
    response = requests.get(
        f'https://api.trello.com/1/members/me/boards?fields=name,url&key={Trello_API_KEY}&token={Trello_Token}').json()
    for board in response:
        board_btns = InlineKeyboardButton(text=f'{board["name"]}', callback_data=f'{board["id"]}')
        board_key_board_inline.add(board_btns)
    await message.answer("Choose a board:", reply_markup=board_key_board_inline)


# Cancel handler
@dp.message_handler(commands=['cancel'])
async def boards_command(message: types.Message):
    global operation
    global boardId
    global listId
    operation = "cancel"
    boardId = ""
    listId = ""
    await message.reply('Operation is canceled use the menu for more options')


# Search handler
@dp.message_handler(commands=['search'])
async def boards_command(message: types.Message):
    global operation
    # operation = "search_card_by_name"
    searchBtn1 = InlineKeyboardButton(text='Board name', callback_data='board_name')
    searchbtn2 = InlineKeyboardButton(text='Card name', callback_data='card_name')
    search_key_board_inline = InlineKeyboardMarkup().add(searchBtn1, searchbtn2)
    await message.answer("Search cards by:", reply_markup=search_key_board_inline)
    # await message.answer("Search cards by name or board name:")


# Callback handlers
@dp.callback_query_handler(types.CallbackQuery)
async def action_in_board(call: types.CallbackQuery):
    global operation
    global boardId
    global listId
    if call.data == "add_board":
        operation = "add_board"
        await call.message.answer("Enter the New board name:")
    if call.data == "edit_board":
        operation = "edit_board"
        edit_board_key_board_inline = InlineKeyboardMarkup()
        # print(x)
        response = requests.get(
            f'https://api.trello.com/1/members/me/boards?fields=name,url&key={Trello_API_KEY}&token={Trello_Token}').json()
        for board in response:
            edit_newbtn = InlineKeyboardButton(text=f'{board["name"]}', callback_data=f'{board["id"]}')
            edit_board_key_board_inline.add(edit_newbtn)
        await call.message.answer("Choose a board to edit:", reply_markup=edit_board_key_board_inline)
    if call.data == "board_name":
        operation = "search_card_by_board"
        await call.message.answer("Search card by board name:")
    if call.data == "card_name":
        operation = "search_card_by_name"
        await call.message.answer("Search card by card name:")
    else:
        if operation == "edit_board":
            boardId = call.data
            operation = "edit_selected_board"
            await call.message.answer("Enter the new board name:")
        elif operation == "choose_board":
            boardId = call.data
            lists_key_board_inline = InlineKeyboardMarkup()
            response = requests.get(
                f'https://api.trello.com/1/boards/{boardId}/lists?key={Trello_API_KEY}&token={Trello_Token}').json()
            # print(response.status_code)
            # if response.status_code == 200:
            for list in response:
                list_newbtn = InlineKeyboardButton(text=f'{list["name"]}', callback_data=f'{list["id"]}')
                lists_key_board_inline.add(list_newbtn)
            await call.message.answer("Choose a list:", reply_markup=lists_key_board_inline)
            # else:
            #     text = "Somthing went wrong, try again."
            #     await call.message.answer(text)
            operation = "add_card_to_list"
        elif operation == "add_card_to_list":
            listId = call.data
            cards = "Cards:"
            response = requests.get(
                f'https://api.trello.com/1/lists/{listId}/cards?key={Trello_API_KEY}&token={Trello_Token}').json()
            for card in response:
                cards += f'\n- {card["name"]}'
            cards += '\nEnter the new card name:'
            await call.message.answer(cards)

    await call.answer()

# Normal messages handler
@dp.message_handler(types.Message)
async def message_handle(message: types.Message):
    global operation
    global boardId
    global listId
    if operation == "add_board":
        payload = {"name": str(message.text)}
        response = requests.post(
            f'https://api.trello.com/1/boards?fields=name,url&key={Trello_API_KEY}&token={Trello_Token}', data=payload)
        # print(response.status_code)
        if response.status_code == 200:
            text = "Board Added"
        else:
            text = "Somthing went wrong, try again."
        operation = "cancel"
    elif operation == "edit_selected_board":
        response = requests.put(
            f'https://api.trello.com/1/boards/{boardId}?key={Trello_API_KEY}&token={Trello_Token}',
            json={"name": message.text}, headers={"Content-Type": "application/json"})
        # print(response.status_code)
        if response.status_code == 200:
            text = "Board Edited"
        else:
            text = "Somthing went wrong, try again."
        operation = "cancel"
        boardId = ""
    elif operation == "edit_board":
        text = "Edited"
        operation = "cancel"
    elif operation == "add_card_to_list":
        payload = {"name": str(message.text)}
        response = requests.post(
            f'https://api.trello.com/1/cards?idList={listId}&key={Trello_API_KEY}&token={Trello_Token}', data=payload)
        # print(response.status_code)
        if response.status_code == 200:
            text = "Card Added"
        else:
            text = "Somthing went wrong, try again."
        operation = "cancel"
    elif operation == "search_card_by_board":
        text = "Cards from search results:"
        response = requests.get(
            f'https://api.trello.com/1/search?query={message.text}&key={Trello_API_KEY}&token={Trello_Token}').json()

        for board in response["boards"]:
            cardResponse = requests.get(
                f'https://api.trello.com/1/boards/{board["id"]}/cards?key={Trello_API_KEY}&token={Trello_Token}').json()
            for card in cardResponse:
                text += f'\n- {card["name"]}'

        operation = "cancel"
    elif operation == "search_card_by_name":
        text = "Cards from search results:"
        response = requests.get(
            f'https://api.trello.com/1/search?query={message.text}&key={Trello_API_KEY}&token={Trello_Token}').json()
        for card in response["cards"]:
            text += f'\n- {card["name"]}'

        operation = "cancel"
    else:
        text = "Use the menu for more options"
        operation = "cancel"
    await message.answer(text)

# Executor
executor.start_polling(dp)
