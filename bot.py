import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TimedOut, NetworkError
from config import BOT_TOKEN, STORE_NAME, WORKING_HOURS, ADDRESS, CONTACT_PHONE, ADMIN_IDS
from database import get_session, get_products, get_categories, add_product, update_product, add_category, update_category, delete_category
from models import Product, Category
import asyncio
from sqlalchemy import select
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TimedOut, NetworkError
from config import BOT_TOKEN, STORE_NAME, WORKING_HOURS, ADDRESS, CONTACT_PHONE, ADMIN_IDS
from database import get_session, get_products, get_categories, add_product, update_product, add_category, update_category, delete_category
from models import Product, Category
import asyncio
from sqlalchemy import select

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("📋 КАТАЛОГ", callback_data='catalog'),
            InlineKeyboardButton("💰 ОПТ", callback_data='opt')
        ],
        [
            InlineKeyboardButton("🔍 ПОИСК", callback_data='search'),
            InlineKeyboardButton("ℹ️ О НАС", callback_data='about')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f'Добро пожаловать в {STORE_NAME}! 👋\n\n'
        'Выберите нужный раздел:',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == 'catalog':
            await show_catalog(query)
        elif query.data == 'opt':
            await show_opt(query)
        elif query.data == 'about':
            await show_about(query)
        elif query.data == 'search':
            await start_search(query)
        elif query.data == 'start':
            # Возврат в главное меню
            keyboard = [
                [
                    InlineKeyboardButton("📋 КАТАЛОГ", callback_data='catalog'),
                    InlineKeyboardButton("💰 ОПТ", callback_data='opt')
                ],
                [
                    InlineKeyboardButton("🔍 ПОИСК", callback_data='search'),
                    InlineKeyboardButton("ℹ️ О НАС", callback_data='about')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f'Добро пожаловать в {STORE_NAME}! 👋\n\n'
                     'Выберите нужный раздел:',
                reply_markup=reply_markup
            )
        elif query.data.startswith('category_'):
            try:
                category_id = int(query.data.split('_')[1])
                print(f"Opening category with ID: {category_id}")
                await show_products(query, category_id)
            except ValueError as e:
                print(f"Error parsing category ID: {e}")
                await query.answer("Ошибка: неверный ID категории", show_alert=True)
            except Exception as e:
                print(f"Error showing products: {e}")
                await query.answer("Произошла ошибка при загрузке товаров", show_alert=True)
        elif query.data.startswith('order_'):
            try:
                product_id = int(query.data.split('_')[1])
                await query.answer("Для заказа свяжитесь с нами по телефону", show_alert=True)
            except Exception as e:
                print(f"Error processing order: {e}")
                await query.answer("Произошла ошибка", show_alert=True)
    except Exception as e:
        print(f"Error in button_handler: {e}")
        await query.answer("Произошла ошибка", show_alert=True)
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📋 КАТАЛОГ", callback_data='catalog'),
                    InlineKeyboardButton("💰 ОПТ", callback_data='opt')
                ],
                [
                    InlineKeyboardButton("🔍 ПОИСК", callback_data='search'),
                    InlineKeyboardButton("ℹ️ О НАС", callback_data='about')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text=f'Произошла ошибка. Пожалуйста, попробуйте снова.\n\n'
                     'Выберите нужный раздел:',
                reply_markup=reply_markup
            )
        except Exception as edit_error:
            print(f"Error editing message: {edit_error}")

async def show_catalog(query):
    """Show the product catalog with categories."""
    try:
        # Получаем сессию базы данных
        async for session in get_session():
            # Получаем все категории
            categories = await get_categories(session)
            
            if not categories:
                message = "Каталог пуст. Пожалуйста, добавьте категории."
                keyboard = [[InlineKeyboardButton("◀️ НАЗАД", callback_data='start')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=message, reply_markup=reply_markup)
                return
            
            # Создаем клавиатуру с категориями
            keyboard = []
            
            # Добавляем кнопки для каждой категории
            for category in categories:
                # Для всех пользователей показываем только кнопку для просмотра товаров
                keyboard.append([
                    InlineKeyboardButton(category.name, callback_data=f"category_{category.id}")
                ])
            
            # Добавляем кнопку "Назад"
            keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data='start')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="🏗 *Каталог товаров*\n\nВыберите категорию:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error in show_catalog: {e}")
        message = "Произошла ошибка при загрузке каталога. Пожалуйста, попробуйте позже."
        keyboard = [[InlineKeyboardButton("◀️ НАЗАД", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup)

async def show_products(query, category_id: int):
    """Show products in a specific category."""
    try:
        async for session in get_session():
            # Получаем категорию
            stmt = select(Category).where(Category.id == category_id)
            result = await session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                await query.edit_message_text(
                    text="Категория не найдена.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД", callback_data='catalog')]])
                )
                return
            
            # Получаем товары в категории
            products = await get_products(session, category_id)
            
            if not products:
                await query.edit_message_text(
                    text=f"В категории «{category.name}» пока нет товаров.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД", callback_data='catalog')]])
                )
                return
            
            # Отправляем первое сообщение с названием категории
            await query.edit_message_text(
                text=f"*{category.name}*\n\nТовары в этой категории:",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД", callback_data='catalog')]])
            )
            
            # Отправляем каждый товар отдельным сообщением
            for product in products:
                # Формируем текст сообщения
                message_text = (
                    f"*{product.name}*\n\n"
                    f"{product.description}\n\n"
                    f"💰 Цена: {product.price} руб.\n"
                    f"ID товара: {product.id}"
                )
                
                try:
                    if product.image_url:
                        # Проверяем и корректируем URL изображения
                        image_url = product.image_url
                        if not image_url.startswith(('http://', 'https://')):
                            image_url = 'https://' + image_url.lstrip('/')
                        
                        # Отправляем фото с описанием
                        await query.message.reply_photo(
                            photo=image_url,
                            caption=message_text,
                            parse_mode="Markdown"
                        )
                    else:
                        # Отправляем только текст
                        await query.message.reply_text(
                            text=message_text,
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    print(f"Error sending product {product.id}: {e}")
                    # Если не удалось отправить с фото, отправляем без фото
                    await query.message.reply_text(
                        text=message_text,
                        parse_mode="Markdown"
                    )
            
            # Отправляем последнее сообщение с кнопкой "Назад"
            await query.message.reply_text(
                text="Для возврата в каталог нажмите кнопку ниже:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД В КАТАЛОГ", callback_data='catalog')]])
            )
            
    except Exception as e:
        print(f"Error in show_products: {e}")
        try:
            await query.edit_message_text(
                text="Произошла ошибка при загрузке товаров. Пожалуйста, попробуйте позже.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД", callback_data='catalog')]])
            )
        except Exception as edit_error:
            print(f"Error editing message: {edit_error}")
            try:
                await query.message.reply_text(
                    text="Произошла ошибка при загрузке товаров. Пожалуйста, попробуйте позже.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД", callback_data='catalog')]])
                )
            except Exception as reply_error:
                print(f"Error sending error message: {reply_error}")

async def show_opt(query):
    """Show wholesale pricing information."""
    message = f"💰 *Оптовые цены*\n\n"
    message += f"Для получения оптовых цен и условий сотрудничества, пожалуйста, свяжитесь с нами по телефону:\n\n"
    message += f"📞 {CONTACT_PHONE}\n\n"
    message += f"или посетите наш магазин по адресу:\n\n"
    message += f"📍 {ADDRESS}"
    
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown")

async def show_working_hours(query):
    """Show working hours."""
    message = f"🕒 Режим работы:\n\n{WORKING_HOURS}\n\n"
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup)

async def show_location(query):
    """Show store location."""
    message = f"📍 Адрес магазина:\n\n{ADDRESS}\n\n"
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup)

async def show_contacts(query):
    """Show contact information."""
    message = f"📞 Контактная информация:\n\n"
    message += f"Телефон: {CONTACT_PHONE}\n"
    message += f"Адрес: {ADDRESS}\n\n"
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup)

async def show_about(query):
    """Show about information."""
    message = f"ℹ️ *О нас*\n\n"
    message += f"Мы работаем с {WORKING_HOURS} и находимся по адресу:\n\n"
    message += f"📍 [{ADDRESS}](https://2gis.ru/irkutsk/search/мастер/firm/70000001041280291?m=104.176233%2C52.347187%2F14.69)\n\n"
    message += f"Если у вас есть вопросы или предложения, пожалуйста, свяжитесь с нами по телефону:\n\n"
    message += f"📞 {CONTACT_PHONE}"
    
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="Markdown", disable_web_page_preview=False)

async def add_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new product to the database."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Получаем аргументы команды
        args = context.args
        if not args:
            await update.message.reply_text(
                "Использование: /add_product название|описание|цена|id_категории|ссылка_на_фото\n"
                "Пример: /add_product Кирпич красный|Строительный кирпич красный|15.50|1|https://example.com/photo.jpg"
            )
            return
        
        # Объединяем все аргументы в одну строку и разбиваем по разделителю |
        command_text = ' '.join(args)
        parts = command_text.split('|')
        
        if len(parts) < 4:
            await update.message.reply_text(
                "Недостаточно аргументов. Использование: /add_product название|описание|цена|id_категории|ссылка_на_фото\n"
                "Пример: /add_product Кирпич красный|Строительный кирпич красный|15.50|1|https://example.com/photo.jpg"
            )
            return
        
        name = parts[0].strip()
        description = parts[1].strip()
        price = float(parts[2].strip())
        category_id = int(parts[3].strip())
        image_url = parts[4].strip() if len(parts) > 4 else None
        
        # Проверяем существование категории
        async for session in get_session():
            stmt = select(Category).where(Category.id == category_id)
            result = await session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                await update.message.reply_text(f"Категория с ID {category_id} не найдена.")
                return
            
            # Добавляем товар
            product = await add_product(session, name, description, price, category_id, image_url)
            
            if product:
                await update.message.reply_text(
                    f"✅ Товар успешно добавлен!\n\n"
                    f"📦 Название: {product.name}\n"
                    f"📝 Описание: {product.description}\n"
                    f"💰 Цена: {product.price} руб.\n"
                    f"📋 Категория: {category.name}\n"
                    f"🖼 Фото: {'Есть' if product.image_url else 'Нет'}"
                )
            else:
                await update.message.reply_text("❌ Ошибка при добавлении товара.")
    except ValueError as e:
        await update.message.reply_text(f"Ошибка в формате данных: {str(e)}")
    except Exception as e:
        print(f"Error in add_product_command: {e}")
        await update.message.reply_text(f"Ошибка при добавлении товара: {str(e)}")

async def update_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Update product price (admin only)."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return

    try:
        # Format: /update_product product_id|price
        args = context.args[0].split('|')
        if len(args) != 2:
            await update.message.reply_text(
                "Неверный формат. Используйте: /update_product product_id|price"
            )
            return

        product_id, price = args
        async for session in get_session():
            product = await update_product(
                session,
                int(product_id),
                price=float(price)
            )
            if product:
                await update.message.reply_text(f"Цена товара '{product.name}' успешно обновлена!")
            else:
                await update.message.reply_text("Товар не найден.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обновлении цены: {str(e)}")

async def list_categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all categories with their IDs."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    async for session in get_session():
        categories = await get_categories(session)
        if not categories:
            await update.message.reply_text("Категории не найдены.")
            return
        
        message = "📋 Список категорий:\n\n"
        for category in categories:
            message += f"ID: {category.id} - {category.name}\n"
            if category.description:
                message += f"   Описание: {category.description}\n"
            message += "\n"
        
        await update.message.reply_text(message)

async def add_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new category."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Format: /add_category name|description
        args = context.args[0].split('|')
        if len(args) < 1:
            await update.message.reply_text(
                "Неверный формат. Используйте: /add_category name|description"
            )
            return
        
        name = args[0]
        description = args[1] if len(args) > 1 else None
        
        async for session in get_session():
            category = await add_category(session, name=name, description=description)
            await update.message.reply_text(f"Категория '{category.name}' успешно добавлена с ID: {category.id}!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении категории: {str(e)}")

async def update_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Update a category."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Format: /update_category id|name|description
        args = context.args[0].split('|')
        if len(args) < 2:
            await update.message.reply_text(
                "Неверный формат. Используйте: /update_category id|name|description"
            )
            return
        
        category_id = int(args[0])
        name = args[1]
        description = args[2] if len(args) > 2 else None
        
        async for session in get_session():
            category = await update_category(
                session,
                category_id,
                name=name,
                description=description
            )
            if category:
                await update.message.reply_text(f"Категория успешно обновлена!")
            else:
                await update.message.reply_text("Категория не найдена.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при обновлении категории: {str(e)}")

async def delete_category_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a category."""
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Format: /delete_category id
        if not context.args:
            await update.message.reply_text(
                "Неверный формат. Используйте: /delete_category id"
            )
            return
        
        category_id = int(context.args[0])
        
        async for session in get_session():
            success = await delete_category(session, category_id)
            if success:
                await update.message.reply_text(f"Категория с ID {category_id} успешно удалена!")
            else:
                await update.message.reply_text("Категория не найдена.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при удалении категории: {str(e)}")

async def delete_product_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a product by ID."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Получаем ID товара из команды
        if not context.args:
            await update.message.reply_text(
                "Использование: /delete_product id_товара\n"
                "Пример: /delete_product 1"
            )
            return
        
        product_id = int(context.args[0])
        
        async for session in get_session():
            # Проверяем существование товара
            stmt = select(Product).where(Product.id == product_id)
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()
            
            if not product:
                await update.message.reply_text(f"❌ Товар с ID {product_id} не найден.")
                return
            
            # Удаляем товар
            await session.delete(product)
            await session.commit()
            
            await update.message.reply_text(f"✅ Товар '{product.name}' успешно удален!")
    
    except ValueError:
        await update.message.reply_text("❌ Ошибка: ID товара должен быть числом.")
    except Exception as e:
        print(f"Error in delete_product_command: {e}")
        await update.message.reply_text(f"❌ Ошибка при удалении товара: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if isinstance(context.error, TimedOut):
        logger.info("Connection timed out. Waiting before retry...")
        await asyncio.sleep(5)  # Wait 5 seconds before retrying
        return
        
    if isinstance(context.error, NetworkError):
        logger.info("Network error occurred. Waiting before retry...")
        await asyncio.sleep(5)  # Wait 5 seconds before retrying
        return
        
    if "Conflict: terminated by other getUpdates request" in str(context.error):
        logger.error("Another bot instance is running. Please stop other instances first.")
        import sys
        sys.exit(1)  # Завершаем программу с ошибкой

async def start_search(query):
    """Start the search process."""
    message = "🔍 *Поиск товаров*\n\n"
    message += "Введите название или описание товара, который вы ищете.\n"
    message += "Например: кирпич, цемент, краска и т.д."
    
    keyboard = [[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    # Устанавливаем состояние ожидания поискового запроса
    context = query.get_bot().context
    context.user_data['waiting_for_search'] = True

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for products based on user input."""
    # Проверяем, ожидаем ли мы поисковый запрос
    if not context.user_data.get('waiting_for_search', False):
        return
    
    # Сбрасываем флаг ожидания
    context.user_data['waiting_for_search'] = False
    
    search_query = update.message.text.lower()
    
    try:
        async for session in get_session():
            # Получаем все товары
            products = await get_products(session)
            
            # Фильтруем товары по поисковому запросу
            found_products = []
            for product in products:
                if (search_query in product.name.lower() or 
                    search_query in product.description.lower()):
                    found_products.append(product)
            
            if not found_products:
                await update.message.reply_text(
                    "❌ По вашему запросу ничего не найдено.\n\n"
                    "Попробуйте изменить запрос или вернитесь в каталог.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]])
                )
                return
            
            # Отправляем сообщение с результатами поиска
            await update.message.reply_text(
                f"🔍 *Результаты поиска по запросу: {search_query}*\n\n"
                f"Найдено товаров: {len(found_products)}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]])
            )
            
            # Отправляем каждый найденный товар отдельным сообщением
            for product in found_products:
                # Получаем категорию товара
                stmt = select(Category).where(Category.id == product.category_id)
                result = await session.execute(stmt)
                category = result.scalar_one_or_none()
                category_name = category.name if category else "Неизвестная категория"
                
                # Формируем текст сообщения
                message_text = (
                    f"*{product.name}*\n\n"
                    f"{product.description}\n\n"
                    f"💰 Цена: {product.price} руб.\n"
                    f"📋 Категория: {category_name}\n"
                    f"ID товара: {product.id}"
                )
                
                try:
                    if product.image_url:
                        # Проверяем и корректируем URL изображения
                        image_url = product.image_url
                        if not image_url.startswith(('http://', 'https://')):
                            image_url = 'https://' + image_url.lstrip('/')
                        
                        # Отправляем фото с описанием
                        await update.message.reply_photo(
                            photo=image_url,
                            caption=message_text,
                            parse_mode="Markdown"
                        )
                    else:
                        # Отправляем только текст
                        await update.message.reply_text(
                            text=message_text,
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    print(f"Error sending product {product.id}: {e}")
                    # Если не удалось отправить с фото, отправляем без фото
                    await update.message.reply_text(
                        text=message_text,
                        parse_mode="Markdown"
                    )
            
            # Отправляем последнее сообщение с кнопкой "Назад"
            await update.message.reply_text(
                text="Для возврата в главное меню нажмите кнопку ниже:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]])
            )
            
    except Exception as e:
        print(f"Error in search_products: {e}")
        await update.message.reply_text(
            "Произошла ошибка при поиске товаров. Пожалуйста, попробуйте позже.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ НАЗАД В МЕНЮ", callback_data='start')]])
        )

def main():
    """Start the bot."""
    try:
        # Create the Application and pass it your bot's token
        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("add_product", add_product_command))
        application.add_handler(CommandHandler("update_product", update_product_command))
        application.add_handler(CommandHandler("delete_product", delete_product_command))
        application.add_handler(CommandHandler("list_categories", list_categories_command))
        application.add_handler(CommandHandler("add_category", add_category_command))
        application.add_handler(CommandHandler("update_category", update_category_command))
        application.add_handler(CommandHandler("delete_category", delete_category_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        # Добавляем обработчик текстовых сообщений для поиска
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_products))
        
        # Add error handler
        application.add_error_handler(error_handler)

        # Start the Bot with increased timeout
        logger.info("Starting bot...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            read_timeout=30,
            write_timeout=30,
            connect_timeout=30,
            pool_timeout=30
        )
    except Exception as e:
        logger.error(f"Critical error: {e}")
        import sys
        sys.exit(1)

if __name__ == '__main__':
    main() 