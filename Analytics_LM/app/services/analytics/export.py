from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import json
from app.models.interaction import Interaction, CSAT, HSM, SpeechAnalytics, AgentMetrics, QueueMetrics

class ExportService:
    @staticmethod
    def export_interactions_to_excel(
        interactions: List[Interaction],
        output_path: str
    ) -> str:
        """
        Exporta interações para Excel
        """
        df = pd.DataFrame([{
            "ID": i.id,
            "Data": i.start_time,
            "Fila": i.queue_id,
            "Cliente": i.customer_id,
            "Operador": i.agent_id,
            "Canal": i.channel_type,
            "Duração": i.duration,
            "Tempo de Espera": i.wait_time,
            "Tempo de Conversação": i.talk_time,
            "Status": i.status,
            "Auto Serviço": i.is_auto_service,
            "Tipo Auto Serviço": i.auto_service_type,
            "Rechamada": i.is_callback,
            "Motivo Rechamada": i.callback_reason,
            "Canal Duplicado": i.is_duplicate_channel
        } for i in interactions])
        
        df.to_excel(output_path, index=False)
        return output_path

    @staticmethod
    def export_csat_to_excel(
        csat_scores: List[CSAT],
        output_path: str
    ) -> str:
        """
        Exporta scores CSAT para Excel
        """
        df = pd.DataFrame([{
            "ID Interação": s.interaction_id,
            "Data": s.created_at,
            "Fila": s.queue_id,
            "CPF/CNPJ": s.customer_id,
            "Nome do Agente": s.agent_id,
            "Supervisor": s.supervisor_id,
            "Canal": s.channel_type,
            "Explicação Clara": s.clarity_score,
            "Nota Atendimento": s.score,
            "Nota Navegação": s.navigation_score,
            "Nota Espera": s.wait_time_score,
            "Campo Aberto": s.open_feedback
        } for s in csat_scores])
        
        df.to_excel(output_path, index=False)
        return output_path

    @staticmethod
    def export_hsm_to_excel(
        hsm_messages: List[HSM],
        output_path: str
    ) -> str:
        """
        Exporta mensagens HSM para Excel
        """
        df = pd.DataFrame([{
            "Data/Hora": m.sent_at,
            "Celular": m.customer_id,
            "Nome": m.customer_name,
            "Data/Hora Envio": m.sent_at,
            "Data/Hora Recebido": m.delivered_at,
            "Data/Hora Lido": m.read_at,
            "Template": m.template_id,
            "Mensagem": m.message,
            "Status": m.status,
            "E-mail Remetente": m.sender_email
        } for m in hsm_messages])
        
        df.to_excel(output_path, index=False)
        return output_path

    @staticmethod
    def export_speech_analytics_to_excel(
        speech_data: List[SpeechAnalytics],
        output_path: str
    ) -> str:
        """
        Exporta dados de Speech Analytics para Excel
        """
        df = pd.DataFrame([{
            "ID Interação": s.interaction_id,
            "Fila": s.queue_id,
            "Data": s.created_at,
            "Tópico": s.topic,
            "Canal": s.channel_type,
            "Operador": s.agent_id,
            "Confiança": s.confidence,
            "Transcrição": s.transcript,
            "Score Sentimento": s.sentiment_score
        } for s in speech_data])
        
        df.to_excel(output_path, index=False)
        return output_path

    @staticmethod
    def export_agent_metrics_to_excel(
        agent_metrics: List[AgentMetrics],
        output_path: str
    ) -> str:
        """
        Exporta métricas de agentes para Excel
        """
        df = pd.DataFrame([{
            "Agente": m.agent_id,
            "Data": m.date,
            "Total Interações": m.total_interactions,
            "Interações Atendidas": m.answered_interactions,
            "TMA": m.average_handle_time,
            "TME": m.average_wait_time,
            "Tempo Conversação": m.average_talk_time,
            "Nível Serviço": m.service_level,
            "Nota CSAT": m.csat_score
        } for m in agent_metrics])
        
        df.to_excel(output_path, index=False)
        return output_path

    @staticmethod
    def export_queue_metrics_to_excel(
        queue_metrics: List[QueueMetrics],
        output_path: str
    ) -> str:
        """
        Exporta métricas de filas para Excel
        """
        df = pd.DataFrame([{
            "Fila": m.queue_id,
            "Data": m.date,
            "Total Interações": m.total_interactions,
            "Interações Atendidas": m.answered_interactions,
            "Interações Abandonadas": m.abandoned_interactions,
            "TME": m.average_wait_time,
            "Nível Serviço": m.service_level
        } for m in queue_metrics])
        
        df.to_excel(output_path, index=False)
        return output_path

    @staticmethod
    def export_to_json(
        data: List[Dict],
        output_path: str
    ) -> str:
        """
        Exporta dados para JSON
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return output_path

    @staticmethod
    def export_to_csv(
        data: List[Dict],
        output_path: str
    ) -> str:
        """
        Exporta dados para CSV
        """
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        return output_path 