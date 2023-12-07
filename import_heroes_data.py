import csv
from app.database import Session
from app.models import HeroCard


def import_data(csv_file_path: str, db: Session):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            record = HeroCard(
                name=row['name'],
                gender=row['appearance.gender'],
                intelligence=row['powerstats.intelligence'],
                strength=row['powerstats.strength'],
                speed=row['powerstats.speed'],
                durability=row['powerstats.durability'],
                power=row['powerstats.power'],
                combat=row['powerstats.combat'],
                img=row['image.url']
            )
            db.add(record)

    db.commit()


if __name__ == "__main__":
    csv_file_path = 'heroes.csv'
    import_data(csv_file_path, Session())
