import streamlit as st
from database_manager import create_db
from csv_to_database import CSV2DataBase
from pandas import DataFrame

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
        data = csv_to_database.load_data()
        csv_head = data.head()
        st.subheader("Success")
        st.write(csv_head)
        #st.write(data[data['film_id'] == 22104])
    else : 
        return
    
    st.session_state["import_csv"] = True
    if st.button("Load database") :
        st.session_state["fill_database"] = True
    else : 
        if not st.session_state.get("fill_database") :
            st.write("database not loaded yet")

    if st.session_state.get("fill_database") :
        data = csv_to_database.load_data()
        st.session_state["fill_database"] = True
        csv_to_database.fill_database()
        st.subheader("Success")

if __name__ == "__main__":
    main()