from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hlink
from glQiwiApi import QiwiWrapper
from glQiwiApi.types import Bill

from tgbot.keyboards.inline import buy_keyboard, paid_keyboard
from tgbot.misc.items import items


def register_pay_for_item(dp: Dispatcher):
    dp.register_message_handler(show_items, Command("items"))
    dp.register_callback_query_handler(create_invoice, text_contains="buy")
    dp.register_callback_query_handler(cancel_payment, text="cancel", state="qiwi")
    dp.register_callback_query_handler(approve_payment, text="paid", state="qiwi")


async def show_items(message: types.Message):
    caption = """
Название продукта: {title}
<i>Описание:</i>
{description}
<u>Цена:</u> {price:.2f} <b>RUB</b>
"""

    for item in items:
        await message.answer_photo(
            photo=item.photo_link,
            caption=caption.format(
                title=item.title,
                description=item.description,
                price=item.price,
            ),
            reply_markup=buy_keyboard(item_id=item.id)
        )


async def create_invoice(call: types.CallbackQuery, state: FSMContext, qiwi_client: QiwiWrapper):
    await call.answer(cache_time=60)
    item_id = call.data.split(":")[-1]
    item_id = int(item_id) - 1
    item = items[item_id]

    amount = item.price
    bill = await qiwi_client.create_p2p_bill(amount=amount)

    await call.message.answer(
        f"Перейдите по ссылке: {hlink('тык', bill.pay_url)} и оплатите счёт",
        reply_markup=paid_keyboard)

    await state.set_state("qiwi")
    await state.update_data(bill=bill)


async def cancel_payment(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Отменено")
    await state.finish()


async def approve_payment(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bill: Bill = data.get("bill")
    is_paid = await bill.check()
    if not is_paid:
        return await call.answer("Вы не оплатили счёт.", show_alert=True, cache_time=5)
    await call.message.answer("Успешно оплачено")
    await call.message.edit_reply_markup()
    await state.finish()
