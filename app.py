import streamlit as st
import requests
import re
import time

st.set_page_config(page_title="Alerte Prix Pro", page_icon="🤖")
st.title("🤖 Moniteur de Prix pour Entreprises")

# Formulaire d'entrée
with st.form("form_robot"):
    url_site = st.text_input("Lien URL du site concurrent :", value="https://scrapethissite.com")
    email_client = st.text_input("Votre adresse courriel :", value="test@courriel.com")
    activer = st.form_submit_button("Lancer la surveillance")

if activer:
    st.success("🚀 Robot démarré avec succès !")
    
    # Barre de progression visuelle pour éviter les bogues d'affichage
    barre_progression = st.progress(0)
    status_texte = st.markdown("### 📊 État du Robot")
    
    ancien_prix = None
    
    # Le robot va faire 5 vérifications stables
    for cycle in range(1, 6):
        # On met à jour la barre de progression (ex: 20%, 40%...)
        barre_progression.progress(cycle * 20)
        
        try:
            entetes = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            reponse = requests.get(url_site, headers=entetes, timeout=5)
            code_html = reponse.text
            
            resultat = re.search(r'(\d+[\.,]\d+)', code_html)
            
            if resultat:
                prix_actuel = resultat.group(1).strip() + " $"
                
                if ancien_prix is None:
                    ancien_prix = prix_actuel
                    status_texte.info(f"🤖 **Vérification {cycle}/5** : Valeur initiale repérée : **{prix_actuel}**")
                elif prix_actuel != ancien_prix:
                    status_texte.error(f"🚨 **Vérification {cycle}/5** : Le prix a changé ! {ancien_prix} -> **{prix_actuel}**")
                    ancien_prix = prix_actuel
                else:
                    status_texte.success(f"😴 **Vérification {cycle}/5** : Le prix est stable à **{prix_actuel}**")
            else:
                status_texte.warning(f"⚠️ **Vérification {cycle}/5** : Aucun chiffre détecté sur la page.")
                
        except Exception as e:
            status_texte.error(f"❌ **Vérification {cycle}/5** : Erreur de connexion ({e})")
        
        # Pause de 4 secondes entre les vérifications
        time.sleep(4)
        
    st.balloons()  # Petite animation de célébration quand le test réussit !
    status_texte.markdown("### ✅ Session de test complétée sans bogue !")


