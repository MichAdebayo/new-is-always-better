import scrapy
import re
from datetime import datetime

class MassiveJpboxSpider(scrapy.Spider):
    name = "jpbox_mass"
    allowed_domains = ["jpbox-office.com"]
    
    # Périodes à traiter
    periods = [
        {"year": "2000", "year2": "2009", "label": "2000-2009"},
        {"year": "2010", "year2": "2019", "label": "2010-2019"},
        {"year": "2020", "year2": "2029", "label": "2020-2029"},
    ]
    
    # Liste pour éviter les doublons
    visited_films = set()
    
    # Compteurs pour le diagnostic
    film_count = 0
    page_count = 0
    genre_count = 0
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_TIMEOUT': 120,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'DEPTH_LIMIT': 0,
        'FEED_URI': './massive_jpbox_export.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_DELIMITER': ';',
        'LOG_LEVEL': 'INFO',
        'FEED_EXPORT_FIELDS': [
            'film_id', 'titre', 'genre_principale', 'genres', 'date_sortie_france', 
            'date_sortie_usa', 'duree_minutes', 'synopsis', 'realisateur', 'acteurs', 
            'pays_origine', 'budget', 'box_office_demarrage', 'box_office_france', 'recette_usa', 
            'recette_monde', 'image_url', 'note_moyenne'
        ]
    }
    
    def start_requests(self):
        self.logger.info("🚀 DÉMARRAGE DU SPIDER MASSIVE (EXTRACTION COMPLÈTE)")
        url = "https://www.jpbox-office.com/v9_genres.php"
        yield scrapy.Request(url, self.parse_genres)
    
    def parse_genres(self, response):
        self.logger.info(f"Extraction des genres depuis {response.url}")
        genres_links = response.xpath('//table[@class="tablesmall tablesmall3"]//td[@class="col_poster_titre"]/h3/a | //div[@class="bloc_entete"]/following::table//td[@class="col_poster_titre"]/h3/a')
        
        total_genres = len(genres_links)
        self.logger.info(f"Nombre de genres trouvés : {total_genres}")
        
        # Limiter à 10 genres pour tester
        genres_to_process = 10
        
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
                    meta={'genre': genre_name, 'period': period['label']}
                )
    
    def parse_films_list(self, response):
        genre = response.meta.get('genre', 'unknown')
        period = response.meta.get('period', 'unknown')
        
        # Déterminer la page actuelle
        current_page = 1
        page_match = re.search(r'page=(\d+)', response.url)
        if page_match:
            current_page = int(page_match.group(1))
        
        # Extraire les lignes de films
        films = response.xpath('//table[contains(@class, "tablesmall")]//tr[.//td[contains(@class, "col_poster_titre")]/h3/a]')
        films_count = len(films)
        
        self.page_count += 1
        self.logger.info(f"Page {self.page_count} - Genre: {genre} - Période: {period} - Films: {films_count}")
        
        for film_row in films:  # Ne pas limiter le nombre de films par page
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
                meta={'genre': genre, 'period': period},
                priority=100  # Priorité élevée
            )
        else:
            self.logger.info(f"🏁 Fin de pagination pour {genre} - {period}")
    
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
        
        for row in act_rows:
            if row.xpath('./td[@class="celluletitre"]').get():
                break
                
            nom = row.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            if nom:
                acteurs.append(nom.strip())
        
        if acteurs:
            item['acteurs'] = " | ".join(acteurs[:10])  # Limiter à 10
        
        yield item
    
    def closed(self, reason):
        self.logger.info(f"Spider fermé pour la raison: {reason}")
        self.logger.info(f"RÉSUMÉ FINAL:")
        self.logger.info(f"- Genres traités: {self.genre_count}")
        self.logger.info(f"- Pages visitées: {self.page_count}")
        self.logger.info(f"- Films trouvés: {self.film_count}")
        self.logger.info(f"- Films uniques: {len(self.visited_films)}")