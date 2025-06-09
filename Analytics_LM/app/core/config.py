from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Configurações da API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Analytics Genesys Cloud"
    
    # Configurações da Genesys Cloud
    GENESYS_CLIENT_ID: str = os.getenv("GENESYS_CLIENT_ID")
    GENESYS_CLIENT_SECRET: str = os.getenv("GENESYS_CLIENT_SECRET")
    GENESYS_ENVIRONMENT: str = os.getenv("GENESYS_ENVIRONMENT")
    
    # Configurações do Power BI
    POWERBI_CLIENT_ID: str = os.getenv("POWERBI_CLIENT_ID")
    POWERBI_CLIENT_SECRET: str = os.getenv("POWERBI_CLIENT_SECRET")
    POWERBI_TENANT_ID: str = os.getenv("POWERBI_TENANT_ID")
    
    # Configurações do Banco de Dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./analytics.db")
    
    # Configurações da Aplicação
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Configurações de Filas
    QUEUES = {
        "whatsapp_entrega": "Ativo - WhatsApp Gestão da Entrega",
        "whatsapp_marketplace": "Ativo WhatsApp Marketplace",
        "whatsapp_qualidade": "Ativo WhatsApp Qualidade",
        "whatsapp_voz_cliente": "Ativo WhatsApp Voz do Cliente",
        "calm_whatsapp": "CALM - WhatsApp",
        "calm_concierge": "CALM_CONCIERGE",
        "calm_concierge_whatsapp": "CALM_CONCIERGE_WHATSAPP",
        "fila_calm": "FILA_CALM",
        "fila_calm_rechamada": "FILA_CALM_RECHAMADA",
        "fila_calm_rechamada_whatsapp": "FILA_CALM_RECHAMADA_WHATSAPP",
        "instalador_ge": "INSTALADOR_GE",
        "transporte_ge": "TRANSPORTE_GE",
        "loja_ge": "LOJA_GE"
    }
    
    # Configurações de Autosserviço
    AUTOSERVICE = [
        "2° Via de nota Fiscal",
        "2° Via de boleto faturado",
        "Status de pedido",
        "Cancelamento",
        "Comprovante de Estorno",
        "Código de rastreio",
        "Correção de nota fiscal",
        "Alteração cadastral"
    ]
    
    # Configurações de Atualização
    UPDATE_INTERVAL: int = 60  # segundos
    
    class Config:
        case_sensitive = True

settings = Settings() 