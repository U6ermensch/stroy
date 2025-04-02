import asyncio
from database import init_db, get_session
from models import Category

async def create_initial_categories():
    async for session in get_session():
        # Создаем основные категории
        categories = [
            Category(name="Кирпич", description="Строительный кирпич различных видов"),
            Category(name="Бетон", description="Бетон и бетонные смеси"),
            Category(name="Пиломатериалы", description="Доски, брус, вагонка"),
            Category(name="Кровля", description="Кровельные материалы"),
            Category(name="Отделочные материалы", description="Штукатурка, краски, обои"),
            Category(name="Инструменты", description="Строительные инструменты"),
            Category(name="Крепеж", description="Гвозди, саморезы, анкера"),
            Category(name="Сантехника", description="Сантехнические материалы"),
            Category(name="Электрика", description="Электротехнические материалы"),
        ]
        
        for category in categories:
            session.add(category)
        
        await session.commit()
        print("Категории успешно созданы!")

async def main():
    await init_db()
    await create_initial_categories()

if __name__ == "__main__":
    asyncio.run(main()) 