import pandas as pd
from .models import Movie # adapte à ton app Django
import datetime as dt

class CustomDate:
    
    DATE_FORMATS = [
        "%d %B %Y",     # ex: 30 avril 2025
        "%d/%m/%Y",     # ex: 30/04/2025
        "%Y-%m-%d",     # ex: 2025-04-30
    ]

    def parse_french_date(self, date_str):
            for fmt in self.DATE_FORMATS:
                try:
                    return dt.datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            return None

def safe_str(value):
    return "" if pd.isna(value) else str(value).strip()

def safe_int(value):
    try:
        return int(str(value).replace(" ", "").replace("\u202f", ""))
    except:
        return 0

def process_movies_dataframe(df: pd.DataFrame) -> list:
    logs = []
    for _, row in df.iterrows():
        try:
            title = safe_str(row.get('film_title'))
            release_date_str = safe_str(row.get('release_date'))
            release_date_fr = CustomDate().parse_french_date(release_date_str)

            if not title or not release_date_fr:
                logs.append(f"❌ Skipped: title/date missing - '{title}' / '{release_date_str}'")
                continue

            movie = Movie.objects.filter(title=title, release_date_fr=release_date_fr).first()

            image_url = safe_str(row.get('film_image_url'))
            synopsis = safe_str(row.get('synopsis'))
            genre = safe_str(row.get('associated_genres'))
            cast = safe_str(row.get('top_stars'))
            fr_entries = safe_int(row.get('fr_entries'))

            if movie:
                movie.image_url = image_url
                movie.synopsis = synopsis
                movie.genre = genre
                movie.cast = cast
                movie.first_week_actual_entries_france = fr_entries
                movie.save()
                logs.append(f"✅ Updated: {title} ({release_date_fr})")
            else:
                Movie.objects.create(
                    title=title,
                    image_url=image_url,
                    synopsis=synopsis,
                    genre=genre,
                    cast=cast,
                    release_date_fr=release_date_fr,
                    first_week_actual_entries_france=fr_entries
                )
                logs.append(f"✅ Created: {title} ({release_date_fr})")
        except Exception as e:
            logs.append(f"❌ Error for {row.get('film_title')} : {str(e)}")

    return logs
