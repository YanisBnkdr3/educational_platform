import snowflake.connector

def test_snowflake_table_connection():
    try:
        # Connexion à Snowflake
        conn = snowflake.connector.connect(
            user='YANISBNKDR06',
            password='Yanismob06',
            account='iurfcex-xy75467',
            warehouse='COMPUTE_WH',
            database='EXAM_SYSTEM',
            schema='ONLINE_EXAM_SCHEMA'
        )
        cur = conn.cursor()
        print("Connexion réussie à Snowflake.")  # Message pour confirmer la connexion

        # Requête pour tester la connexion à une table spécifique
        cur.execute("SELECT * FROM ETUDIANT LIMIT 1")
        result = cur.fetchone()

        if result:
            print("Données récupérées de la table ETUDIANT :", result)
        else:
            print("Connexion réussie, mais aucune donnée trouvée dans la table ETUDIANT.")
        
        conn.close()
        return True
    except Exception as e:
        print("Erreur de connexion à Snowflake :", e)
        return False

# Exécuter la fonction de test
test_snowflake_table_connection()
