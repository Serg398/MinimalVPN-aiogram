import logging
import os
import time
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from mongo_database import createNewPeer, getAllUserPeers, deletePeer, getFilePeer, updatePeer, ping_server
from instruction import text_instruction


print("Initialize services..")


load_dotenv()

API_TOKEN_BOT = os.environ.get("API_TOKEN_BOT")
PAYMENTS_TOKEN = os.environ.get("PAYMENTS_TOKEN")
PRICE_RUB = int(os.environ.get("PRICE_RUB"))
PRICE = types.LabeledPrice(label="Оплата", amount=100 * PRICE_RUB)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN_BOT)
dp = Dispatcher(bot)

# Buttons
generalMenu = types.InlineKeyboardButton("🏠 Главное меню", callback_data='generalMenu')
addDevice = types.InlineKeyboardButton("➕ Добавить новое устройство", callback_data='addDevice')
myDevices = types.InlineKeyboardButton("📱 Управление устройствами", callback_data="myDevices")
payment = types.InlineKeyboardButton("💳 Пополнить счет", callback_data="payment")
instruction = types.InlineKeyboardButton("📄 Инструкция", callback_data="instruction")

print("Start bot..")


async def listPeers(telegramID):
    peersAll = await getAllUserPeers(telegramID=telegramID)
    buttons = []
    for peer in peersAll:
        if peer['enabled'] == True:
            indicator = "\u2705"
        else:
            indicator = "\u274c"
        buttons.append(types.InlineKeyboardButton(f" {indicator} {peer['name']}", callback_data="Удалить"))
        buttons.append(types.InlineKeyboardButton("Скачать", callback_data="get, " + peer['ids']))
        buttons.append(types.InlineKeyboardButton("Удалить", callback_data="del " + peer['ids']))
        buttons.append(
            types.InlineKeyboardButton("Оплатить", callback_data="payments " + peer['ids'] + f" {peer['name']}"))
    return buttons


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    inMurkup = types.InlineKeyboardMarkup(row_width=1)
    inMurkup.add(myDevices, instruction)
    await message.answer(f"Привет, {message.from_user.first_name}.", reply_markup=inMurkup)


@dp.callback_query_handler()
async def callback_query_handler(call: types.CallbackQuery):
    if call.data == "addDevice":
        await call.message.answer(text=f"Поиск ближайшего сервера")
        text = await createNewPeer(call.from_user.id)
        await call.message.answer(text=text)
        buttons = await listPeers(telegramID=call.from_user.id)
        if buttons == []:
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            inMurkup.add(addDevice, generalMenu)
            await call.message.answer(text=f"Список пуст", reply_markup=inMurkup)
            await bot.answer_callback_query(call.id)
        else:
            inMurkup = types.InlineKeyboardMarkup(row_width=4)
            inMurkup.add(*buttons, addDevice)
            inMurkup.add(generalMenu)
            await call.message.answer(text=f"📱 Список устройств:", reply_markup=inMurkup)
            await bot.answer_callback_query(call.id)

    if call.data == "myDevices":
        buttons = await listPeers(telegramID=call.from_user.id)
        if buttons == []:
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            inMurkup.add(addDevice, generalMenu)
            await call.message.answer(text=f"Список пуст", reply_markup=inMurkup)
            await bot.answer_callback_query(call.id)
        else:
            inMurkup = types.InlineKeyboardMarkup(row_width=4)
            inMurkup.add(*buttons, addDevice)
            inMurkup.add(generalMenu)
            await call.message.answer(text=f"📱 Список устройств:", reply_markup=inMurkup)
            await bot.answer_callback_query(call.id)

    if call.data.startswith("del"):
        text = await deletePeer(ids=call.data.split()[1])
        await call.message.answer(text=text)
        buttons = await listPeers(telegramID=call.from_user.id)
        if buttons == []:
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            inMurkup.add(addDevice)
            inMurkup.add(generalMenu)
            await call.message.answer(text=f"Список пуст", reply_markup=inMurkup)
            await bot.answer_callback_query(call.id)
        else:
            inMurkup = types.InlineKeyboardMarkup(row_width=4)
            inMurkup.add(*buttons)
            inMurkup.add(addDevice)
            inMurkup.add(generalMenu)
            await call.message.answer(text=f"📱 Список устройств:", reply_markup=inMurkup)
            await bot.answer_callback_query(call.id)

    if call.data.startswith("get"):
        print('get')
        file, filename = await getFilePeer(ids=call.data.split()[1])
        await bot.send_document(call.from_user.id, (f"{filename}.conf", file))
        await bot.answer_callback_query(call.id)

    if call.data.startswith("generalMenu"):
        inMurkup = types.InlineKeyboardMarkup(row_width=1)
        inMurkup.add(myDevices, instruction)
        await call.message.answer(text=f"🏠 Главное меню:", reply_markup=inMurkup)
        await bot.answer_callback_query(call.id)

    if call.data.startswith("instruction"):
        inMurkup = types.InlineKeyboardMarkup(row_width=1)
        inMurkup.add(myDevices, generalMenu)
        text = await text_instruction()
        await call.message.answer(text=text, reply_markup=inMurkup, parse_mode='HTML')
        await bot.answer_callback_query(call.id)

    if call.data.startswith("payments"):
        if await ping_server(call.data.split()[1]) == True:
            await bot.send_invoice(call.message.chat.id,
                                   title="Оплата услуг VPN-сервиса",
                                   description=f"Устройство: {call.data.split()[2]}",
                                   provider_token=PAYMENTS_TOKEN,
                                   need_email=True,
                                   send_email_to_provider=True,
                                   currency="rub",
                                   is_flexible=False,
                                   prices=[PRICE],
                                   provider_data={
                                       "receipt": {
                                           "items": [
                                               {
                                                   "description": f"{call.data.split()[2]}",
                                                   "quantity": "1.00",
                                                   "amount": {
                                                       "value": "120.00",
                                                       "currency": "RUB"
                                                   },
                                                   "vat_code": 1
                                               }
                                           ]
                                       }
                                   },
                                   start_parameter="test",
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
    inMurkup = types.InlineKeyboardMarkup(row_width=1)
    inMurkup.add(addDevice, myDevices, payment, instruction)
    peer = await updatePeer(ids=message.successful_payment.invoice_payload, status=True)
    await bot.send_message(-917478475,
                           f'*ID:* {message.chat.id}\n'
                           f'*USER:* {message.from_user.first_name}, {message.from_user.last_name}, @{message.from_user.username}\n\n'
                           f'*Оплата прошла успешно!*\n\n'
                           f'*Сумма:* {message.successful_payment.total_amount / 100} {message.successful_payment.currency}\n'
                           f"*Устройство:* {peer['name']}\n"
                           f"*ID peer:* {peer['ids']}\n"
                           f"*ID провайдера:* {message.successful_payment.provider_payment_charge_id}\n"
                           f"*Активен до:* {time.strftime('%Y-%m-%d', time.localtime(peer['disableDate']))}",
                           parse_mode='Markdown')

    await bot.send_message(message.chat.id,
                           f'*Оплата прошла успешно!*\n\n'
                           f'*Сумма:* {message.successful_payment.total_amount / 100} {message.successful_payment.currency}\n'
                           f"*Устройство:* {peer['name']}\n"
                           f"*Активен до:* {time.strftime('%Y-%m-%d', time.localtime(peer['disableDate']))}",
                           parse_mode='Markdown', reply_markup=inMurkup)


if __name__ == '__main__':
    executor.start_polling(dp)
