import streamlit as st
import requests
import re
import time
import datetime

st.set_page_config(page_title="Alerte Prix Pro", page_icon="🤖")
st.title("🤖 Moniteur de Prix pour Entreprises")

# --- SYSTÈME DE SÉCURITÉ CLIENT ---
mot_de_passe_client = st.text_input("Entrez votre clé d'activation client :", type="password")

if mot_de_passe_client != "Client30Dollars":
    st.warning("⚠️ Veuillez entrer une clé d'activation valide pour utiliser le robot.")
    st.stop()

# --- FORMULAIRE DU CLIENT ---
with st.form("form_robot"):
    url_site = st.text_input("Lien URL du site concurrent :", value="https://scrapethissite.com")
    email_client = st.text_input("Votre adresse courriel :", value="test@courriel.com")
    
    # 🌟 LE NOUVEAU BOUTON SE PLACE ICI (Dans le formulaire)
    choix_duree = st.selectbox(
        "Combien de temps voulez-vous surveiller ce site ?",
        options=["2 heures (Test)", "1 jour (24h)", "7 jours", "30 jours"]
    )
    
    activer = st.form_submit_button("Lancer la surveillance")

# --- LOGIQUE DU ROBOT EN CONTINU ---
if activer:
    st.success("🚀 Robot de surveillance démarré en continu !")
    
    # Conversion du choix textuel du client en vraies heures pour le script
    if choix_duree == "2 heures (Test)":
        heures_de_surveillance = 2
    elif choix_duree == "1 jour (24h)":
        heures_de_surveillance = 24
    elif choix_duree == "7 jours":
        heures_de_surveillance = 168
    else:
        heures_de_surveillance = 720  # 30 jours
    
    # Calcul automatique de l'heure d'arrêt
    heure_demarrage = datetime.datetime.now()
    heure_fin = heure_demarrage + datetime.timedelta(hours=heures_de_surveillance)
    
    st.info(f"⏳ Le robot fonctionnera en continu jusqu'au : {heure_fin.strftime('%Y-%m-%d %H:%M:%S')}")
    
    zone_logs = st.empty()
    zone_prix = st.empty()
    
    ancien_prix = None
    compteur_verif = 0
    
    # Boucle qui tourne tant qu'on n'a pas atteint la date de fin choisie
    while datetime.datetime.now() < heure_fin:
        compteur_verif += 1
        zone_logs.markdown(f"🔄 **Vérification en cours...** (Total de scans effectués : `{compteur_verif}`)")
        
        try:
            entetes = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            reponse = requests.get(url_site, headers=entetes, timeout=10)
            code_html = reponse.text
            
            resultat = re.search(r'(\d+[\.,]\d+)', code_html)
            
            if resultat:
                prix_actuel = resultat.group(1).strip() + " $"
                
                if ancien_prix is None:
                    ancien_prix = prix_actuel
                    zone_prix.info(f"🤖 Valeur initiale repérée : **{prix_actuel}**")
                elif prix_actuel != ancien_prix:
                    zone_prix.error(f"🚨 ALERTE : Le prix a changé ! {ancien_prix} -> **{prix_actuel}**")
                    ancien_prix = prix_actuel
                else:
                    zone_prix.success(f"😴 RAS : Le prix est stable à **{prix_actuel}**")
            else:
                zone_prix.warning("⚠️ Aucun format de prix détecté lors de ce scan.")
                
        except Exception as e:
            zone_prix.error(f"❌ Erreur de connexion au site : {e}")
        
        # Intervalle de 15 minutes entre chaque scan (900 secondes)
        time.sleep(900)
        
    st.warning("⏱️ Le temps de surveillance choisi est écoulé. Le robot s'est arrêté.")



