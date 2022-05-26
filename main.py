import telegram
import data
from typing import Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ChatMemberUpdated, Chat, ChatMember
from telegram.ext import CallbackContext, ContextTypes, CallbackQueryHandler, Updater, MessageHandler, Filters, \
    CommandHandler, ChatMemberHandler

bot = telegram.Bot(data.TOKEN)


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
            bot.send_message(chat_id=data.VNU_CHAT_ID,
                             text=f"@{member_name}, {data.GREETING_MESSAGE}",
                             reply_markup=reply_markup)
        else:
            member_name = update.chat_member.new_chat_member.user.full_name
            bot.send_message(chat_id=data.VNU_CHAT_ID,
                             text=f"{member_name}, {data.GREETING_MESSAGE}",
                             reply_markup=reply_markup)


def private_messages(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id != data.VNU_CHAT_ID:
        text = update.message.text
        if text == data.BUTTONS[0]:
            update.message.reply_text(
                text=data.RULES_LINK)
        elif text == data.BUTTONS[1]:
            update.message.reply_text(
                text=data.ABOUT_ME)
        elif text == data.BUTTONS[2]:
            update.message.reply_text(
                text=data.ADVERTISMENT_OPTIONS)
        elif text == data.BUTTONS[3]:
            update.message.reply_text(
                text=data.ADMINISTRATION)
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=data.BUTTONS[0]),
                    KeyboardButton(text=data.BUTTONS[1])
                ],
                [
                    KeyboardButton(text=data.BUTTONS[2]),
                    KeyboardButton(text=data.BUTTONS[3])
                ]
            ],
            resize_keyboard=True
        )
        if text == "/start":
            update.message.reply_text(
                text=data.INIT_MESSAGE,
                reply_markup=reply_markup)


def main():
    updater = Updater(
        token=data.TOKEN,
        use_context=True
    )

    updater.dispatcher.add_handler(ChatMemberHandler(new_member_notification, ChatMemberHandler.ANY_CHAT_MEMBER))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, private_messages))
    updater.start_polling(allowed_updates=Update.ALL_TYPES)
    updater.idle()


if __name__ == '__main__':
    main()
