import scrapy
import re

class JpboxOfficeSpider(scrapy.Spider):
    name = "jpbox_office"
    allowed_domains = ["jpbox-office.com"]
    
    # Maximum de films à récupérer par genre
    max_films_per_genre = 1500
    
    # Liste pour éviter les doublons
    visited_films = set()
    
    # Paramètres pour éviter d'être bloqué
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'DOWNLOAD_DELAY': 3,  # Augmenté à 3 secondes pour éviter d'être bloqué
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,  # Limiter les requêtes simultanées
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8,en-US;q=0.7',
            'Referer': 'https://www.jpbox-office.com/',
            'Connection': 'keep-alive'
        }
    }
    
    def start_requests(self):
        # URL pour la page des genres
        url = "https://www.jpbox-office.com/v9_genres.php"
        yield scrapy.Request(url, self.parse_genres)
    
    def parse_genres(self, response):
        """Extrait la liste des genres et navigue vers chaque page de genre"""
        self.logger.info(f"Extraction des genres depuis {response.url}")
        
        # Extraire tous les liens de genre
        genres_links = response.xpath('//table[@class="tablesmall tablesmall3"]//td[@class="col_poster_titre"]/h3/a')
        
        self.logger.info(f"Nombre de genres trouvés : {len(genres_links)}")
        
        # Limiter à 5 genres pour les tests
        max_genres = 66
        count = 0
        
        # Pour chaque genre, extraire l'URL et le nom
        for genre_link in genres_links:
            if count >= max_genres:
                break
                
            genre_url = response.urljoin(genre_link.xpath('@href').get())
            genre_name = genre_link.xpath('text()').get().strip()
            
            # Log pour vérification
            self.logger.info(f"Genre trouvé : {genre_name} ({genre_url})")
            
            # Ajouter les paramètres année et vue
            if '?' in genre_url:
                genre_url += '&year=2020&year2=2029&view=25'
            else:
                genre_url += '?year=2020&year2=2029&view=25'
            
            # Requête vers la page du genre
            yield scrapy.Request(
                genre_url,
                callback=self.parse_films_list,
                meta={'genre': genre_name}
            )
            
            count += 1
    
    def parse_films_list(self, response):
        """Extrait la liste des films en utilisant la structure HTML exacte"""
        genre = response.meta.get('genre', 'unknown')
        
        self.logger.info(f"Analyse de la page: {response.url} - Genre: {genre}")
        
        # Compter le nombre de lignes dans le tableau pour vérifier
        rows = response.xpath('//tr')
        self.logger.info(f"Nombre total de lignes (tr) trouvées: {len(rows)}")
        
        # Compteur pour ce genre spécifique
        films_count = 0
        
        for film_row in rows:
            # Vérifier si on a atteint la limite pour ce genre
            if films_count >= self.max_films_per_genre:
                break
            
            # Vérifier si cette ligne contient bien un film
            title_element = film_row.xpath('.//td[contains(@class, "col_poster_titre")]/h3/a/b/text()')
            
            if title_element:
                # Extraire le titre
                title = title_element.get().strip()
                
                # Extraire l'URL du film
                film_link = film_row.xpath('.//td[contains(@class, "col_poster_titre")]/h3/a/@href').get()
                
                if film_link:
                    # Construire l'URL complète
                    full_url = response.urljoin(film_link)
                    
                    # Extraire l'ID du film
                    film_id_match = re.search(r'id=(\d+)', full_url)
                    if not film_id_match:
                        film_id_match = re.search(r'fichfilm.php\?id=(\d+)', full_url)
                    
                    if film_id_match:
                        film_id = film_id_match.group(1)
                        
                        # Éviter les doublons
                        if film_id not in self.visited_films:
                            self.visited_films.add(film_id)
                            
                            # Extraire l'URL de l'image
                            image_url = film_row.xpath('.//td[contains(@class, "col_poster_image")]/img/@src').get()
                            if image_url:
                                image_url = response.urljoin(image_url)
                            
                            # Extraire les informations de date
                            content_cell = film_row.xpath('.//td[contains(@class, "col_poster_contenu")]/text()').getall()
                            
                            # Pour le texte HTML complet incluant les <br>
                            content_html = film_row.xpath('.//td[contains(@class, "col_poster_contenu")]').get()
                            
                            # Initialiser les dates
                            date_france = ""
                            date_usa = ""
                            
                            # Traiter le contenu HTML pour extraire les dates
                            if content_html:
                                # Trouver la date de sortie France
                                france_match = re.search(r'Sortie France : ([^<]+)', content_html)
                                if france_match:
                                    date_france = france_match.group(1).strip()
                                
                                # Trouver la date de sortie USA
                                usa_match = re.search(r'Sortie USA : ([^<]+)', content_html)
                                if usa_match:
                                    date_usa = usa_match.group(1).strip()
                            
                            self.logger.info(f"Film trouvé: {title} (ID: {film_id}) - Genre: {genre}")
                            self.logger.info(f"Date France: {date_france}, Date USA: {date_usa}")
                            
                            # Créer un item avec les informations extraites
                            item = {
                                'film_id': film_id,
                                'titre': title,
                                'genre_principale': genre,
                                'date_sortie_france': date_france,
                                'date_sortie_usa': date_usa,
                                'image_url': image_url
                            }
                            
                            yield scrapy.Request(
                                full_url,
                                self.parse_film_details,
                                meta={'item': item}
                            )
                            
                            # Incrémenter le compteur de films pour ce genre
                            films_count += 1

    def parse_film_details(self, response):
        """Extrait les détails d'un film depuis sa page individuelle"""
        
        item = response.meta.get('item', {})
        
        self.logger.info(f"Analyse des détails du film: {item.get('titre', 'Inconnu')} - {response.url}")
        
        # 1. Synopsis
        synopsis_texts = response.xpath('//div[@class="bloc_infos tablesmall5"]/text()').getall()
        if synopsis_texts:
            #Joindre tous les fragments de texte et nettoyer
            item['synopsis'] = " ".join([text.strip() for text in synopsis_texts if text.strip()])
        #Voir pour remplacer les "," par "§"

        # 2. Durée 
        duree = response.xpath('//h3/text()[contains(., "min")]').get()
        if duree:
            duree_clean = duree.strip()
            if "min" in duree_clean:
                item['duree'] = duree_clean
        
        # 3. Note moyenne 
        try:
            # Cibler précisément la section Moyenne et la première ligne d'étoiles
            rating_row = response.xpath('//table[contains(@class, "tablesmall1")]//tr[td[@class="celluletitre"]/div[contains(text(), "Moyenne")]]/following-sibling::tr[1]')
            
            if rating_row:
                # Extraire les étoiles de rating3 (étoiles pleines)
                rating3_stars = rating_row.xpath('.//div[@class="rating3"]/text()').getall()
                stars_count = "".join(rating3_stars).count('★')
                
                # Vérifier si nous avons une valeur raisonnable
                if 0 <= stars_count <= 5:
                    item['note_moyenne'] = str(stars_count)
                    self.logger.info(f"Note moyenne extraite: {stars_count} étoiles")
                else:
                    item['note_moyenne'] = "Non disponible"
                    self.logger.warning(f"Nombre d'étoiles anormal: {stars_count}")
            else:
                item['note_moyenne'] = "Non disponible"
                self.logger.warning("Section de notation moyenne non trouvée")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction de la note moyenne: {e}")
            item['note_moyenne'] = "Non disponible"

        #4. Entrées France
        entrees_demarrage = response.xpath('//td[text()="Démarrage"]/following-sibling::td/div/text()').get()
        if entrees_demarrage:
            item['entrees_demarrage_france'] = entrees_demarrage.strip()
        
        #5. Entrées totales en France 
        entrees_totales = response.xpath('//td[@class="cellulejaune"]/strong[contains(text(), "Entrées")]/parent::td/following-sibling::td[@class="cellulejaune"]/div/strong/text()').get()
        if not entrees_totales:
            entrees_totales = response.xpath('//td[contains(@class, "cellulejaune")][.//strong[contains(text(), "Entrées")]]/following-sibling::td/div/strong/text()').get()
        if entrees_totales:
            item['entrees_totales_france'] = entrees_totales.strip()

        #6. Budget
        self.logger.info(f"Tentative d'extraction du budget pour {item.get('titre')}")
        
        # Tentative 1
        budget_css = response.css('table.tablesmall tr:first-child td:last-child div strong::text').get()
        self.logger.info(f"Résultat sélecteur CSS: {budget_css}")
        
        # Tentative 2
        budget_xpath1 = response.xpath('//td[@class="cellulejaune"]/strong[text()="Budget"]/parent::td/following-sibling::td/div/strong/text()').get()
        self.logger.info(f"Résultat XPath spécifique: {budget_xpath1}")
        
        # Tentative 3
        budget_xpath2 = response.xpath('//td[contains(., "Budget")]/following-sibling::td/div/strong/text()').get()
        self.logger.info(f"Résultat XPath général: {budget_xpath2}")
        
        # Tentative 4
        budget_regex = None
        if "Budget" in response.text:
            self.logger.info("Le mot 'Budget' existe dans la page")
            budget_match = re.search(r'Budget.*?<strong>([\d\s]+\$)</strong>', response.text)
            if budget_match:
                budget_regex = budget_match.group(1)
                self.logger.info(f"Correspondance regex trouvée: {budget_regex}")
        else:
            self.logger.info("Le mot 'Budget' n'existe PAS dans la page")
        
        # Utiliser le premier résultat non-nul
        budget = budget_css or budget_xpath1 or budget_xpath2 or budget_regex
        
        if budget:
            # Nettoyer et formater le budget pour éviter les problèmes d'exportation
            budget_clean = budget.strip()
            # Supprimer les caractères non-ASCII qui pourraient causer des problèmes
            budget_clean = ''.join(c for c in budget_clean if ord(c) < 128)
            # Convertir explicitement en string pour assurer la compatibilité avec CSV
            item['budget'] = str(budget_clean)
            self.logger.info(f"Budget extrait et nettoyé avec succès: {budget_clean}")
        else:
            self.logger.error(f"Impossible d'extraire le budget pour {item.get('titre')}")
            # Valeur par défaut pour éviter les champs vides
            item['budget'] = "Non disponible"

        # Débogage de l'item avant de continuer
        self.logger.info(f"Item partiel avant extraction des autres données: {item}")

        #7. Recettes USA
        recette_usa = response.xpath('//td[contains(text(), "Etats-Unis")]/following-sibling::td/div/text()').get()
        if recette_usa:
            item['recette_usa'] = recette_usa.strip()

        #8. Recettes mondiales
        recette_monde = response.xpath('//td[contains(text(), "Reste du monde")]/following-sibling::td/div/text()').get()
        if recette_monde:
            item['recette_monde'] = recette_monde.strip()

        #9. Total salles
        total_salles = response.xpath('//td[@class="cellulejaune"]/strong[text()="Total Salles"]/parent::td/following-sibling::td/div/strong/text()').get()
        if total_salles:
            item['total_salles'] = total_salles.strip()
        
        #10. Naviguer vers la page "casting" pour extraire les acteurs
        film_id = item.get('film_id')
        if film_id:
            casting_url = f"https://www.jpbox-office.com/fichfilm.php?id={film_id}&view=7"
            yield scrapy.Request(
                casting_url,
                callback=self.parse_casting,
                meta={'item': item.copy()}
            )
        else:
            yield item

    def parse_casting(self, response):
        """Extrait toutes les informations de casting en une seule fonction"""
        self.logger.info(f"!!!! EXTRACTION DU CASTING POUR {response.url} !!!!")
        item = response.meta.get('item', {})
        
        # 1. Extraire les acteurs
        acteurs_list = []
        acteurs_rows = response.xpath('//td[@class="celluletitre" and contains(text(), "Acteurs et actrices")]/parent::tr/following-sibling::tr')
        
        for acteur_row in acteurs_rows:
            if acteur_row.xpath('./td[@class="celluletitre"]').get():
                break
                
            nom_acteur = acteur_row.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            role_info = acteur_row.xpath('.//td[@class="col_poster_titre"][2]/i/text()').get()
            role_nom = acteur_row.xpath('.//td[@class="col_poster_titre"][2]/text()').get()
            
            if nom_acteur:
                info_complementaire = []
                if role_info:
                    info_complementaire.append(role_info.strip())
                if role_nom:
                    role_nom = role_nom.strip()
                    if role_nom and role_nom not in ['-', '']:
                        info_complementaire.append(role_nom)
                
                if info_complementaire:
                    acteurs_list.append(f"{nom_acteur.strip()} ({' - '.join(info_complementaire)})")
                else:
                    acteurs_list.append(nom_acteur.strip())
        
        if acteurs_list:
            item['acteurs'] = " | ".join(acteurs_list)
            self.logger.info(f"Acteurs extraits: {item['acteurs']}")
        else:
            item['acteurs'] = "Non disponible"
        
        # 2. Extraire les réalisateurs
        realisateurs_list = []
        realisateurs_rows = response.xpath('//td[@class="celluletitre" and contains(text(), "Realisateur")]/parent::tr/following-sibling::tr')
        
        for realisateur_row in realisateurs_rows:
            if realisateur_row.xpath('./td[@class="celluletitre"]').get():
                break
                
            nom_realisateur = realisateur_row.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            if nom_realisateur:
                realisateurs_list.append(nom_realisateur.strip())
        
        if realisateurs_list:
            item['realisateurs'] = " | ".join(realisateurs_list)
            self.logger.info(f"Réalisateurs extraits: {item['realisateurs']}")
        else:
            item['realisateurs'] = "Non disponible"
        
        # 3. Extraire les producteurs
        producteurs_list = []
        producteurs_rows = response.xpath('//td[@class="celluletitre" and contains(text(), "Producteur")]/parent::tr/following-sibling::tr')
        
        for producteur_row in producteurs_rows:
            if producteur_row.xpath('./td[@class="celluletitre"]').get():
                break
                
            nom_producteur = producteur_row.xpath('.//td[@class="col_poster_titre"]/h3/a/text()').get()
            role_producteur = producteur_row.xpath('.//td[@class="col_poster_titre"]/i/text()').get() or producteur_row.xpath('.//td[@class="col_poster_titre"]/colspan/i/text()').get()
            
            if nom_producteur:
                if role_producteur:
                    producteurs_list.append(f"{nom_producteur.strip()} ({role_producteur.strip()})")
                else:
                    producteurs_list.append(nom_producteur.strip())
        
        if producteurs_list:
            item['producteurs'] = " | ".join(producteurs_list)
            self.logger.info(f"Producteurs extraits: {item['producteurs']}")
        else:
            item['producteurs'] = "Non disponible"
        
        # Tout faire en un seul yield à la fin
        self.logger.info(f"ITEM FINAL COMPLET: {item}")
        yield item