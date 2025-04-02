import asyncio
from sqlalchemy import delete
from database import async_session, engine
from models import Category, Product

async def delete_all_data():
    """Delete all categories and products from the database."""
    async with async_session() as session:
        try:
            # Delete all products first (due to foreign key constraints)
            await session.execute(delete(Product))
            
            # Then delete all categories
            await session.execute(delete(Category))
            
            # Commit the changes
            await session.commit()
            print("✅ Все категории и товары успешно удалены из базы данных.")
        except Exception as e:
            print(f"❌ Ошибка при удалении данных: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(delete_all_data()) 