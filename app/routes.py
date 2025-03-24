from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from app.database import get_async_session
from app.models import ShortenedURL
from app.schemas import URLCreate, URLResponse, URLStats
from app.generator_short_link import generate_short_code
from datetime import timedelta


router = APIRouter()


# создаем сокращенную ссылку и кладем в бд
@router.post("/links/shorten", response_model=URLResponse)
async def shorten_url(url_data: URLCreate, db: AsyncSession = Depends(get_async_session)):
    """Данная ручка создает сокращенную ссылку"""
    # проверяем ссылку на занятость
    if url_data.custom_alias:
        existing = await db.execute(select(ShortenedURL).where(ShortenedURL.short_code == url_data.custom_alias))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Alias already exists")
        short_code = url_data.custom_alias
    # если пользователь не прописал alias, то давайте сгенеририруем его
    else:
        short_code = generate_short_code()

    expires_at = datetime.now(timezone.utc) + timedelta(hours=48)

    new_url = ShortenedURL(original_url=url_data.original_url,
                           short_code=short_code,
                           expires_at=expires_at)

    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)
    return new_url


# возвращаем оригинальную ссылку (URL) по сокращенной ссылке и увеличиваем счетчик по посещениям
@router.get("/links/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_async_session)):
    """Возвращаем оригинальную ссылку по сокращенной ссылке и увеличиваем счетчик по посещениям"""
    result = await db.execute(select(ShortenedURL).where(ShortenedURL.short_code == short_code))
    url_entry = result.scalars().first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Link nt found")

    url_entry.visit_count += 1
    await db.commit()

    return {"redirect_to": url_entry.original_url}

# удаляем ссылки из бд
@router.delete("/links/{short_code}")
async def delete_link(short_code: str, db: AsyncSession = Depends(get_async_session)):
    """Удаляем запись из БД по сокращенной ссылке"""
    result = await db.execute(select(ShortenedURL).where(ShortenedURL.short_code == short_code))
    url_entry = result.scalars().first()
    if not url_entry:
       raise HTTPException(status_code=404, detail="Link not found")

    await db.delete(url_entry)
    await db.commit()
    return {"message": "Link deleted successfully"}


# обновляем ссылку
@router.put("/links/{short_code}")
async def update_link(short_code: str, new_data: URLCreate, db: AsyncSession = Depends(get_async_session)):
    """Обновляем ссылку для сокращенной ссылки"""
    # Ищем существующую ссылку по short_code
    result = await db.execute(select(ShortenedURL).where(ShortenedURL.short_code == short_code))
    url_entry = result.scalars().first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Link not found")

    if new_data.custom_alias and new_data.custom_alias != short_code:
        existing = await db.execute(select(ShortenedURL).where(ShortenedURL.short_code == new_data.custom_alias))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="Alias already exists")

        url_entry.short_code = new_data.custom_alias

    url_entry.original_url = new_data.original_url

    await db.commit()
    return {"message": "Link updated successfully"}


# получаем статистику
@router.get("/links/{short_code}/stats", response_model=URLStats)
async def get_link_stats(short_code: str, db: AsyncSession = Depends(get_async_session)):
    """Возвращаем статистику по сокращенной ссылке"""
    result = await db.execute(select(ShortenedURL).where(ShortenedURL.short_code == short_code))
    url_entry = result.scalars().first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Link not found")
    return url_entry


# возвращаем сокращенную ссылку по оригинальноый ссылке
@router.get("/links/search")
async def search_link(original_url: str, db: AsyncSession = Depends(get_async_session)):
    """Возвращаем сокращенную ссылку по оригинальной ссылке"""
    result = await db.execute(select(ShortenedURL).where(ShortenedURL.original_url == original_url.strip()))

    url_entry = result.scalars().first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Link not found")
    await db.commit()
    await db.refresh(url_entry)

    return {"short_code": url_entry.short_code}




