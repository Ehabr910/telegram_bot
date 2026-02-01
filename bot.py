from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
import time
import sys

# ===== قراءة التوكن =====
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    print("❌ BOT_TOKEN is not set")
    sys.exit(1)

# ===== المسار الأساسي =====
BASE_PATH = "files"

# تأكيد وجود مجلد files
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

# ===== دالة البداية =====
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("📘 السنة الأولى", callback_data="year1")],
        [InlineKeyboardButton("📗 السنة الثانية", callback_data="year2")],
        [InlineKeyboardButton("📙 السنة الثالثة", callback_data="year3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "👋 أهلاً بك في بوت مجتمع اللغة الألمانية 🇩🇪\n"
        "😁 تم تصميم هذا البوت من قبل Ehab Refai",
        reply_markup=reply_markup
    )

# ===== التعامل مع الأزرار =====
def button_handler(update, context):
    try:
        query = update.callback_query
        query.answer()

        if query.data in ["year1", "year2", "year3"]:
            show_semesters(query)

        elif query.data == "back":
            start_over(query)

        elif "_file_" in query.data:
            send_single_file(query, query.data, context)

        elif "sem" in query.data:
            show_files(query, query.data)

    except Exception as e:
        print("❌ Button handler error:", e)

# ===== دالة إظهار الفصول =====
def show_semesters(query):
    year = query.data
    keyboard = []

    if year == "year1":
        keyboard = [
            [InlineKeyboardButton("📖 الفصل الأول", callback_data="year1_sem1")],
            [InlineKeyboardButton("📚 الفصل الثاني", callback_data="year1_sem2")]
        ]
    elif year == "year2":
        keyboard = [
            [InlineKeyboardButton("📖 الفصل الأول", callback_data="year2_sem1")],
            [InlineKeyboardButton("📚 الفصل الثاني", callback_data="year2_sem2")]
        ]
    elif year == "year3":
        keyboard = [
            [InlineKeyboardButton("📖 الفصل الأول", callback_data="year3_sem1")]
        ]

    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
    query.edit_message_text(
        f"✨ اختر الفصل من {year}:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== دالة الرجوع =====
def start_over(query):
    keyboard = [
        [InlineKeyboardButton("📘 السنة الأولى", callback_data="year1")],
        [InlineKeyboardButton("📗 السنة الثانية", callback_data="year2")],
        [InlineKeyboardButton("📙 السنة الثالثة", callback_data="year3")]
    ]
    query.edit_message_text(
        "👋 عدنا إلى البداية، اختر السنة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== دالة إظهار الملفات =====
def show_files(query, data):
    try:
        year, sem = data.split("_")
        folder_path = os.path.join(BASE_PATH, year, sem.replace("sem", "semester"))

        if not os.path.exists(folder_path) or not os.listdir(folder_path):
            query.message.reply_text("❌ لا توجد ملفات في هذا الفصل 😢")
            return

        keyboard = []
        for file_name in os.listdir(folder_path):
            callback = f"{data}_file_{file_name}"
            keyboard.append(
                [InlineKeyboardButton(f"📄 {file_name}", callback_data=callback)]
            )

        keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data=year)])
        query.edit_message_text(
            "📂 اختر الملف لإرساله:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        print("❌ show_files error:", e)

# ===== دالة إرسال ملف =====
def send_single_file(query, data, context):
    try:
        folder_data, file_name = data.split("_file_")
        year, sem = folder_data.split("_")
        file_path = os.path.join(
            BASE_PATH,
            year,
            sem.replace("sem", "semester"),
            file_name
        )

        if not os.path.exists(file_path):
            query.message.reply_text("❌ الملف غير موجود 😢")
            return

        context.bot.send_chat_action(
            chat_id=query.message.chat_id,
            action=ChatAction.UPLOAD_DOCUMENT
        )
        time.sleep(0.3)

        with open(file_path, "rb") as f:
            query.message.reply_document(
                f,
                caption=f"📄 {file_name} ✅ تم الإرسال بنجاح!"
            )

    except Exception as e:
        print("❌ send_single_file error:", e)

# ===== تشغيل البوت =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
