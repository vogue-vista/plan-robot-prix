import streamlit as st
import requests
import re
import time
import datetime
import resend  # Outil officiel d'envoi de courriels

# 🔑 CONFIGURATION DE LA CLÉ DE COURRIEL GRATUITE
# Vous obtiendrez cette clé en ouvrant un compte gratuit sur resend.com
resend.api_key = re_K6dKkydS_8sy3ProUZZEm393JvLj1WSRR

st.set_page_config(page_title="Alerte Prix Pro", page_icon="🤖")
st.title("🤖 Moniteur de Prix pour Entreprises")

# --- SYSTÈME DE CLÉS UNIQUES ---
mot_de_passe_client = st.text_input("Entrez votre clé d'activation client :", type="password")
cles_valides = ["Client_Alex94", "Client_BoutiquePro", "FleuristeMontreal", "MonPremierTest"]

if mot_de_passe_client not in cles_valides:
    st.warning("⚠️ Clé d'activation invalide ou expirée.")
    st.stop()

# --- FORMULAIRE DU CLIENT ---
with st.form("form_robot"):
    url_site = st.text_input("Lien URL du site concurrent :", value="https://scrapethissite.com")
    email_client = st.text_input("Votre adresse courriel pour recevoir l'alerte :")
    
    choix_duree = st.selectbox(
        "Combien de temps voulez-vous surveiller ce site ?",
        options=["2 heures (Test)", "1 jour (24h)", "7 jours", "30 jours"]
    )
    activer = st.form_submit_button("Lancer la surveillance")

# --- LOGIQUE DU ROBOT ET ALERTES ---
if activer:
    if not email_client:
        st.error("❌ Vous devez entrer votre adresse courriel pour recevoir les alertes !")
        st.stop()
        
    st.success(f"🚀 Robot en ligne ! Les alertes seront envoyées à : {email_client}")
    
    if choix_duree == "2 heures (Test)":
        heures_de_surveillance = 2
    elif choix_duree == "1 jour (24h)":
        heures_de_surveillance = 24
    elif choix_duree == "7 jours":
        heures_de_surveillance = 168
    else:
        heures_de_surveillance = 720
    
    heure_fin = datetime.datetime.now() + datetime.timedelta(hours=heures_de_surveillance)
    barre_progression = st.progress(0)
    status_texte = st.markdown("### 📊 État du Robot")
    
    ancien_prix = None
    compteur = 0
    
    while datetime.datetime.now() < heure_fin:
        compteur += 1
        try:
            entetes = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            reponse = requests.get(url_site, headers=entetes, timeout=10)
            code_html = reponse.text
            
            resultat = re.search(r'(\d+[\.,]\d+)', code_html)
            
            if resultat:
                prix_actuel = resultat.group(1).strip() + " $"
                
                if ancien_prix is None:
                    ancien_prix = prix_actuel
                    status_texte.info(f"🤖 **Scan #{compteur}** : Valeur initiale repérée : **{prix_actuel}**")
                
                elif prix_actuel != ancien_prix:
                    status_texte.error(f"🚨 **Scan #{compteur}** : LE PRIX A CHANGÉ ! {ancien_prix} -> **{prix_actuel}**")
                    
                    # 📧 DÉCLENCHEMENT DU VRAI COURRIEL AUTOMATIQUE
                    try:
                        resend.Emails.send({
                            "from": "Robot Prix <onboarding@resend.dev>",
                            "to": email_client,
                            "subject": "🚨 Alerte : Un concurrent a changé ses prix !",
                            "html": f"""
                            <h3>Changement de prix détecté !</h3>
                            <p>Le robot vient de repérer une modification sur le site : {url_site}</p>
                            <p><b>Ancien prix :</b> {ancien_prix}</p>
                            <p><b>Nouveau prix :</b> {prix_actuel}</p>
                            <br>
                            <p><i>Généré automatiquement par votre Robot de Prix à 30$.</i></p>
                            """
                        })
                        st.toast("📧 Courriel envoyé dans votre boîte de réception !")
                    except Exception as error_mail:
                        st.sidebar.error(f"Erreur d'envoi du message : {error_mail}")
                    
                    ancien_prix = prix_actuel
                else:
                    status_texte.success(f"😴 **Scan #{compteur}** : Le prix est stable à **{prix_actuel}**")
            else:
                status_texte.warning(f"⚠️ **Scan #{compteur}** : Aucun format numérique détecté.")
                
        except Exception as e:
            status_texte.error(f"❌ Erreur : {e}")
            
        time.sleep(900)  # Pause de 15 minutes entre chaque analyse
