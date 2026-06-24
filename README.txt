# Interface pour l'Adaptation de l'Impédance avec PicoVNA

Ce projet consiste en la réalisation d'une interface web permettant de piloter un analyseur de réseau vectoriel (PicoVNA) afin d'automatiser la mesure des paramètres S (S11,S12,S21,S22) et de faciliter les calculs liés à l'adaptation d'impédance en haute fréquence.

L'application utilise un backend Python Flask qui communique avec le SDK natif du PicoVNA (via une DLL C++), et une interface utilisateur dynamique en HTML/JavaScript utilisant la bibliothèque Plotly pour l'affichage en temps réel.

## 🚀 Fonctionnalités

*   Connexion au PicoVNA : Détection automatique et initialisation de l'appareil via le SDK.
*   Configuration du balayage (Sweep) :** Paramétrage de la plage de fréquences (de 1 MHz à 3 GHz par défaut, sur 201 points).
*   Mesure en temps réel : Récupération instantanée des données complexes (parties réelles et imaginaires) pour les 4 paramètres S.
*   Visualisation graphique : Affichage interactif des amplitudes en décibels (dB) pour S11, S21, S12, et S22.
*   Outils de calcul HF : Fonctions prêtes pour la conversion du coefficient de réflexion en impédance.

---

## 📁 Structure du Projet

```text
├── app.py                  # Serveur Flask principal (Backend API)
├── pico_vna.py             # Wrapper Python (ctypes) pour le SDK du PicoVNA
├── impedance.py            # Fonctions de calculs mathématiques et d'impédance
├── sdk/
│   └── vna.dll             # Bibliothèque dynamique native du constructeur
│   └── vna.lib
│   └── vna.py
│   └── vna_python.lib
│   └── docopt.dll
│   └── ftd2xx.dll
├── templates/
│   └── index.html          # Interface utilisateur (Frontend)
└── static/
    └── js/
        └── app.js          # Logique de requêtage asynchrone et traçage Plotly