# <p align="center">Création de rapport de Veilles</p>

## Description

Ce projet est une plateforme de veille technologique, concurrentielle et marchés publics pour les tumeurs cérébrales en imagerie médicale. 
Le système utilise l’IA locale (GPT4All) pour résumer automatiquement les publications et générer un rapport PDF hebdomadaire. 
Les alertes sont envoyées par email et Slack, et le tout est planifié automatiquement chaque semaine.

## Fonctionnalités principales

- TechWatch : veille sur PubMed (brain tumor, MRI) avec résumé automatique via GPT4All
- MarketWatch : suivi des concurrents et startups dans le domaine de l’IA médicale
- PublicWatch : veille sur les appels d’offres et marchés publics liés à l’imagerie médicale
- Rapports PDF : génération d’un rapport PDF complet et sauvegarde dans `historique_reports/`
- Alertes : envoi automatique du PDF par email et Slack
- Scheduler hebdomadaire : exécution chaque lundi à 9h

## 📁 Structure du projet
```bash
├─ veille.py             # Script principal
├─ requirements.txt      # Packages Python requis
├─ README.md             # Documentation complète
├─ .gitignore            # Fichiers à ignorer
├─ .env.example          # Exemple de fichier .env
├─ historique_reports/   # Rapports PDF générés (non versionnés)
````

## 🚀 Installation

### 1. Cloner le projet :
```bash
git clone <url-du-repo>
cd Veille
```

### 2. Créer un environnement virtuel :
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Configuration .env

Créer un fichier .env à partir de .env.example et remplir vos informations :
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```
Remplir les valeurs réelles : email, mot de passe App Gmail, token Slack, chemin du modèle GPT4All.

## Installation du modèle GPT4All local

Le projet utilise le modèle **GPT4All 13B Snoozy** pour résumer automatiquement les publications. 
Voici comment l’obtenir et l’intégrer :

### 1. Télécharger le modèle

- Option 1 : **Téléchargement direct** depuis le site officiel :  
  🔗 [ggml-gpt4all-l13b-snoozy.bin](https://gpt4all.io/models/ggml-gpt4all-l13b-snoozy.bin)  

- Option 2 : **Via GPT4All Desktop**  
  1. Installer GPT4All Desktop ([docs.gpt4all.io](https://docs.gpt4all.io/gpt4all_desktop/quickstart.html))  
  2. Dans l’interface, sélectionner le modèle **GPT4All‑13B Snoozy** et télécharger  
  3. Le fichier `.bin` sera ajouté sur ton PC  

> ⚠️ Le modèle pèse plusieurs gigaoctets (~7 Go), prévois un téléchargement long.

### 2. Placer le modèle

- Exemple sur Windows :  
```bash
C:\Users\ton_nom\Documents\Models\ggml-gpt4all-l13b-snoozy.bin
```
- Exemple sur Mac/Linux :
```bash
/Users/ton_nom/Documents/Models/ggml-gpt4all-l13b-snoozy.bin
```

## Utilisation

Lancer le script principal :
```bash
python veille.py
```
- Génère un PDF dans historique_reports/
- Envoie le PDF par email et Slack
- Scheduler hebdo (lundi 9h)

## Sécurité

- .env contient toutes les informations sensibles

- .gitignore protège ces fichiers et les fichiers temporaires

- GPT4All fonctionne 100% local

## 📬 Contact

Pour toute question, suggestion ou contribution :

- 📧 matthieu.graziani007@gmail.com
- 🌐 www.linkedin.com/in/matthieu-graziani-4190b526b 