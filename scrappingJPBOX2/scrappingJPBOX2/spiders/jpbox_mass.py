import scrapy
import re
from datetime import datetime
import os
import sys

# Ajout du répertoire parent au chemin de recherche pour pouvoir importer le fichier de config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import de la configuration
from jpbox_config import (
    PERIODS, MAX_GENRES, MAX_FILMS_PER_GENRE_PERIOD, MAX_TOTAL_FILMS,
    MAX_PAGES_PER_GENRE_PERIOD, EXPORT_SETTINGS, PERFORMANCE_SETTINGS,
    LOGGING_SETTINGS, SPECIFIC_GENRES, MAIN_ACTORS_ONLY, MAX_ACTORS,
    DEBUG_MODE, EXPORT_FIELDS
)

class MassiveJpboxSpider(scrapy.Spider):
    name = "jpbox_mass"
    allowed_domains = ["jpbox-office.com"]
    
    # Périodes à traiter (importées de la config)
    periods = PERIODS
    
    # Liste pour éviter les doublons
    visited_films = set()
    
    # Compteurs pour le diagnostic
    film_count = 0
    page_count = 0
    genre_count = 0
    
    # Paramètres personnalisés (combinés avec ceux de la config)
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_TIMEOUT': 120,
        'FEED_URI': EXPORT_SETTINGS['FEED_URI'],
        'FEED_FORMAT': EXPORT_SETTINGS['FEED_FORMAT'],
        'FEED_EXPORT_ENCODING': EXPORT_SETTINGS['FEED_EXPORT_ENCODING'],
        'FEED_EXPORT_DELIMITER': EXPORT_SETTINGS['FEED_EXPORT_DELIMITER'],
        'LOG_LEVEL': LOGGING_SETTINGS['LOG_LEVEL'],
        'LOG_FILE': LOGGING_SETTINGS['LOG_FILE'],
        'DOWNLOAD_DELAY': PERFORMANCE_SETTINGS['DOWNLOAD_DELAY'],
        'CONCURRENT_REQUESTS': PERFORMANCE_SETTINGS['CONCURRENT_REQUESTS'],
        'CONCURRENT_REQUESTS_PER_DOMAIN': PERFORMANCE_SETTINGS['CONCURRENT_REQUESTS_PER_DOMAIN'],
        'DEPTH_LIMIT': 0,
        'FEED_EXPORT_FIELDS': EXPORT_FIELDS
    }
    
    def start_requests(self):
        mode = "DEBUG" if DEBUG_MODE else "PRODUCTION"
        self.logger.info(f"🚀 DÉMARRAGE DU SPIDER JPBOX ({mode})")
        self.logger.info(f"Configuration: {MAX_GENRES} genres, {MAX_FILMS_PER_GENRE_PERIOD} films par genre/période, {MAX_TOTAL_FILMS} films max au total")
        url = "https://www.jpbox-office.com/v9_genres.php"
        yield scrapy.Request(url, self.parse_genres)
    
    def parse_genres(self, response):
        self.logger.info(f"Extraction des genres depuis {response.url}")
        genres_links = response.xpath('//table[@class="tablesmall tablesmall3"]//td[@class="col_poster_titre"]/h3/a | //div[@class="bloc_entete"]/following::table//td[@class="col_poster_titre"]/h3/a')
        
        total_genres = len(genres_links)
        self.logger.info(f"Nombre de genres trouvés : {total_genres}")
        
        # Filtrer les genres si une liste spécifique est fournie
        if SPECIFIC_GENRES:
            self.logger.info(f"Filtrage des genres: recherche uniquement de {SPECIFIC_GENRES}")
            filtered_genres = []
            for genre_link in genres_links:
                genre_name = genre_link.xpath('text()').get().strip()
                if genre_name in SPECIFIC_GENRES:
                    filtered_genres.append(genre_link)
            genres_links = filtered_genres
            self.logger.info(f"Genres filtrés: {len(genres_links)} genres correspondants trouvés")
        
        # Limiter le nombre de genres si configuré
        if MAX_GENRES is not None:
            genres_to_process = min(MAX_GENRES, len(genres_links))
            self.logger.info(f"Limitation à {genres_to_process} genres")
        else:
            genres_to_process = len(genres_links)
        
        for i, genre_link in enumerate(genres_links[:genres_to_process]):
            genre_url = response.urljoin(genre_link.xpath('@href').get())
            genre_name = genre_link.xpath('text()').get().strip()
            
            self.genre_count += 1
            self.logger.info(f"Genre {i+1}/{genres_to_process}: {genre_name}")
            
            for period in self.periods:
                if '?' in genre_url:
                    period_url = f"{genre_url}&year={period['year']}&year2={period['year2']}&view=25"
                else:
                    period_url = f"{genre_url}?year={period['year']}&year2={period['year2']}&view=25"
                
                yield scrapy.Request(
                    period_url,
                    callback=self.parse_films_list,
                    meta={
                        'genre': genre_name, 
                        'period': period['label'],
                        'page_count': 0,
                        'films_found': 0
                    }
                )
    
    def parse_films_list(self, response):
        # Vérifier si on a atteint la limite totale de films
        if MAX_TOTAL_FILMS is not None and self.film_count >= MAX_TOTAL_FILMS:
            self.logger.info(f"Limite totale de films atteinte ({MAX_TOTAL_FILMS}). Arrêt du scraping.")
            return
        
        genre = response.meta.get('genre', 'unknown')
        period = response.meta.get('period', 'unknown')
        page_count = response.meta.get('page_count', 0) + 1
        films_found = response.meta.get('films_found', 0)
        
        # Vérifier si on a atteint la limite de pages par genre/période
        if MAX_PAGES_PER_GENRE_PERIOD is not None and page_count > MAX_PAGES_PER_GENRE_PERIOD:
            self.logger.info(f"Limite de pages atteinte pour {genre} - {period} ({MAX_PAGES_PER_GENRE_PERIOD} pages). Passage au genre/période suivant.")
            return
        
        # Déterminer la page actuelle
        current_page = 1
        page_match = re.search(r'page=(\d+)', response.url)
        if page_match:
            current_page = int(page_match.group(1))
        
        # Extraire les lignes de films
        films = response.xpath('//table[contains(@class, "tablesmall")]//tr[.//td[contains(@class, "col_poster_titre")]/h3/a]')
        films_count = len(films)
        
        self.page_count += 1
        self.logger.info(f"Page {page_count} - Genre: {genre} - Période: {period} - Films: {films_count}")
        
        # Pour chaque film sur la page
        for film_row in films:
            # Vérifier si on a atteint la limite de films par genre/période
            if MAX_FILMS_PER_GENRE_PERIOD is not None and films_found >= MAX_FILMS_PER_GENRE_PERIOD:
                self.logger.info(f"Limite de films atteinte pour {genre} - {period} ({MAX_FILMS_PER_GENRE_PERIOD} films). Passage à la période/genre suivant.")
                break
            
            # Vérifier si on a atteint la limite totale de films
            if MAX_TOTAL_FILMS is not None and self.film_count >= MAX_TOTAL_FILMS:
                self.logger.info(f"Limite totale de films atteinte ({MAX_TOTAL_FILMS}). Arrêt du scraping.")
                break
            
            title_element = film_row.xpath('.//td[contains(@class, "col_poster_titre")]/h3/a/b/text()')
            if not title_element:
                title_element = film_row.xpath('.//td[contains(@class, "col_poster_titre")]/h3/a/text()')
            
            if title_element:
                title = title_element.get().strip()
                film_link = film_row.xpath('.//td[contains(@class, "col_poster_titre")]/h3/a/@href').get()
                
                if film_link:
                    full_url = response.urljoin(film_link)
                    film_id_match = re.search(r'id=(\d+)', full_url)
                    
                    if film_id_match:
                        film_id = film_id_match.group(1)
                        
                        if film_id not in self.visited_films:
                            self.visited_films.add(film_id)
                            self.film_count += 1
                            films_found += 1
                            
                            # Extraire les dates
                            content_html = film_row.xpath('.//td[contains(@class, "col_poster_contenu")]').get()
                            date_france = ""
                            date_usa = ""
                            
                            if content_html:
                                france_match = re.search(r'Sortie France : ([^<]+)', content_html)
                                if france_match:
                                    date_france = france_match.group(1).strip()
                                
                                usa_match = re.search(r'Sortie USA : ([^<]+)', content_html)
                                if usa_match:
                                    date_usa = usa_match.group(1).strip()
                            
                            # Extraire l'image
                            image_url = film_row.xpath('.//td[contains(@class, "col_poster_image")]/img/@src').get()
                            if image_url:
                                image_url = response.urljoin(image_url)
                            
                            # Log tous les 10 films
                            if self.film_count % 10 == 0:
                                self.logger.info(f"🎬 FILMS TRAITÉS: {self.film_count} - Dernier: {title}")
                            
                            # Créer un item avec les informations de base
                            item = {
                                'film_id': film_id,
                                'titre': title,
                                'genre_principale': genre,
                                'date_sortie_france': date_france,
                                'date_sortie_usa': date_usa,
                                'image_url': image_url
                            }
                            
                            # Naviguer vers la page du film
                            yield scrapy.Request(
                                full_url,
                                callback=self.parse_film_details,
                                meta={'item': item}
                            )
        
        # Si on n'a pas atteint les limites, continuer avec la page suivante
        if (MAX_FILMS_PER_GENRE_PERIOD is None or films_found < MAX_FILMS_PER_GENRE_PERIOD) and \
           (MAX_PAGES_PER_GENRE_PERIOD is None or page_count < MAX_PAGES_PER_GENRE_PERIOD) and \
           (MAX_TOTAL_FILMS is None or self.film_count < MAX_TOTAL_FILMS):
            
            # Rechercher la pagination
            next_page = response.xpath('//div[@class="pagination"]//a[contains(text(), "»")]/@href').get()
            if not next_page:
                next_page = response.xpath('//a[contains(text(), "Suivant") or contains(text(), "»")]/@href').get()
            if not next_page:
                current_page_num = current_page
                next_page_num = current_page + 1
                next_page = response.xpath(f'//div[@class="pagination"]//a[contains(text(), "{next_page_num}")]/@href').get()

            if next_page:
                next_url = response.urljoin(next_page)
                self.logger.info(f"📄 Navigation vers la page suivante: {next_url}")
                yield scrapy.Request(
                    next_url,
                    callback=self.parse_films_list,
                    meta={
                        'genre': genre, 
                        'period': period,
                        'page_count': page_count,
                        'films_found': films_found
                    },
                    priority=100  # Priorité élevée
                )
            else:
                self.logger.info(f"🏁 Fin de pagination pour {genre} - {period}")
        else:
            if MAX_FILMS_PER_GENRE_PERIOD is not None and films_found >= MAX_FILMS_PER_GENRE_PERIOD:
                self.logger.info(f"Limite de films atteinte pour {genre} - {period} ({films_found}/{MAX_FILMS_PER_GENRE_PERIOD})")
            if MAX_PAGES_PER_GENRE_PERIOD is not None and page_count >= MAX_PAGES_PER_GENRE_PERIOD:
                self.logger.info(f"Limite de pages atteinte pour {genre} - {period} ({page_count}/{MAX_PAGES_PER_GENRE_PERIOD})")
    
    def parse_film_details(self, response):
        """Extrait les détails complets d'un film"""
        item = response.meta.get('item', {})
        
        # Synopsis
        synopsis_texts = response.xpath('//div[@class="bloc_infos tablesmall5"]/text()').getall()
        if synopsis_texts:
            item['synopsis'] = " ".join([text.strip() for text in synopsis_texts if text.strip()])
        
        # Durée
        duree = response.xpath('//h3/text()[contains(., "min")]').get()
        if duree:
            duree_match = re.search(r'(\d+)\s*min', duree)
            if duree_match:
                item['duree_minutes'] = duree_match.group(1)
        
        # Note moyenne
        rating_row = response.xpath('//table[contains(@class, "tablesmall1")]//tr[td[@class="celluletitre"]/div[contains(text(), "Moyenne")]]/following-sibling::tr[1]')
        if rating_row:
            rating3_stars = rating_row.xpath('.//div[@class="rating3"]/text()').getall()
            stars_count = "".join(rating3_stars).count('★')
            if 0 <= stars_count <= 5:
                item['note_moyenne'] = str(stars_count)
        
        # Budget
        budget = response.xpath('//td[@class="cellulejaune"]/strong[text()="Budget"]/parent::td/following-sibling::td/div/strong/text()').get()
        if budget:
            item['budget'] = budget.strip()

        # Box-office démarrage
        box_office_demarrage = response.xpath('//td[text()="Démarrage"]/following-sibling::td/div/text()').get()
        if box_office_demarrage:
            item['box_office_demarrage'] = box_office_demarrage.strip()

        # Box-office France
        box_office_france = response.xpath('//td[@class="cellulejaune"]/strong[contains(text(), "Entrées")]/parent::td/following-sibling::td[@class="cellulejaune"]/div/strong/text()').get()
        if box_office_france:
            item['box_office_france'] = box_office_france.strip()
        
        # Recettes USA
        recette_usa = response.xpath('//td[contains(text(), "Etats-Unis")]/following-sibling::td/div/text()').get()
        if recette_usa:
            item['recette_usa'] = recette_usa.strip()
        
        # Recettes mondiales
        recette_monde = response.xpath('//td[contains(text(), "Reste du monde")]/following-sibling::td/div/text()').get()
        if recette_monde:
            item['recette_monde'] = recette_monde.strip()
        
        # Pays d'origine
        pays_xpath = response.xpath('//td[text()="Nationalité"]/following-sibling::td/text()').get()
        if pays_xpath:
            item['pays_origine'] = pays_xpath.strip()
        
        # Genres supplémentaires
        genres_list = response.xpath('//td[text()="Genre"]/following-sibling::td/a/text()').getall()
        if genres_list:
            item['genres'] = " | ".join([genre.strip() for genre in genres_list])
        
        # Aller au casting
        film_id = item.get('film_id')
        if film_id:
            casting_url = f"https://www.jpbox-office.com/fichfilm.php?id={film_id}&view=7"
            yield scrapy.Request(
                casting_url,
                callback=self.parse_casting,
                meta={'item': item}
            )
        else:
            yield item
    
    def parse_casting(self, response):
        """Extrait les acteurs et réalisateurs"""
        item = response.meta.get('item', {})
        
        # Réalisateurs
        realisateurs = []
        real_rows = response.xpath('//td[@class="celluletitre" and contains(text(), "Realisateur")]/parent::tr/following-sibling::tr')
        
        for row in real_rows:
            if row.xpath('./td[@class="celluletitre"]').get():
                break
                
            nom = row.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            if nom:
                realisateurs.append(nom.strip())
        
        if realisateurs:
            item['realisateur'] = " | ".join(realisateurs)
        
        # Acteurs
        acteurs = []
        act_rows = response.xpath('//td[@class="celluletitre" and contains(text(), "Acteurs et actrices")]/parent::tr/following-sibling::tr')
        
        for i, row in enumerate(act_rows):
            if row.xpath('./td[@class="celluletitre"]').get():
                break
                
            # Si on veut seulement les acteurs principaux et qu'on en a déjà suffisamment
            if MAIN_ACTORS_ONLY and i >= MAX_ACTORS:
                break
                
            nom = row.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            if nom:
                acteurs.append(nom.strip())
        
        if acteurs:
            # Limiter le nombre d'acteurs selon la configuration
            max_actors_to_keep = min(len(acteurs), MAX_ACTORS)
            item['acteurs'] = " | ".join(acteurs[:max_actors_to_keep])
        
        yield item
    
    def closed(self, reason):
        self.logger.info(f"Spider fermé pour la raison: {reason}")
        self.logger.info(f"RÉSUMÉ FINAL:")
        self.logger.info(f"- Genres traités: {self.genre_count}")
        self.logger.info(f"- Pages visitées: {self.page_count}")
        self.logger.info(f"- Films trouvés: {self.film_count}")
        self.logger.info(f"- Films uniques: {len(self.visited_films)}")