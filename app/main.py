import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from mongo_database import createNewPeer, getAllUserPeers, deletePeer, getFilePeer, updatePeer, ping_server
from instruction import text_instruction

load_dotenv()

API_TOKEN = '5653584102:AAGb6Iuj_BzN_WPvbH-z31bBUqXjtta9F3Q'
PAYMENTS_TOKEN = os.environ.get("PAYMENTS_TOKEN")
PRICE_RUB = int(os.environ.get("PRICE_RUB"))
PRICE = types.LabeledPrice(label="Оплата", amount=100*PRICE_RUB)


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


#Buttons
generalMenu = types.InlineKeyboardButton("🏠 Главное меню", callback_data='generalMenu')
addDevice = types.InlineKeyboardButton("➕ Добавить новое устройство", callback_data='addDevice')
myDevices = types.InlineKeyboardButton("📱 Мои устройства", callback_data="myDevices")
payment = types.InlineKeyboardButton("💳 Пополнить счет", callback_data="payment")
instruction = types.InlineKeyboardButton("📄 Инструкция", callback_data="instruction")


async def listPeers(telegramID):
    peersAll = getAllUserPeers(telegramID=telegramID)
    buttons = []
    for peer in peersAll:
        if peer['enabled'] == True:
            indicator = "\u2705"
        else:
            indicator = "\u274c"
        buttons.append(types.InlineKeyboardButton(f" {indicator} {peer['name']}", callback_data="Удалить"))
        buttons.append(types.InlineKeyboardButton("Скачать", callback_data="get, " + peer['ids']))
        buttons.append(types.InlineKeyboardButton("Удалить", callback_data="del " + peer['ids']))
        buttons.append(types.InlineKeyboardButton("Оплатить", callback_data="payments " + peer['ids'] + f" {peer['name']}"))
    return buttons


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    inMurkup = types.InlineKeyboardMarkup(row_width=1)
    inMurkup.add(addDevice, myDevices, payment, instruction)
    await message.answer(f"Привет, {message.from_user.first_name}.", reply_markup=inMurkup)


@dp.callback_query_handler()
async def callback_query_handler(call: types.CallbackQuery):
    if call.data == "addDevice":
        print("addDevice")
        await call.message.reply(text=f"Поиск ближайшего сервера")
        await call.message.reply(text=createNewPeer(call.from_user.id))
        buttons = await listPeers(telegramID=call.from_user.id)
        if buttons == []:
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            inMurkup.add(addDevice, generalMenu)
            await call.message.answer(text=f"Список пуст", reply_markup=inMurkup)
            await bot.answer_callback_query(callback_query_id=call.id)
        else:
            inMurkup = types.InlineKeyboardMarkup(row_width=4)
            inMurkup.add(*buttons, generalMenu)
            await call.message.answer(text=f"📱 Список устройств:", reply_markup=inMurkup)
            await bot.answer_callback_query(callback_query_id=call.id)

    if call.data == "myDevices":
        print("myDevices")
        buttons = await listPeers(telegramID=call.from_user.id)
        if buttons == []:
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            inMurkup.add(addDevice, generalMenu)
            await call.message.answer(text=f"Список пуст", reply_markup=inMurkup)
            await bot.answer_callback_query(callback_query_id=call.id)
        else:
            inMurkup = types.InlineKeyboardMarkup(row_width=4)
            inMurkup.add(*buttons, generalMenu)
            await call.message.answer(text=f"📱 Список устройств:", reply_markup=inMurkup)
            await bot.answer_callback_query(callback_query_id=call.id)

    if call.data.startswith("del"):
        print("del")
        await call.message.reply(text=deletePeer(ids=call.data.split()[1]))
        buttons = await listPeers(telegramID=call.from_user.id)
        if buttons == []:
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            inMurkup.add(addDevice, generalMenu)
            await call.message.answer(text=f"Список пуст", reply_markup=inMurkup)
            await bot.answer_callback_query(callback_query_id=call.id)
        else:
            inMurkup = types.InlineKeyboardMarkup(row_width=4)
            inMurkup.add(*buttons, generalMenu)
            await call.message.answer(text=f"📱 Список устройств:", reply_markup=inMurkup)
            await bot.answer_callback_query(callback_query_id=call.id)

    if call.data.startswith("get"):
        file, filename = getFilePeer(ids=call.data.split()[1])
        await bot.send_document(call.from_user.id, (f"{filename}.conf", file))
        await bot.answer_callback_query(callback_query_id=call.id)

    if call.data.startswith("generalMenu"):
        print("generalMenu")
        inMurkup = types.InlineKeyboardMarkup(row_width=1)
        inMurkup.add(addDevice, myDevices, payment, instruction)
        await call.message.answer(text=f"🏠 Главное меню:", reply_markup=inMurkup)
        await bot.answer_callback_query(callback_query_id=call.id)


    if call.data.startswith("instruction"):
        inMurkup = types.InlineKeyboardMarkup(row_width=1)
        inMurkup.add(generalMenu)
        text = text_instruction()
        await call.message.answer(text=text, reply_markup=inMurkup, parse_mode='HTML')
        await bot.answer_callback_query(callback_query_id=call.id)

    if call.data.startswith("payments"):
        print(call.data.split())
        if ping_server(call.data.split()[1]) == True:
            await bot.send_invoice(call.message.chat.id,
                             title="Оплата услуг VPN-сервиса",
                             description=f"Устройство: {call.data.split()[2]}",
                             provider_token=PAYMENTS_TOKEN,
                             currency="rub",
                             is_flexible=False,
                             prices=[PRICE],
                             start_parameter="test_bot",
                             payload=f"{call.data.split()[1]}",
                             )
            await bot.answer_callback_query(callback_query_id=call.id)
        else:
            await call.message.reply(text="Сервер временно не доступен", parse_mode='HTML')
            await bot.answer_callback_query(callback_query_id=call.id)


@dp.shipping_query_handler()
async def shipping(shipping_query: types.shipping_query):
    await bot.answer_shipping_query(shipping_query.id, ok=True,
                              error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@dp.pre_checkout_query_handler()
async def checkout(pre_checkout_query: types.pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@dp.message_handler(content_types=['successful_payment'])
async def got_payment(message: types.Message):
    print(message.successful_payment.invoice_payload)
    peer = updatePeer(ids=message.successful_payment.invoice_payload, status=True)
    print('Оплата прошла успешно!\n')
    inMurkup = types.InlineKeyboardMarkup(row_width=1)
    inMurkup.add(addDevice, myDevices, payment, instruction)
    await bot.send_message(message.chat.id,
                     f'Оплата прошла успешно!\n'
                     f'Сумма {message.successful_payment.total_amount / 100} {message.successful_payment.currency}\n'
                     f"Устройство: {peer['name']}",
                     parse_mode='Markdown', reply_markup=inMurkup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)