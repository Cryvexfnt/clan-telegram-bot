import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Токен твоего бота
TOKEN = "8914916171:AAHkzPOHAne300FXHhB4FxvHyUQKYNBwBIU"

# ID администраторов (ты и создатель)
ADMIN_IDS = [8726230274, 7869485247]

router = Router()


# Состояния для анкеты
class Form(StatesGroup):
  name = State()
  age = State()
  zoom = State()
  timezone = State()
  squad = State()
  forum = State()
  raid = State()
  skill = State()
  username = State()
  confirm = State()
  editing = State()
  waiting_admin_message = State()
  waiting_reject_reason = State()


# Временное хранилище данных заявок
user_applications = {}


# /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
  await state.clear()
  keyboard = InlineKeyboardMarkup(inline_keyboard=[[
      InlineKeyboardButton(
          text="Написать заявку в клан", callback_data="start_form"
      )
  ]])
  await message.answer(
      "Здравствуйте, вас приветствует бот для написания заявок в наш клан"
      " **Hard raid squad**!\nЧтобы написать заявку в клан нажмите кнопку под"
      " сообщением.",
      reply_markup=keyboard,
      parse_mode="Markdown",
  )


# Начало заполнения
@router.callback_query(F.data == "start_form")
async def start_form(callback: CallbackQuery, state: FSMContext):
  await callback.message.edit_text(
      "Хорошо, приступим к написанию заявки! Это займёт не более 3-5 минут"
      " (смотря как быстро вы читаете и пишите).\n\nНиже напишите ваше реальное"
      " имя."
  )
  await state.set_state(Form.name)
  await callback.answer()


# Шаги опроса
@router.message(Form.name)
async def process_name(message: Message, state: FSMContext):
  await state.update_data(name=message.text, edited_name=False)
  await message.answer("Хорошо, теперь напишите ваш возраст.")
  await state.set_state(Form.age)


@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
  await state.update_data(age=message.text, edited_age=False)
  await message.answer("Где вы берёте ссылки на zoom конференции?")
  await state.set_state(Form.zoom)


@router.message(Form.zoom)
async def process_zoom(message: Message, state: FSMContext):
  await state.update_data(zoom=message.text, edited_zoom=False)
  await message.answer("Ваш часовой пояс?")
  await state.set_state(Form.timezone)


@router.message(Form.timezone)
async def process_timezone(message: Message, state: FSMContext):
  await state.update_data(timezone=message.text, edited_timezone=False)
  await message.answer("Что такое Squad?")
  await state.set_state(Form.squad)


@router.message(Form.squad)
async def process_squad(message: Message, state: FSMContext):
  await state.update_data(squad=message.text, edited_squad=False)
  await message.answer("Что такое Forum?")
  await state.set_state(Form.forum)


@router.message(Form.forum)
async def process_forum(message: Message, state: FSMContext):
  await state.update_data(forum=message.text, edited_forum=False)
  await message.answer("Что такое рейд? (Raid)")
  await state.set_state(Form.raid)


@router.message(Form.raid)
async def process_raid(message: Message, state: FSMContext):
  await state.update_data(raid=message.text, edited_raid=False)
  await message.answer("Ваш навык рейдерства от 1 до 10?")
  await state.set_state(Form.skill)


@router.message(Form.skill)
async def process_skill(message: Message, state: FSMContext):
  await state.update_data(skill=message.text, edited_skill=False)
  await message.answer(
      "Ваш юзернейм (Не напишите его — отказ) (Например: @username)"
  )
  await state.set_state(Form.username)


@router.message(Form.username)
async def process_username(message: Message, state: FSMContext):
  await state.update_data(username=message.text, edited_username=False)
  await message.answer(
      'Подтвердите написание анкеты, после написания "Да" вам дадут'
      " перепроверить её"
  )
  await state.set_state(Form.confirm)


@router.message(Form.confirm)
async def process_confirm(message: Message, state: FSMContext):
  if message.text.strip().lower() == "да":
    data = await state.get_data()
    text = format_application_text(data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Переделать", callback_data="edit_menu")],
        [InlineKeyboardButton(text="Отправить заявку", callback_data="submit_app")],
    ])
    await message.answer(
        "Ваша заявка была написана! Ниже она представлена по всем критериям"
        " которые вы писали! Если вы написали что-то не так либо не правдивую"
        ' информацию, нажмите кнопку "Переделать" чтобы изменить конкретный'
        f" пункт.\n\n{text}",
        reply_markup=keyboard,
    )
  else:
    await message.answer(
        'Пожалуйста, напишите "Да" для подтверждения перехода к проверке.'
    )


def format_application_text(data):
  return (
      f"👤 **Имя:** {data.get('name')}\n"
      f"📅 **Возраст:** {data.get('age')}\n"
      f"🔗 **Zoom ссылки:** {data.get('zoom')}\n"
      f"🌍 **Часовой пояс:** {data.get('timezone')}\n"
      f"🛡 **Squad:** {data.get('squad')}\n"
      f"💬 **Forum:** {data.get('forum')}\n"
      f"⚔️ **Raid:** {data.get('raid')}\n"
      f"📊 **Навык рейдерства:** {data.get('skill')}\n"
      f"🏷 **Юзернейм:** {data.get('username')}"
  )


# Меню редактирования
@router.callback_query(F.data == "edit_menu")
async def edit_menu(callback: CallbackQuery, state: FSMContext):
  keyboard = InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="Имя", callback_data="edit_name")],
      [InlineKeyboardButton(text="Возраст", callback_data="edit_age")],
      [InlineKeyboardButton(text="Zoom ссылки", callback_data="edit_zoom")],
      [InlineKeyboardButton(text="Часовой пояс", callback_data="edit_timezone")],
      [InlineKeyboardButton(text="Squad", callback_data="edit_squad")],
      [InlineKeyboardButton(text="Forum", callback_data="edit_forum")],
      [InlineKeyboardButton(text="Raid", callback_data="edit_raid")],
      [
          InlineKeyboardButton(
              text="Навык рейдерства", callback_data="edit_skill"
          )
      ],
      [InlineKeyboardButton(text="Юзернейм", callback_data="edit_username")],
      [InlineKeyboardButton(text="Вернуться назад", callback_data="back_to_preview")],
  ])
  await callback.message.edit_text(
      "Выберите пункт для изменения:", reply_markup=keyboard
  )
  await callback.answer()


@router.callback_query(F.data.startswith("edit_"))
async def edit_specific_field(callback: CallbackQuery, state: FSMContext):
  action = callback.data.split("_")[1]
  if action == "menu":
    return
  await state.update_data(current_edit=action)
  await callback.message.edit_text(
      f"Введите новое значение для пункта: {action}"
  )
  await state.set_state(Form.editing)
  await callback.answer()


@router.message(Form.editing)
async def save_edited_field(message: Message, state: FSMContext):
  data = await state.get_data()
  field = data.get("current_edit")
  await state.update_data(
      {field: message.text, f"edited_{field}": True, "current_edit": None}
  )

  keyboard = InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="Имя", callback_data="edit_name")],
      [InlineKeyboardButton(text="Возраст", callback_data="edit_age")],
      [InlineKeyboardButton(text="Zoom ссылки", callback_data="edit_zoom")],
      [InlineKeyboardButton(text="Часовой пояс", callback_data="edit_timezone")],
      [InlineKeyboardButton(text="Squad", callback_data="edit_squad")],
      [InlineKeyboardButton(text="Forum", callback_data="edit_forum")],
      [InlineKeyboardButton(text="Raid", callback_data="edit_raid")],
      [
          InlineKeyboardButton(
              text="Навык рейдерства", callback_data="edit_skill"
          )
      ],
      [InlineKeyboardButton(text="Юзернейм", callback_data="edit_username")],
      [InlineKeyboardButton(text="Вернуться назад", callback_data="back_to_preview")],
  ])
  await message.answer(
      "Пункт успешно изменен! Выберите следующий пункт для изменения или"
      ' нажмите "Вернуться назад".',
      reply_markup=keyboard,
  )


@router.callback_query(F.data == "back_to_preview")
async def back_to_preview(callback: CallbackQuery, state: FSMContext):
  data = await state.get_data()
  text = format_application_text(data)

  keyboard = InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="Переделать", callback_data="edit_menu")],
      [InlineKeyboardButton(text="Отправить заявку", callback_data="submit_app")],
  ])
  await callback.message.edit_text(text=text, reply_markup=keyboard)
  await callback.answer()


# Отправка заявки администраторам
@router.callback_query(F.data == "submit_app")
async def submit_application(callback: CallbackQuery, state: FSMContext, bot: Bot):
  data = await state.get_data()
  user_id = callback.from_user.id
  user_applications[user_id] = data

  app_text = format_application_text(data)

  # Проверяем, менял ли пользователь что-то реально
  edited_fields = [
      field.replace("edited_", "")
      for field, val in data.items()
      if field.startswith("edited_") and val is True
  ]
  changes_text = (
      f"\n\n✏️ **Измененные пункты:** {', '.join(edited_fields)}"
      if edited_fields
      else "\n\n📌 Пользователь ничего не изменял в анкете."
  )

  admin_text = (
      "У нас появилась новая заявка в клан! Ниже предоставлены критерии"
      f" пользователя.\n\n{app_text}{changes_text}"
  )

  admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
      [
          InlineKeyboardButton(
              text="Взять на рассмотрение",
              callback_data=f"review_{user_id}",
          )
      ],
      [
          InlineKeyboardButton(
              text="Написать пользователю",
              callback_data=f"msg_user_{user_id}",
          )
      ],
  ])

  for admin_id in ADMIN_IDS:
    try:
      await bot.send_message(
          admin_id, admin_text, reply_markup=admin_keyboard, parse_mode="Markdown"
      )
    except Exception as e:
      logging.error(f"Не удалось отправить админу {admin_id}: {e}")

  await callback.message.edit_text(
      "Ваша заявка была успешно отправлена составу клана! Примерное время"
      " ответа на заявку 5-15 минут!"
  )
  await state.clear()


# Админ нажал "Взять на рассмотрение"
@router.callback_query(F.data.startswith("review_"))
async def take_to_review(callback: CallbackQuery, bot: Bot):
  user_id = int(callback.data.split("_")[1])
  try:
    await bot.send_message(user_id, "Ваша заявка взята в рассмотрение!")
  except Exception:
    pass

  admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
      [
          InlineKeyboardButton(
              text="Отказать", callback_data=f"reject_{user_id}"
          ),
          InlineKeyboardButton(
              text="Принять", callback_data=f"accept_{user_id}"
          ),
      ],
      [
          InlineKeyboardButton(
              text="Написать пользователю",
              callback_data=f"msg_user_{user_id}",
          )
      ],
  ])
  await callback.message.edit_reply_markup(reply_markup=admin_keyboard)
  await callback.answer("Заявка взята на рассмотрение")


# Админ нажал "Написать пользователю"
@router.callback_query(F.data.startswith("msg_user_"))
async def admin_write_user(callback: CallbackQuery, state: FSMContext):
  user_id = int(callback.data.split("_")[2])
  await state.update_data(target_user_id=user_id)
  await state.set_state(Form.waiting_admin_message)
  await callback.message.answer(
      "Напишите сообщение пользователю (оно будет отправлено ему от лица"
      " состава):"
  )
  await callback.answer()


@router.message(Form.waiting_admin_message)
async def send_admin_message_to_user(message: Message, state: FSMContext, bot: Bot):
  data = await state.get_data()
  target_user_id = data.get("target_user_id")

  user_keyboard = InlineKeyboardMarkup(
      inline_keyboard=[[
          InlineKeyboardButton(text="Ответить", callback_data="user_reply_btn")
      ]]
  )

  await bot.send_message(
      target_user_id,
      "Вам пришло уведомление от состава клана!\n\n" f"{message.text}",
      reply_markup=user_keyboard,
  )

  await message.answer("Сообщение успешно отправлено пользователю!")
  await state.clear()


# Пользователь нажал кнопку "Ответить"
@router.callback_query(F.data == "user_reply_btn")
async def user_reply_prompt(callback: CallbackQuery, state: FSMContext):
  await state.set_state(Form.waiting_admin_message)
  await callback.message.answer(
      "Напишите ваш ответ на вопрос состава клана (доступна 1 отправка):"
  )
  await callback.answer()


# Отказ по заявке
@router.callback_query(F.data.startswith("reject_"))
async def reject_application(callback: CallbackQuery, state: FSMContext):
  user_id = int(callback.data.split("_")[1])
  await state.update_data(reject_user_id=user_id)
  await state.set_state(Form.waiting_reject_reason)
  await callback.message.answer("Укажите причину отказа заявки (Обязательно):")
  await callback.answer()


@router.message(Form.waiting_reject_reason)
async def process_reject_reason(
    message: Message, state: FSMContext, bot: Bot
):
  data = await state.get_data()
  user_id = data.get("reject_user_id")
  reason = message.text

  try:
    await bot.send_message(
        user_id,
        "Ваша заявка была отклонена! Причина отказа:\n" f"{reason}",
    )
  except Exception:
    pass

  await message.answer("Отказ успешно отправлен пользователю.")
  await state.clear()


# Принятие заявки
@router.callback_query(F.data.startswith("accept_"))
async def accept_application(callback: CallbackQuery, bot: Bot):
  user_id = int(callback.data.split("_")[1])
  try:
    await bot.send_message(
        user_id, "Ваша заявка принята! Ожидайте ответа в личку."
    )
  except Exception:
    pass

  await callback.message.answer("Заявка успешно принята!")
  await callback.answer()


async def main():
  logging.basicConfig(level=logging.INFO)
  bot = Bot(token=TOKEN)
  dp = Dispatcher(storage=MemoryStorage())
  dp.include_router(router)
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
