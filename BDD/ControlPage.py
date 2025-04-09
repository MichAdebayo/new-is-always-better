import streamlit as st
from database_manager import create_db
from csv_to_database import CSV2DataBase
from pandas import DataFrame
from expected_fields import CsvType, JpBoxExpectedFilmField

# Créer la base de données si elle n'existe pas
create_db()

# Application Streamlit
def main():
    st.title("Control Page")
    csv_to_database = CSV2DataBase()

    if st.button("Import csv") :
        st.session_state["import_csv"] = True
    else : 
        if not st.session_state.get("import_csv") :
            st.write("button not clicked yet")

    if  st.session_state.get("import_csv") :
        data = csv_to_database.load_data(CsvType.JPBOX)
        csv_head = data.head()
        st.subheader("Success")
        st.write(f'shape: {data.shape}')

        # nb_total = data[JpBoxExpectedFilmField.FRANCE_FIRST_WEEK.value].shape[0]
        # entrees_ok = data[JpBoxExpectedFilmField.FRANCE_FIRST_WEEK.value].apply(lambda x: isinstance(x, float) and float(x) >0.0)
        # nb_ok = entrees_ok.sum()
        
        #st.write(data[data['film_id'] == 22104])
        #st.write(f"total entrees : {nb_total}")
        #st.write(f"entrees ok : {nb_total}")

        st.write(csv_head)
    else : 
        return
    
    st.session_state["import_csv"] = True
    if st.button("Load database") :
        st.session_state["fill_database"] = True
    else : 
        if not st.session_state.get("fill_database") :
            st.write("database not loaded yet")

    if st.session_state.get("fill_database") :
        data = csv_to_database.load_data(CsvType.JPBOX)
        st.session_state["fill_database"] = True
        csv_to_database.fill_database(CsvType.JPBOX)
        st.subheader("Success")

if __name__ == "__main__":
    main()