import smtplib
import os
import time
import datetime
import schedule
import feedparser
import pandas as pd
from fpdf import FPDF
from slack_sdk import WebClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from gpt4all import GPT4All
from dotenv import load_dotenv


# Charge les variables depuis .env
load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
GPT4ALL_PATH = os.getenv("GPT4ALL_PATH")

# -----------------------------
# --- Initialisation LLM local ---
# -----------------------------
# Remplace le chemin par ton fichier .bin GPT4All local
gpt_model = GPT4All(model_name=None, model_path=GPT4ALL_PATH)

def summarize_with_llm(text, max_tokens=150):
    prompt = f"Résume ce texte pour un radiologue de manière claire et concise :\n{text}"
    return gpt_model.generate(prompt, max_tokens=max_tokens)

# -----------------------------
# --- Agent 1: TechWatch ---
# -----------------------------
def techwatch_agent():
    urls = [
        "https://pubmed.ncbi.nlm.nih.gov/rss/search/1P5xyB4cY7nR?term=brain+tumor+MRI&limit=20&sort=date"
    ]
    articles = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            summary = summarize_with_llm(entry.summary)
            priority = 1 + int("AI" in entry.title or "deep learning" in entry.summary)
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary,
                "priority": priority
            })
    df = pd.DataFrame(articles).sort_values(by="priority", ascending=False)
    df.to_csv("techwatch_pro.csv", index=False)
    return df

# -----------------------------
# --- Agent 2: MarketWatch ---
# -----------------------------
def marketwatch_agent():
    competitors = [
        {"name": "BrainScanAI","status": "market", "funding": "5M€",
        "regulation": "FDA approved", "priority":3},
        {"name": "NeuroVision", "status": "preprod",
        "funding": "2M€", "regulation": "CE", "priority":2},
        {"name": "NeuroScanPro", "status": "R&D",
        "funding": "1M€", "regulation": "pending", "priority":1}
    ]
    df = pd.DataFrame(competitors).sort_values(by="priority", ascending=False)
    df.to_csv("marketwatch_pro.csv", index=False)
    return df

# -----------------------------
# --- Agent 3: PublicWatch ---
# -----------------------------
def publicwatch_agent():
    url = "https://www.boamp.fr/rss"
    feed = feedparser.parse(url)
    ao_list = []
    for entry in feed.entries[:10]:
        priority = 1
        if "IA" in entry.title or "imagerie" in entry.title:
            priority = 3
        ao_list.append({
            "title": entry.title,
            "link": entry.link,
            "date": entry.published,
            "priority": priority
        })
    df = pd.DataFrame(ao_list).sort_values(by="priority", ascending=False)
    df.to_csv("publicwatch_pro.csv", index=False)
    return df

# -----------------------------
# --- ReportGen PDF ---
# -----------------------------
def reportgen_agent(df_tech, df_market, df_public):
    today = datetime.date.today().strftime("%d-%m-%Y")
    # --- PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Rapport Veille IA Tumores Cérébrales - {today}", ln=True, align='C')

    # TechWatch
    pdf.set_font("Arial", 'B', 14)
    pdf.ln(5)
    pdf.cell(0,10,"1. Veille Technologique",ln=True)
    pdf.set_font("Arial",'',12)
    for _, row in df_tech.head(10).iterrows():
        pdf.multi_cell(0,6,f"- {row['title']} | Priority: {row['priority']}\nRésumé: {row['summary']}\nLien: {row['link']}\n")

    # MarketWatch
    pdf.set_font("Arial",'B',14)
    pdf.ln(5)
    pdf.cell(0,10,"2. Veille Concurrence",ln=True)
    pdf.set_font("Arial",'',12)
    for _, row in df_market.iterrows():
        pdf.multi_cell(0,6,f"- {row['name']} | Statut: {row['status']} | Financement: {row['funding']} | Régulation: {row['regulation']} | Priority: {row['priority']}")


    # PublicWatch
    pdf.set_font("Arial",'B',14)
    pdf.ln(5)
    pdf.cell(0,10,"3. Veille Marchés Publics",ln=True)
    pdf.set_font("Arial",'',12)
    for _, row in df_public.iterrows():
        pdf.multi_cell(0,6,f"- {row['title']} | Date: {row['date']} | Lien: {row['link']} | Priority: {row['priority']}")

    # Historique PDF
    reports_dir = "historique_reports"
    os.makedirs(reports_dir, exist_ok=True)
    pdf_path = os.path.join(reports_dir, f"weekly_report_{today}.pdf")
    pdf.output(pdf_path)
    print(f"PDF généré ✅ {pdf_path}")

    return pdf_path

# -----------------------------
# --- Alertes Email / Slack ---
# -----------------------------
def send_email_alert(pdf_path, sender, receiver, smtp_server, smtp_port, password):
    subject = "Rapport hebdomadaire veille IA - tumeurs cérébrales"
    body = "Le rapport hebdomadaire est disponible en pièce jointe."
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body,'plain'))

    with open(pdf_path,'rb') as f:
        part = MIMEBase('application','octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',f"attachment; filename={pdf_path}")
    msg.attach(part)

    server = smtplib.SMTP(smtp_server,smtp_port)
    server.starttls()
    server.login(sender,password)
    server.sendmail(sender,receiver,msg.as_string())
    server.quit()
    print("Email envoyé ✅")

def send_slack_alert(pdf_path, slack_token, channel="#general"):
    client = WebClient(token=slack_token)
    client.files_upload(channels=channel, file=pdf_path, title="Rapport veille IA")
    print("Slack alert envoyé ✅")

# -----------------------------
# --- Scheduler hebdo ---
# -----------------------------
def run_weekly_veille_pro():
    print("Démarrage veille hebdomadaire PRO...")
    df_tech = techwatch_agent()
    df_market = marketwatch_agent()
    df_public = publicwatch_agent()
    pdf_path = reportgen_agent(df_tech, df_market, df_public)

    # Envoi alertes
    send_email_alert(pdf_path, SMTP_EMAIL, "destinataire@example.com", SMTP_SERVER, SMTP_PORT, SMTP_PASSWORD)
    send_slack_alert(pdf_path, SLACK_TOKEN)
    print("Veille hebdomadaire PRO terminée ✅")

# Lancement scheduler chaque lundi à 9h
schedule.every().monday.at("09:00").do(run_weekly_veille_pro)

while True:
    schedule.run_pending()
    time.sleep(60)
