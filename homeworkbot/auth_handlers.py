#auth_hendlers.py
from telebot.apihelper import ApiTelegramException
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from homeworkbot.configuration import bot

import database.main_db.common_crud as common_crud
import database.main_db.student_crud as student_crud
from database.main_db.common_crud import UserEnum


class AuthStates(StatesGroup):
    full_name = State()


async def is_subscribed(chat_id: int, user_id: int) -> bool:
    try:
        response = await bot.get_chat_member(chat_id, user_id)
        if response.status == 'left':
            return False
        else:
            return True
    except ApiTelegramException as ex:
        if ex.result_json['description'] == 'Bad Request: user not found':
            return False


@bot.message_handler(commands=['start'])
async def handle_start(message: Message):
    user = common_crud.user_verification(message.from_user.id)
    match user:
        case UserEnum.Admin:
            await bot.send_message(
                message.chat.id,
                '<b>О, мой повелитель! Бот готов издеваться над студентами!!!</b>',
                parse_mode='HTML',
                # TODO: клавиатура
            )
        case UserEnum.Teacher:
            await bot.send_message(
                message.chat.id,
                'Приветствую! Надеюсь, что в этом году студенты вас не разочаруют!',
                parse_mode='HTML',
                # TODO: клавиатура
            )
        case UserEnum.Student:
            await bot.send_message(
                message.chat.id,
                'С возвращением! О, юнный падаван ;)',
                parse_mode='HTML',
                # TODO: клавиатура
            )
        case _:
            chats = common_crud.get_chats()
            user_in_chat = False
            for chat_id in chats:
                user_in_chat = await is_subscribed(chat_id, message.from_user.id)
                if user_in_chat:
                    break

            if user_in_chat:
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton('Да', callback_data='start_yes'),
                    InlineKeyboardButton('Нет', callback_data='start_no'),
                )

                text = 'Бот осуществляет хранение и обработку персональных данных '
                text += 'на российских серверах. К таким данным относятся: \n'
                text += '- ФИО\n'
                text += '- Успеваемость по предмету\n'
                text += 'Telegram ID\n'
                text += 'Вы даете разрешение на хранение и обработку своих персональных данных?'
                await bot.send_message(
                    message.chat.id,
                    text,
                    reply_markup=markup,
                )
            else:
                await bot.send_message(
                    message.chat.id,
                    'Пожалуйста, подпишитесь на канал!!!',
                )


@bot.callback_query_handler(func=lambda call: 'start_' in call.data)
async def callback_auth_query(call: CallbackQuery):
    type_callback = call.data.split('_')[0]
    match type_callback:
        case 'start':
            if call.data == 'start_yes':
                text = 'Спасибо! Удачной учебы!\n'
                text += 'Для вашей идентификации введите ФИО:'
                await bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.id,
                )
                await bot.set_state(
                    call.from_user.id, AuthStates.full_name, call.message.chat.id
                )
            if call.data == 'start_no':
                await bot.edit_message_text(
                    'Жаль! Если передумаете - перезапустите бота!',
                    call.message.chat.id,
                    call.message.id,
                )
        case _:
            await bot.edit_message_text(
                'Неизвестный формат для обработки данных!',
                call.message.chat.id,
                call.message.id,
            )


@bot.message_handler(state=AuthStates.full_name)
async def input_full_name(message: Message):
    full_name = message.text
    if len(full_name.split(' ')) != 3:
        await bot.send_message(
            message.chat.id,
            'Пожалуйста, введите полное ФИО! Например: Иванов Иван Иванович'
        )
    else:
        if student_crud.has_student(full_name):
            student_crud.set_telegram_id(full_name, message.from_user.id)
            await bot.send_message(
                message.chat.id,
                'Поздравляю! Вы успешно авторизовались!',
                # TODO: клавиатура
            )
            await bot.delete_state(message.from_user.id, message.chat.id)
        else:
            await bot.send_message(
                message.chat.id,
                'Пожалуйста, проверьте корректность ввода ФИО или свяжитесь с преподавателем'
            )
