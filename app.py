import streamlit as st
import requests
import re
import time
import datetime
import resend

# 🔑 TA CLÉ DE COURRIEL GRATUITE (À obtenir sur resend.com)
resend.api_key = "re_123456789" 

st.set_page_config(page_title="Alerte Prix Pro", page_icon="🤖")
st.title("🤖 Moniteur de Prix pour Entreprises")

# --- 🧠 SYSTÈME DE MÉMOIRE CACHÉE (SESSION STATE) ---
# Si la mémoire de connexion n'existe pas encore, on la crée à "Faux"
if "connecte" not in st.session_state:
    st.session_state.connecte = False

# Si le client n'est pas encore connecté, on affiche le formulaire de clé
if not st.session_state.connecte:
    with st.form("form_securite"):
        st.subheader("🔑 Activation du logiciel")
        mot_de_passe_client = st.text_input("Entrez votre clé d'activation client :", type="password")
        bouton_connexion = st.form_submit_button("Déverrouiller le robot")

    cles_valides = ["Client_Alex94", "Client_BoutiquePro", "FleuristeMontreal", "MonPremierTest"]

    if bouton_connexion:
        if mot_de_passe_client in cles_valides:
            st.session_state.connecte = True  # 🔓 On enregistre dans la mémoire que c'est BON
            st.rerun()  # On recharge la page immédiatement pour afficher le robot
        else:
            st.error("⚠️ Clé d'activation invalide ou expirée.")
    
    st.stop()  # On arrête le code ici tant que st.session_state.connecte est Faux

# --- 2. TABLEAU DE BORD DU CLIENT (S'affiche uniquement si connecté est Vrai) ---
st.success("🔓 Clé d'activation valide ! Bienvenue sur votre tableau de bord.")

# Bouton de déconnexion pour le client (optionnel mais professionnel)
if st.button("🔴 Se déconnecter"):
    st.session_state.connecte = False
    st.rerun()

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
    
    if choix_duree == "2 heures (Test)":
        heures_de_surveillance = 2
    elif choix_duree == "1 jour (24h)":
        heures_de_surveillance = 24
    elif choix_duree == "7 jours":
        heures_de_surveillance = 168
    else:
        heures_de_surveillance = 720
    
    heure_fin = datetime.datetime.now() + datetime.timedelta(hours=heures_de_surveillance)
    st.info(f"⏳ Le robot fonctionnera en continu jusqu'au : {heure_fin.strftime('%Y-%m-%d %H:%M:%S')}")
    
    zone_logs = st.empty()
    zone_prix = st.empty()
    
    ancien_prix = None
    compteur_verif = 0
    
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
        
        # Mis à 10 secondes pour te laisser tester la boucle sans attendre 15 minutes
        time.sleep(10)
        
    st.warning("⏱️ Le temps de surveillance choisi est écoulé. Le robot s'est arrêté.")
