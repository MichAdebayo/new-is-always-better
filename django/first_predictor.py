import joblib
from sklearn.pipeline import Pipeline

class FirstPredictor() :
    def __init__(self, model_version:int):
        self.model_version = model_version

    def predict(self, movie_title : str, movie_release_date: str) -> tuple[int, int]:
        """
        N'utilise pas movie_release_date pour l'instant
        """

        match(self.model_version) :
            case 0 : 
                return self._predict_version_0(movie_title)
            
            case 1 : 
                return self._predict_version_1(movie_title)
            
        
    def _predict_version_0(self, movie_title: str) -> tuple[int, int]:
        """
        csv origin = films_jp_box.csv
        """

        # chargement modèle
        import joblib
        from sklearn.pipeline import Pipeline
        dummy_model: Pipeline  = joblib.load("dummy_pipeline.joblib")

        # chargement data 
        import pandas as pd
        
        #original_csv = pd.read_csv('static/films_jp_box.csv')
        original_csv = pd.read_csv('static/films_jp_box_V2.csv', sep=';')

        movie_row = original_csv[original_csv['titre']== movie_title].iloc[[0]]
        prediction = dummy_model.predict(movie_row)

        pred_int = int(prediction[0])
        error = int(pred_int/5)
       
        return  (pred_int, error)
    
    def _predict_version_1(self, movie_title: str) -> tuple[int, int]:
        """
        csv origin = massive_jpbox_clean.csv
        """

        # chargement modèle
        import joblib
        from sklearn.pipeline import Pipeline
        dummy_model: Pipeline  = joblib.load("dummy_pipeline.joblib")

        # chargement data 
        import pandas as pd
        original_csv = pd.read_csv('static/massive_jpbox_clean.csv')

        movie_row = original_csv[original_csv['titre']== movie_title].iloc[[0]]
        prediction = dummy_model.predict(movie_row)

        pred_int = int(prediction[0])
        error = int(pred_int/5)
       
        return  (pred_int, error)
    
    

    