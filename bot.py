from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
import time

TOKEN = os.environ.get("BOT_TOKEN")

BASE_PATH = "files"

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
        "😁 تم تصميم هذا البوت من قبل  Ehab Refai",
        reply_markup=reply_markup
    )

# ===== التعامل مع الأزرار =====
def button_handler(update, context):
    query = update.callback_query
    query.answer()

    # ===== سنوات =====
    if query.data in ["year1", "year2", "year3"]:
        show_semesters(query)

    # ===== العودة =====
    elif query.data == "back":
        start_over(query)

    # ===== إرسال الملفات =====
    elif "file" in query.data:
        send_single_file(query, query.data, context)

    # ===== اختيار فصل لإظهار الملفات =====
    elif "sem" in query.data:
        show_files(query, query.data)

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
        keyboard = [[InlineKeyboardButton("📖 الفصل الأول", callback_data="year3_sem1")]]

    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"✨ اختر الفصل من {year}:", reply_markup=reply_markup)

# ===== دالة الرجوع =====
def start_over(query):
    keyboard = [
        [InlineKeyboardButton("📘 السنة الأولى", callback_data="year1")],
        [InlineKeyboardButton("📗 السنة الثانية", callback_data="year2")],
        [InlineKeyboardButton("📙 السنة الثالثة", callback_data="year3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("👋 عدنا إلى البداية، اختر السنة:", reply_markup=reply_markup)

# ===== دالة إظهار الملفات داخل الفصل =====
def show_files(query, data):
    year, sem = data.split("_")
    folder_path = os.path.join(BASE_PATH, year, sem.replace("sem", "semester"))

    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        query.message.reply_text("❌ لا توجد ملفات في هذا الفصل 😢")
        return

    keyboard = []
    for file_name in os.listdir(folder_path):
        callback = f"{data}_file_{file_name}"
        keyboard.append([InlineKeyboardButton(f"📄 {file_name}", callback_data=callback)])

    keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data=year)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"📂 اختر الملف لإرساله:", reply_markup=reply_markup)

# ===== دالة إرسال ملف واحد =====
def send_single_file(query, data, context):
    parts = data.split("_file_")
    folder_data = parts[0]  # مثال: year1_sem1
    file_name = parts[1]

    year, sem = folder_data.split("_")
    folder_path = os.path.join(BASE_PATH, year, sem.replace("sem", "semester"))
    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path):
        query.message.reply_text("❌ الملف غير موجود 😢")
        return

    # نبض البوت أثناء الإرسال
    context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    time.sleep(0.3)

    # إرسال الملف
    with open(file_path, "rb") as f:
        query.message.reply_document(f, caption=f"📄 {file_name} ✅ تم الإرسال بنجاح!")

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
