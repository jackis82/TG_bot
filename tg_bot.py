from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

import cv2
from pyzbar.pyzbar import decode
import numpy as np
from io import BytesIO


# Функция для создания клавиатуры
def create_menu_keyboard():
    keyboard = [
        ["Найти по QR", "Инф-я об объекте", "..."]  # Все кнопки в одной строке
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id  # Получаем user_id
    chat_id = update.message.chat_id  # Получаем chat_id
    await update.message.reply_text("Добро пожаловать!")
    await update.message.reply_text(f"(user_id={user_id}, chat_id={chat_id})")
    await update.message.reply_text("Выберите действие:", reply_markup=create_menu_keyboard())


# Обработчик нажатий на инлайн-кнопки
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем обработку запроса
    to_exit = 0

    # Определяем, какая кнопка была нажата
    if (query.data == "btn_place") and (to_exit == 0):
        await query.edit_message_text(text="Проверяем местоположение...")  # Отправляем ответ
        # ...
        await query.edit_message_text(text="Пока ничего")  # Отправляем ответ
        to_exit = 1

    if (query.data == "btn_tech") and (to_exit == 0):
        await query.edit_message_text(text="Запрос информации о технол.объектах...")  # Отправляем ответ
        # ...
        await query.edit_message_text(text="Пока ничего")  # Отправляем ответ
        to_exit = 1

    if (query.data == "btn_history") and (to_exit == 0):
        await query.edit_message_text(text="Запрос истории...")  # Отправляем ответ
        # ...
        await query.edit_message_text(text="Пока ничего")  # Отправляем ответ
        to_exit = 1


# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()  # Получаем текст сообщения пользователя
    to_exit = 0

    if (user_message.lower() == "инф-я об объекте") and (to_exit == 0):  # Проверяем, если сообщение "меню"
        # Создаем клавиатуру и отправляем её пользователю
        keyboard = [
            [InlineKeyboardButton("Место", callback_data="btn_place")],
            [InlineKeyboardButton("Технология", callback_data="btn_tech")],
            [InlineKeyboardButton("История", callback_data="btn_history")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Ваш выбор?", reply_markup=reply_markup)
        to_exit = 1

    if (user_message.lower() == "привет") and (to_exit == 0):  # Проверяем, если сообщение "Привет"
        await update.message.reply_text("Приветствую Вас!\nВыберите действие в нижней строке")  # Отправляем ответ
        to_exit = 1

    if (user_message.lower() == "найти по qr") and (to_exit == 0):
        await update.message.reply_text("Жду картинку с QR-кодом...")  # Отправляем ответ
        to_exit = 1

    if (user_message.lower() == "картинка") and (to_exit == 0):
        await update.message.reply_text("Жду картинку с QR-кодом...")  # Отправляем ответ
        to_exit = 1



# Функция для распознавания QR-кода
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем фото от пользователя
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_data = await file.download_as_bytearray()

    # Преобразуем сырые данные изображения (image_data) в массив NumPy типа uint8.
    # np.frombuffer используется для интерпретации байтовых данных как массива чисел.
    image_array = np.frombuffer(image_data, dtype=np.uint8)

    # Декодируем массив байтов в изображение с помощью OpenCV.
    # cv2.imdecode читает изображение из буфера и преобразует его в формат, подходящий для OpenCV.
    # Флаг cv2.IMREAD_COLOR указывает, что изображение должно быть загружено в цветном формате (BGR).
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Альтернативный способ загрузки изображения напрямую из файла (закомментирован).
    # img = cv2.imread(image_path)
    print('img done')

    # Масштабируем изображение до размера 1000x1000 пикселей.
    # cv2.resize изменяет размеры изображения, сохраняя пропорции или изменяя их в зависимости от параметров.
    resized_img = cv2.resize(img, (1000, 1000))
    print('resized_img done')

    # Преобразуем цветное изображение в градации серого.
    # cv2.cvtColor выполняет преобразование цветового пространства.
    # Здесь используется флаг cv2.COLOR_BGR2GRAY для перехода из BGR в оттенки серого.
    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    print('gray_img done')

    if gray_img is None:
        await update.message.reply_text("Нет изображения!")
    else:
        await update.message.reply_text("Ищу QR-код...")

        value = ''
        decoded_objects = decode(gray_img)

        if decoded_objects:
            print('QR-код найден!')
        else:
            print('QR-код не найден!')
            await update.message.reply_text('Ничего не найдено!')
        print(f'Найдено областей: {len(decoded_objects)}')

        for index, obj in enumerate(decoded_objects):
            print(f"\nИндекс: {index+1},\tТип: {obj.type}\tДанные из QR-кода:")
            value = obj.data.decode('utf-8')
        #     print("Тип:", obj.type)  # Например, 'QRCODE'
        #     print("Данные:", obj.data.decode("utf-8"))  # Преобразование байтов в строку
        #     print("Положение:", obj.polygon)  # Координаты многоугольника

        # detector = cv2.QRCodeDetector()
        # value, _, _ = detector.detectAndDecode(gray_img)
            print(value)
            if value == '':
                await update.message.reply_text('Ничего не распознано!')
            else:
                if isinstance(value, str):
                    if len(decoded_objects)>1:
                        await update.message.reply_text(f'Информация об объекте #{index+1}:')
                    else:
                        await update.message.reply_text(f'Информация об объекте:')
                    await update.message.reply_text(value)
                else:
                    await update.message.reply_text("QR-код не найден на изображении.")


# Основная функция для запуска бота
def main():
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    token = 'YOUR_BOT_TOKEN'

    # Создаем приложение
    application = ApplicationBuilder().token(token).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))  # Обработчик команды /start
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Обработчик изображений

    application.add_handler(CallbackQueryHandler(button_click))


    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()


