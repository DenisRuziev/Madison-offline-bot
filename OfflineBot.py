from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)
from datetime import datetime, timedelta
import pytz

# Токен бота
BOT_TOKEN = "8073547010:AAFJ4CTgZCBV61jdzMi9ktHuxtMQZu2y6Jc"

# Москва - часовой пояс
MOSCOW_TZ = pytz.timezone("Europe/Moscow")

# Словарь для хранения времени последнего ответа пользователю
last_replied = {}

# Проверка, является ли текущее время нерабочим
def is_off_hours():
    now = datetime.now(MOSCOW_TZ).time()
    start_time = datetime.strptime("19:00", "%H:%M").time()  # Начало с 19:00
    end_time = datetime.strptime("10:00", "%H:%M").time()  # Конец до 10:00 следующего дня

    print(f"Текущее время: {now}, проверка нерабочего времени: {start_time} <= {now} < {end_time}")

    # Нерабочее время с 19:00 до 10:00 следующего дня
    if now >= start_time or now < end_time:
        return True
    return False

# Проверка на выходные
def is_weekend():
    now = datetime.now(MOSCOW_TZ)
    # Если суббота или воскресенье, разрешаем ответ
    if now.weekday() >= 5:
        return True
    return False

# Обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name if update.effective_user.first_name else ""  # Убираем fallback на 'пользователь'
    user_username = update.effective_user.username  # Получаем username пользователя
    now = datetime.now(MOSCOW_TZ)

    print(f"Получено сообщение от пользователя {user_name}, текущее время: {now}")

    if is_off_hours() or is_weekend():  # Проверяем, если выходные или нерабочие часы
        # Проверяем, когда бот последний раз отвечал этому пользователю
        last_reply_time = last_replied.get(user_id)
        if last_reply_time and now - last_reply_time < timedelta(hours=3):
            print("Прошло меньше 3 часов, не отвечаем.")
            return  # Не отвечаем, если прошло меньше 3 часов

        # Формируем тег с использованием username
        if user_username:
            mention = f"@{user_username}"
        else:
            mention = f"Пользователь {user_name}"

        # Отправляем сообщение
        print("Отправка сообщения о нерабочем времени")
        await update.message.reply_text(
            f"{mention}!\n\n"
            "Благодарим вас за обращение в службу технической поддержки Madison Consult. В данный момент мы находимся вне рабочего времени.\n"
            "Наши специалисты доступны для помощи с 10:00 до 19:00 по московскому времени.\n"
            "Спасибо за ваше понимание!"
        )

        # Обновляем время последнего ответа
        last_replied[user_id] = now
        print("Время последнего ответа обновлено.")


# Главная функция
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчик текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен.")
    # Запуск бота
    app.run_polling()


if __name__ == "__main__":
    main()
