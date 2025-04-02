from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models import Base, Category, Product
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def add_product(session: AsyncSession, name: str, description: str, price: float, category_id: int, image_url: str = None):
    """Add a new product to the database."""
    try:
        # Проверяем, что категория существует
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            print(f"Category with ID {category_id} not found")
            return None
        
        # Создаем новый товар
        product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            image_url=image_url
        )
        
        # Добавляем товар в базу данных
        session.add(product)
        await session.commit()
        
        # Обновляем объект, чтобы получить ID
        await session.refresh(product)
        
        print(f"Product added successfully: {product.name} (ID: {product.id})")
        return product
    except Exception as e:
        print(f"Error adding product: {e}")
        await session.rollback()
        return None

async def update_product(session: AsyncSession, product_id: int, **kwargs):
    stmt = select(Product).where(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()
    if product:
        for key, value in kwargs.items():
            setattr(product, key, value)
        await session.commit()
    return product

async def get_products(session: AsyncSession, category_id: int = None):
    """Get products from the database, optionally filtered by category."""
    try:
        if category_id:
            stmt = select(Product).where(Product.category_id == category_id)
        else:
            stmt = select(Product)
        result = await session.execute(stmt)
        products = result.scalars().all()
        print(f"Found {len(products)} products for category_id={category_id}")
        return products
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

async def get_categories(session: AsyncSession):
    """Get all categories from the database."""
    try:
        stmt = select(Category)
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []

async def add_category(session: AsyncSession, name: str, description: str = None):
    """Add a new category to the database."""
    try:
        category = Category(
            name=name,
            description=description
        )
        session.add(category)
        await session.commit()
        return category
    except Exception as e:
        print(f"Error adding category: {e}")
        await session.rollback()
        return None

async def update_category(session: AsyncSession, category_id: int, name: str = None, description: str = None):
    """Update an existing category in the database."""
    try:
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if category:
            if name is not None:
                category.name = name
            if description is not None:
                category.description = description
            await session.commit()
            return category
        return None
    except Exception as e:
        print(f"Error updating category: {e}")
        await session.rollback()
        return None

async def delete_category(session: AsyncSession, category_id: int):
    """Delete a category from the database."""
    try:
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        
        if category:
            await session.delete(category)
            await session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error deleting category: {e}")
        await session.rollback()
        return False 