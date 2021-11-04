from dataclasses import dataclass


@dataclass
class Item:
    id: int
    title: str
    description: str
    price: int
    photo_link: str


Tesla_X = Item(
    id=1,
    title="Тесла Model X",
    description="""
<b>Tesla Model X</b> — полноразмерный электрический кроссовер производства компании Tesla. 
Прототип был впервые показан в Лос-Анджелесе 9 февраля 2012 года. 
Коммерческие поставки начались 29 сентября 2015 года. 
Tesla Model X разрабатывается на базе платформы Tesla Model S \
и собирается на основном заводе компании во Фримонте, штат Калифорния.
""",
    price=1,
    photo_link="https://www.tesla.com/sites/tesla/files/curatedmedia/performance-hero%402.jpg"
)

Tesla_S = Item(
    id=2,
    title="Тесла Model S",
    description="""
<b>Tesla Model S</b> — пятидверный электромобиль производства американской компании Tesla. 
Прототип был впервые показан на Франкфуртском автосалоне в 2009 году; поставки автомобиля в США начались в июне 2012 года
""",
    price=80_000_00,
    photo_link="https://hips.hearstapps.com/hmg-prod.s3.amazonaws.com/images/tesla-model-s-1563301327.jpg"
)

Iphone = Item(
    id=3,
    title="Iphone XS",
    description="""
The iPhone XS and iPhone XS Max (stylized and marketed as iPhone Xs and iPhone Xs Max; \
Roman numeral "X" pronounced "ten")\
are smartphones designed, developed and marketed by Apple Inc. 
They are the twelfth-generation flagships of the iPhone, succeeding the iPhone X.
""",
    price=5_000,
    photo_link="https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/IPhone_XS_Silver.svg/200px-IPhone_XS_Silver.svg.png"
)

items = (
    Tesla_X, Tesla_S, Iphone
)
