import streamlit as st
import requests
import re
import time
import datetime
import resend  # Bibliothèque pour envoyer les vrais courriels

# 🔑 TA CLÉ DE COURRIEL GRATUITE (À obtenir sur resend.com)
# Remplace "re_123456789" par ta vraie clé pour activer les envois
resend.api_key = "re_123456789" 

st.set_page_config(page_title="Alerte Prix Pro", page_icon="🤖")
st.title("🤖 Moniteur de Prix pour Entreprises")

# --- 1. INTERFACE DE SÉCURITÉ CLIENT (STABILISÉE) ---
with st.form("form_securite"):
    st.subheader("🔑 Activation du logiciel")
    mot_de_passe_client = st.text_input("Entrez votre clé d'activation client :", type="password")
    bouton_connexion = st.form_submit_button("Déverrouiller le robot")

# Liste de tes clients autorisés à utiliser l'application
cles_valides = ["Client_Alex94", "Client_BoutiquePro", "FleuristeMontreal", "MonPremierTest"]

# Bloquer le site tant que le mot de passe n'est pas validé
if not bouton_connexion or mot_de_passe_client not in cles_valides:
    if bouton_connexion and mot_de_passe_client not in cles_valides:
        st.error("⚠️ Clé d'activation invalide ou expirée.")
    else:
        st.warning("🔒 Veuillez entrer votre clé pour débloquer l'interface.")
    st.stop()  # Arrête le chargement ici

# --- 2. TABLEAU DE BORD DU CLIENT (S'affiche après connexion) ---
st.success("🔓 Clé d'activation valide ! Bienvenue sur votre tableau de bord.")

with st.form("form_robot"):
    url_site = st.text_input("Lien URL du site concurrent :", value="https://scrapethissite.com")
    email_client = st.text_input("Votre adresse courriel pour recevoir les alertes :", value="test@courriel.com")
    
    choix_duree = st.selectbox(
        "Combien de temps voulez-vous surveiller ce site ?",
        options=["2 heures (Test)", "1 jour (24h)", "7 jours", "30 jours"]
    )
    
    activer = st.form_submit_button("Lancer la surveillance")

# --- 3. LOGIQUE DU ROBOT ET ALERTES EN CONTINU ---
if activer:
    if not url_site or not email_client:
        st.error("❌ Veuillez remplir tous les champs du formulaire.")
        st.stop()
        
    st.success("🚀 Robot de surveillance démarré en continu !")
    
    # Conversion du choix du client en heures réelles
    if choix_duree == "2 heures (Test)":
        heures_de_surveillance = 2
    elif choix_duree == "1 jour (24h)":
        heures_de_surveillance = 24
    elif choix_duree == "7 jours":
        heures_de_surveillance = 168
    else:
        heures_de_surveillance = 720  # 30 jours
    
    # Calcul automatique du chrono de fin
    heure_fin = datetime.datetime.now() + datetime.timedelta(hours=heures_de_surveillance)
    st.info(f"⏳ Le robot fonctionnera en continu jusqu'au : {heure_fin.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Zones fixes pour éviter les bogues d'affichage visuel
    zone_logs = st.empty()
    zone_prix = st.empty()
    
    ancien_prix = None
    compteur_verif = 0
    
    # La boucle tourne tant qu'on n'a pas dépassé l'heure de fin
    while datetime.datetime.now() < heure_fin:
        compteur_verif += 1
        zone_logs.markdown(f"🔄 **Vérification en cours...** (Total de scans effectués : `{compteur_verif}`)")
        
        try:
            # En-têtes pour faire croire au site qu'on est un humain sur Chrome
            entetes = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            reponse = requests.get(url_site, headers=entetes, timeout=10)
            code_html = reponse.text
            
            # Recherche du prix
            resultat = re.search(r'(\d+[\.,]\d+)', code_html)
            
            if resultat:
                prix_actuel = resultat.group(1).strip() + " $"
                
                if ancien_prix is None:
                    ancien_prix = prix_actuel
                    zone_prix.info(f"🤖 Valeur initiale repérée : **{prix_actuel}**")
                
                # SI LE PRIX A CHANGÉ : ON DÉCLENCHE L'ALERTE VISUELLE ET LE COURRIEL
                elif prix_actuel != ancien_prix:
                    zone_prix.error(f"🚨 ALERTE : Le prix a changé ! {ancien_prix} -> **{prix_actuel}**")
                    
                    # Envoi du vrai courriel automatique au client
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
                            <p><i>Généré automatiquement par votre Robot de Prix à 30$/mois.</i></p>
                            """
                        })
                        st.toast("📧 Courriel d'alerte envoyé avec succès !")
                    except Exception as error_mail:
                        st.sidebar.error(f"Erreur d'envoi du courriel : {error_mail}")
                    
                    ancien_prix = prix_actuel
                else:
                    zone_prix.success(f"😴 RAS : Le prix est stable à **{prix_actuel}**")
            else:
                zone_prix.warning("⚠️ Aucun format de prix détecté lors de ce scan.")
                
        except Exception as e:
            zone_prix.error(f"❌ Erreur de connexion au site : {e}")
        
        # ⏱️ INTERVALLE DE 15 MINUTES (900 secondes)
        # Note : Pour faire des tests rapides, tu peux changer 900 par 10 temporairement.
        time.sleep(900)
        
    st.warning("⏱️ Le temps de surveillance choisi est écoulé. Le robot s'est arrêté.")
