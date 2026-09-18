import os
import requests

# ================= CONFIGURAÇÕES DO ALVO =================
# Username do perfil do Stripchat que você quer monitorar
STREAMER_USERNAME = "Alissaasex" 

# URL da API do Stripchat para checar o status do modelo
STRIPCHAT_API_URL = f"https://stripchat.com{STREAMER_USERNAME}/cam"

# ================= CREDENCIAIS SEGURAS DO TELEGRAM =================
# O GitHub Actions vai preencher essas variáveis automaticamente usando os seus "Segredos" guardados.
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Arquivo temporário para salvar o último estado e evitar spam de mensagens
STATUS_FILE = "last_status.txt"

def get_last_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return f.read().strip()
    return "offline"

def set_last_status(status):
    with open(STATUS_FILE, "w") as f:
        f.write(status)

def check_live():
    # User-Agent finge que a requisição está vindo de um navegador comum para evitar bloqueios
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(STRIPCHAT_API_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Puxa a informação se está ao vivo direto do sistema do Stripchat
            is_live = data.get("model", {}).get("isLive", False)
            current_status = "online" if is_live else "offline"
            
            last_status = get_last_status()
            
            # Se o status mudou de offline para online, dispara o gatilho
            if current_status == "online" and last_status == "offline":
                send_telegram_message()
                
            set_last_status(current_status)
            print(f"Checagem concluída. Status atual: {current_status}")
        elif response.status_code == 404:
            print(f"Erro: Usuário '{STREAMER_USERNAME}' não foi encontrado no Stripchat.")
        else:
            print(f"Erro ao acessar API do Stripchat. Código de status: {response.status_code}")
    except Exception as e:
        print(f"Falha na conexão com a API: {e}")

def send_telegram_message():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: As credenciais do Telegram não foram encontradas nas variáveis de ambiente do GitHub.")
        return
        
    text_message = f"🚨 **{STREAMER_USERNAME}** está **AO VIVO** no Stripchat agora! 🚨\n\n👉 https://stripchat.com{STREAMER_USERNAME}"
    
    # URL oficial da API do Telegram para envio de mensagens
    telegram_url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text_message,
        "parse_mode": "Markdown" # Permite usar negritos no texto
    }
    
    try:
        res = requests.post(telegram_url, json=payload)
        if res.status_code == 200:
            print("Notificação enviada com sucesso para o Telegram!")
        else:
            print(f"Erro ao enviar mensagem para o Telegram: {res.text}")
    except Exception as e:
        print(f"Falha ao conectar com o servidor do Telegram: {e}")

if __name__ == "__main__":
    check_live()
