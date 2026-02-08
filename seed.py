"""Seed the database with test data."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.activity import Activity
from app.models.building import Building
from app.models.organization import (
    Organization,
    OrganizationPhone,
    organization_activities,
)


def seed() -> None:
    engine = create_engine(settings.database_url)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()

    # Check if data already exists (idempotent)
    if db.query(Building).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    # ── Buildings ──────────────────────────────────────────────
    buildings = [
        Building(
            address="г. Москва, ул. Ленина 1, офис 3",
            latitude=55.7558,
            longitude=37.6173,
        ),
        Building(
            address="г. Москва, ул. Пушкина 5",
            latitude=55.7601,
            longitude=37.6186,
        ),
        Building(
            address="г. Москва, пр. Мира 10",
            latitude=55.7712,
            longitude=37.6316,
        ),
        Building(
            address="г. Новосибирск, ул. Блюхера 32/1",
            latitude=55.0084,
            longitude=82.9357,
        ),
        Building(
            address="г. Новосибирск, ул. Красный проспект 50",
            latitude=55.0302,
            longitude=82.9204,
        ),
        Building(
            address="г. Санкт-Петербург, Невский проспект 28",
            latitude=59.9343,
            longitude=30.3351,
        ),
        Building(
            address="г. Санкт-Петербург, ул. Рубинштейна 15",
            latitude=59.9298,
            longitude=30.3454,
        ),
    ]
    db.add_all(buildings)
    db.flush()

    # ── Activities (tree, max 3 levels) ───────────────────────
    # Level 1
    food = Activity(name="Еда", level=1)
    cars = Activity(name="Автомобили", level=1)
    it = Activity(name="IT и Технологии", level=1)
    db.add_all([food, cars, it])
    db.flush()

    # Level 2
    meat = Activity(name="Мясная продукция", parent_id=food.id, level=2)
    dairy = Activity(name="Молочная продукция", parent_id=food.id, level=2)
    bakery = Activity(name="Выпечка", parent_id=food.id, level=2)
    trucks = Activity(name="Грузовые", parent_id=cars.id, level=2)
    passenger = Activity(name="Легковые", parent_id=cars.id, level=2)
    software = Activity(name="Разработка ПО", parent_id=it.id, level=2)
    db.add_all([meat, dairy, bakery, trucks, passenger, software])
    db.flush()

    # Level 3
    parts = Activity(name="Запчасти", parent_id=passenger.id, level=3)
    accessories = Activity(name="Аксессуары", parent_id=passenger.id, level=3)
    web_dev = Activity(name="Веб-разработка", parent_id=software.id, level=3)
    db.add_all([parts, accessories, web_dev])
    db.flush()

    # ── Organizations ─────────────────────────────────────────
    orgs = [
        Organization(name='ООО "Рога и Копыта"', building_id=buildings[0].id),
        Organization(name='ООО "Молочный мир"', building_id=buildings[0].id),
        Organization(name='ООО "АвтоПлюс"', building_id=buildings[1].id),
        Organization(name='ООО "Мясной двор"', building_id=buildings[3].id),
        Organization(name='ООО "Хлебный дом"', building_id=buildings[2].id),
        Organization(name='ООО "ГрузАвто"', building_id=buildings[3].id),
        Organization(name='ООО "Запчасти24"', building_id=buildings[4].id),
        Organization(name='ООО "ТехноСофт"', building_id=buildings[5].id),
        Organization(name='ООО "Молоко и Сливки"', building_id=buildings[1].id),
        Organization(name='ООО "Невский Гурман"', building_id=buildings[6].id),
        Organization(name='ООО "СибАвто"', building_id=buildings[4].id),
    ]
    db.add_all(orgs)
    db.flush()

    # ── Phones ────────────────────────────────────────────────
    phones = [
        OrganizationPhone(organization_id=orgs[0].id, phone_number="2-222-222"),
        OrganizationPhone(organization_id=orgs[0].id, phone_number="3-333-333"),
        OrganizationPhone(
            organization_id=orgs[1].id, phone_number="8-923-666-13-13"
        ),
        OrganizationPhone(
            organization_id=orgs[2].id, phone_number="8-495-100-20-30"
        ),
        OrganizationPhone(
            organization_id=orgs[2].id, phone_number="8-495-100-20-31"
        ),
        OrganizationPhone(
            organization_id=orgs[3].id, phone_number="8-383-200-10-10"
        ),
        OrganizationPhone(
            organization_id=orgs[4].id, phone_number="8-495-300-40-50"
        ),
        OrganizationPhone(
            organization_id=orgs[5].id, phone_number="8-383-400-50-60"
        ),
        OrganizationPhone(
            organization_id=orgs[6].id, phone_number="8-383-500-60-70"
        ),
        OrganizationPhone(
            organization_id=orgs[6].id, phone_number="8-383-500-60-71"
        ),
        OrganizationPhone(
            organization_id=orgs[7].id, phone_number="8-812-600-70-80"
        ),
        OrganizationPhone(
            organization_id=orgs[8].id, phone_number="8-495-700-80-90"
        ),
        OrganizationPhone(
            organization_id=orgs[9].id, phone_number="8-812-800-90-00"
        ),
        OrganizationPhone(
            organization_id=orgs[10].id, phone_number="8-383-900-00-10"
        ),
    ]
    db.add_all(phones)
    db.flush()

    # ── Organization ↔ Activity links ─────────────────────────
    links = [
        # "Рога и Копыта" → Мясная, Молочная
        {"organization_id": orgs[0].id, "activity_id": meat.id},
        {"organization_id": orgs[0].id, "activity_id": dairy.id},
        # "Молочный мир" → Молочная
        {"organization_id": orgs[1].id, "activity_id": dairy.id},
        # "АвтоПлюс" → Легковые, Запчасти
        {"organization_id": orgs[2].id, "activity_id": passenger.id},
        {"organization_id": orgs[2].id, "activity_id": parts.id},
        # "Мясной двор" → Мясная
        {"organization_id": orgs[3].id, "activity_id": meat.id},
        # "Хлебный дом" → Выпечка
        {"organization_id": orgs[4].id, "activity_id": bakery.id},
        # "ГрузАвто" → Грузовые
        {"organization_id": orgs[5].id, "activity_id": trucks.id},
        # "Запчасти24" → Запчасти, Аксессуары
        {"organization_id": orgs[6].id, "activity_id": parts.id},
        {"organization_id": orgs[6].id, "activity_id": accessories.id},
        # "ТехноСофт" → Разработка ПО, Веб-разработка
        {"organization_id": orgs[7].id, "activity_id": software.id},
        {"organization_id": orgs[7].id, "activity_id": web_dev.id},
        # "Молоко и Сливки" → Молочная
        {"organization_id": orgs[8].id, "activity_id": dairy.id},
        # "Невский Гурман" → Мясная, Молочная, Выпечка
        {"organization_id": orgs[9].id, "activity_id": meat.id},
        {"organization_id": orgs[9].id, "activity_id": dairy.id},
        {"organization_id": orgs[9].id, "activity_id": bakery.id},
        # "СибАвто" → Легковые, Аксессуары
        {"organization_id": orgs[10].id, "activity_id": passenger.id},
        {"organization_id": orgs[10].id, "activity_id": accessories.id},
    ]
    for link in links:
        db.execute(organization_activities.insert().values(**link))

    db.commit()
    db.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
