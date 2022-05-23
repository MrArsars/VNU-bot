import telegram
from data import TOKEN, TEST_CHAT_ID, VNU_CHAT_ID
from typing import Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ChatMemberUpdated, Chat, ChatMember
from telegram.ext import CallbackContext, ContextTypes, CallbackQueryHandler, Updater, MessageHandler, Filters, \
    CommandHandler, ChatMemberHandler

bot = telegram.Bot(TOKEN)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.CREATOR,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


def new_member_notification(update: Update, context: CallbackContext):
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result

    keyboard = [
        [
            InlineKeyboardButton("Тиць сюди", url="https://t.me/private_vnu_bot")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not was_member and is_member:
        member_name = update.chat_member.new_chat_member.user.username
        if member_name is not None:
            bot.send_message(chat_id=VNU_CHAT_ID,
                             text=f"@{member_name}, вітаємо у Чаті ВНУ! Ознайомтесь, будь ласка, з правилами чату",
                             reply_markup=reply_markup)
        else:
            member_name = update.chat_member.new_chat_member.user.full_name
            bot.send_message(chat_id=VNU_CHAT_ID,
                             text=f"{member_name}, вітаємо у Чаті ВНУ! Ознайомтесь, будь ласка, з правилами чату",
                             reply_markup=reply_markup)


def send_rules(member_id):
    bot.send_message(chat_id=member_id,
                     text="https://telegra.ph/Normativn%D1%96-%D1%96deolog%D1%96chn%D1%96-strateg%D1%96chn%D1%96-ta-%D1%96nformuvaln%D1%96-dokumenti-chatu-VNU-05-19")


def private_messages(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id != VNU_CHAT_ID:
        text = update.message.text
        buttons = ["Правила", "Про мене", "Реклама", "Адміністрація чату"]
        if text == buttons[0]:
            update.message.reply_text(
                text="Ось наші правила: https://linktr.ee/vnuchat")
        elif text == buttons[1]:
            update.message.reply_text(
                text="Я бот, розроблений адміністратором чату @paitsun2 для ознайомлення нових учасників з правилами чату, якщо виникли якісь питання чи ви знайшли баг, прошу звертатись безпосередньо до мого розробника)")
        elif text == buttons[2]:
            update.message.reply_text(
                text="жду коли стас доробить умови реклами")
        elif text == buttons[3]:
            update.message.reply_text(
                text="Власник чату: @stanislavyakovsky\nТопадмін @paitsun2\nнадалі список адміністраторів формується...")
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Правила"),
                    KeyboardButton(text="Про мене")
                ],
                [
                    KeyboardButton(text="Реклама"),
                    KeyboardButton(text="Адміністрація чату")
                ]
            ],
            resize_keyboard=True
        )
        if text == "/start":
            update.message.reply_text(
                text="Привіт, я приватний бот, створений студентом спеціально для чату Волинського Національного Університету. Перед початком спілкування у нашому чаті, будь ласка, ознайомся з правилами та основними положеннями, або ж, якщо ти вже ознайомлений, можеш вибрати розділ, що тебе цікавить",
                reply_markup=reply_markup)


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )

    updater.dispatcher.add_handler(ChatMemberHandler(new_member_notification, ChatMemberHandler.ANY_CHAT_MEMBER))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, private_messages))
    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


if __name__ == '__main__':
    main()
