import asyncio
from sqlalchemy import select
from database import get_session, init_db
from models import Category, Product

async def check_database():
    """Check if the database has categories and products, add test data if needed."""
    # Инициализируем базу данных
    await init_db()
    
    # Проверяем наличие категорий
    async for session in get_session():
        # Проверяем наличие категорий
        stmt = select(Category)
        result = await session.execute(stmt)
        categories = result.scalars().all()
        
        if not categories:
            print("Категории не найдены. Добавляем тестовые категории...")
            
            # Добавляем тестовые категории
            category1 = Category(name="Кирпич", description="Строительный кирпич различных видов")
            category2 = Category(name="Цемент", description="Цемент различных марок")
            category3 = Category(name="Инструменты", description="Строительные инструменты")
            
            session.add(category1)
            session.add(category2)
            session.add(category3)
            await session.commit()
            
            print("Тестовые категории добавлены.")
            
            # Получаем ID категорий
            stmt = select(Category)
            result = await session.execute(stmt)
            categories = result.scalars().all()
            
            # Добавляем тестовые товары
            for category in categories:
                if category.name == "Кирпич":
                    product1 = Product(
                        name="Кирпич красный",
                        description="Строительный кирпич красный, полнотелый",
                        price=15.50,
                        category_id=category.id,
                        image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                    )
                    product2 = Product(
                        name="Кирпич белый",
                        description="Строительный кирпич белый, полнотелый",
                        price=16.50,
                        category_id=category.id,
                        image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                    )
                    session.add(product1)
                    session.add(product2)
                
                elif category.name == "Цемент":
                    product1 = Product(
                        name="Цемент М500",
                        description="Цемент марки М500, высокопрочный",
                        price=450.00,
                        category_id=category.id,
                        image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                    )
                    product2 = Product(
                        name="Цемент М400",
                        description="Цемент марки М400, универсальный",
                        price=420.00,
                        category_id=category.id,
                        image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                    )
                    session.add(product1)
                    session.add(product2)
                
                elif category.name == "Инструменты":
                    product1 = Product(
                        name="Молоток",
                        description="Строительный молоток, 500г",
                        price=850.00,
                        category_id=category.id,
                        image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                    )
                    product2 = Product(
                        name="Отвертка",
                        description="Набор отверток, 6 шт",
                        price=1200.00,
                        category_id=category.id,
                        image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                    )
                    session.add(product1)
                    session.add(product2)
            
            await session.commit()
            print("Тестовые товары добавлены.")
        else:
            print(f"Найдено {len(categories)} категорий.")
            
            # Проверяем наличие товаров
            stmt = select(Product)
            result = await session.execute(stmt)
            products = result.scalars().all()
            
            if not products:
                print("Товары не найдены. Добавляем тестовые товары...")
                
                # Добавляем тестовые товары
                for category in categories:
                    if category.name == "Кирпич":
                        product1 = Product(
                            name="Кирпич красный",
                            description="Строительный кирпич красный, полнотелый",
                            price=15.50,
                            category_id=category.id,
                            image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                        )
                        product2 = Product(
                            name="Кирпич белый",
                            description="Строительный кирпич белый, полнотелый",
                            price=16.50,
                            category_id=category.id,
                            image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                        )
                        session.add(product1)
                        session.add(product2)
                    
                    elif category.name == "Цемент":
                        product1 = Product(
                            name="Цемент М500",
                            description="Цемент марки М500, высокопрочный",
                            price=450.00,
                            category_id=category.id,
                            image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                        )
                        product2 = Product(
                            name="Цемент М400",
                            description="Цемент марки М400, универсальный",
                            price=420.00,
                            category_id=category.id,
                            image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                        )
                        session.add(product1)
                        session.add(product2)
                    
                    elif category.name == "Инструменты":
                        product1 = Product(
                            name="Молоток",
                            description="Строительный молоток, 500г",
                            price=850.00,
                            category_id=category.id,
                            image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                        )
                        product2 = Product(
                            name="Отвертка",
                            description="Набор отверток, 6 шт",
                            price=1200.00,
                            category_id=category.id,
                            image_url="https://ormis.ru/photo_uploads/12-0-410/12-0-410.jpg"
                        )
                        session.add(product1)
                        session.add(product2)
                
                await session.commit()
                print("Тестовые товары добавлены.")
            else:
                print(f"Найдено {len(products)} товаров.")

if __name__ == "__main__":
    asyncio.run(check_database()) 