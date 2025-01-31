import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные о направлениях и курсах
PROGRAMS = {
    "Агрономия": ["Бакалавриат", "Магистратура"],
    "Агрохимия и агропочвоведение": ["Бакалавриат", "Магистратура"],
    "Ландшафтная архитектура": ["Бакалавриат", "Магистратура"],
    "Лесное дело": ["Бакалавриат", "Магистратура"]
}
COURSES = ["I", "II", "III", "IV"]

# Словарь для хранения информации о пользователях
USER_ACCOUNTS = {}

# Функция старта
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("Регистрация", callback_data='register')],
                [InlineKeyboardButton("Выбрать направление", callback_data='choose_program')],
                [InlineKeyboardButton("Моё расписание", callback_data='schedule')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

# Регистрация учетной записи студента
def register(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    USER_ACCOUNTS[user_id] = {"name": user_name, "program": None, "course": None}
    query.edit_message_text(f"Учетная запись зарегистрирована: {user_name}. Выберите направление подготовки.")
    choose_program(update, context)

# Выбор направления подготовки
def choose_program(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton(prog, callback_data=f'prog_{prog}')] for prog in PROGRAMS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.effective_message.reply_text("Выберите направление подготовки:", reply_markup=reply_markup)

# Выбор курса
def choose_course(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    program = query.data.split("_")[1]
    if user_id in USER_ACCOUNTS:
        USER_ACCOUNTS[user_id]["program"] = program
    keyboard = [[InlineKeyboardButton(course, callback_data=f'course_{program}_{course}')] for course in COURSES]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"Вы выбрали {program}. Теперь выберите курс:", reply_markup=reply_markup)

# Сохранение курса студента
def save_course(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    _, program, course = query.data.split("_")
    if user_id in USER_ACCOUNTS:
        USER_ACCOUNTS[user_id]["course"] = course
    query.edit_message_text(text=f"Вы зарегистрированы на {program}, {course} курс.")

# Отправка расписания
def send_schedule(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    if user_id not in USER_ACCOUNTS or not USER_ACCOUNTS[user_id]["program"] or not USER_ACCOUNTS[user_id]["course"]:
        query.message.reply_text("Сначала зарегистрируйтесь, используя кнопку 'Регистрация'.")
        return
    program = USER_ACCOUNTS[user_id]["program"]
    course = USER_ACCOUNTS[user_id]["course"]
    pdf_path = f"{program}_{course}.pdf"  # Название PDF-файла по шаблону
    try:
        with open(pdf_path, "rb") as file:
            query.message.reply_document(document=file, filename=f"Расписание {program} {course} курс.pdf")
    except FileNotFoundError:
        query.message.reply_text("Расписание не найдено. Попробуйте позже.")

# Основная функция
if __name__ == "__main__":
    updater = Updater("7922622721:AAFTTVY7fUOry1ivapQ24bT-YtFzB7JHNBw")
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(register, pattern="^register$"))
    dp.add_handler(CallbackQueryHandler(choose_program, pattern="^choose_program$"))
    dp.add_handler(CallbackQueryHandler(choose_course, pattern="^prog_"))
    dp.add_handler(CallbackQueryHandler(save_course, pattern="^course_"))
    dp.add_handler(CallbackQueryHandler(send_schedule, pattern="^schedule$"))
    
    updater.start_polling()
    updater.idle()
