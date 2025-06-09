from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.models.interaction import Interaction, CSAT, HSM, SpeechAnalytics, AgentMetrics, QueueMetrics

class MetricsService:
    @staticmethod
    def get_total_customers(interactions: List[Interaction]) -> int:
        """
        Calcula a quantidade de clientes únicos que nos acionaram (Contagem por CPF ou CNPJ)
        """
        return len(set(i.customer_id for i in interactions if i.customer_id))

    @staticmethod
    def get_total_received_calls(interactions: List[Interaction]) -> int:
        """
        Calcula a quantidade de Chamadas recebidas (Voz e Texto)
        """
        return len(interactions)

    @staticmethod
    def get_total_answered_calls(interactions: List[Interaction]) -> int:
        """
        Calcula a quantidade de Chamadas Atendidas (Voz e Texto)
        """
        return len([i for i in interactions if i.status == "answered"])

    @staticmethod
    def calculate_service_level(interactions: List[Interaction], target_seconds: int = 20) -> float:
        """
        Calcula o nível de serviço (SL) para as interações
        SL = (Chamadas atendidas dentro do tempo alvo / Total de chamadas) * 100
        """
        if not interactions:
            return 0.0
            
        answered_calls = [i for i in interactions if i.status == "answered"]
        if not answered_calls:
            return 0.0
            
        calls_within_target = len([
            i for i in answered_calls 
            if i.wait_time is not None and i.wait_time <= target_seconds
        ])
        
        return (calls_within_target / len(answered_calls)) * 100 if len(answered_calls) > 0 else 0.0

    @staticmethod
    def calculate_aht(interactions: List[Interaction]) -> float:
        """
        Calcula o Tempo Médio de Atendimento (AHT)
        AHT = (Tempo total de conversação + Tempo total de espera) / Número de chamadas atendidas
        (Em segundos, converter para minutos na exibição)
        """
        if not interactions:
            return 0.0
            
        answered_calls = [i for i in interactions if i.status == "answered"]
        if not answered_calls:
            return 0.0
            
        total_talk_time = sum(i.talk_time if i.talk_time is not None else 0 for i in answered_calls)
        total_wait_time = sum(i.wait_time if i.wait_time is not None else 0 for i in answered_calls)
        
        return (total_talk_time + total_wait_time) / len(answered_calls)

    @staticmethod
    def calculate_awt(interactions: List[Interaction]) -> float:
        """
        Calcula o Tempo Médio de Espera (TME)
        TME = Tempo total de espera / Número de chamadas atendidas
        (Em segundos, converter para minutos na exibição)
        """
        if not interactions:
            return 0.0
            
        answered_calls = [i for i in interactions if i.status == "answered"]
        if not answered_calls:
            return 0.0
            
        total_wait_time = sum(i.wait_time if i.wait_time is not None else 0 for i in answered_calls)
        return total_wait_time / len(answered_calls)

    @staticmethod
    def calculate_att(interactions: List[Interaction]) -> float:
        """
        Calcula o Tempo Médio de Conversação (TCM)
        TCM = Tempo total de conversação / Número de chamadas atendidas
        (Em segundos, converter para minutos na exibição)
        """
        if not interactions:
            return 0.0
            
        answered_calls = [i for i in interactions if i.status == "answered"]
        if not answered_calls:
            return 0.0
            
        total_talk_time = sum(i.talk_time if i.talk_time is not None else 0 for i in answered_calls)
        return total_talk_time / len(answered_calls)

    @staticmethod
    def get_logged_in_agents(interactions: List[Interaction]) -> int:
        """
        Calcula a quantidade de HCs (Agentes Logados no período)
        Considera agentes que participaram de interações atendidas.
        """
        return len(set(i.agent_id for i in interactions if i.agent_id and i.status == "answered"))

    @staticmethod
    def get_auto_service_interactions(interactions: List[Interaction]) -> int:
        """
        Calcula a quantidade de interações retidas no auto serviço
        """
        return len([i for i in interactions if i.is_auto_service])

    @staticmethod
    def get_top_reasons(interactions: List[Interaction], top_n: int = 10) -> Dict[str, int]:
        """
        Obtém os motivos selecionados pelo cliente no Bot ou URA (Top N)
        """
        reason_counts = {}
        for i in interactions:
            if i.reason:
                reason_counts[i.reason] = reason_counts.get(i.reason, 0) + 1
        
        sorted_reasons = sorted(reason_counts.items(), key=lambda item: item[1], reverse=True)
        return dict(sorted_reasons[:top_n])

    @staticmethod
    def get_total_callbacks(interactions: List[Interaction]) -> int:
        """
        Calcula a quantidade de Rechamadas (Total de clientes que nos acionam mais de 1x)
        (Lógica simplificada: conta interações marcadas como is_callback)
        """
        return len([i for i in interactions if i.is_callback])

    @staticmethod
    def get_duplicate_channel_interactions(interactions: List[Interaction]) -> int:
        """
        Calcula interações finalizadas por duplicidade de canal (Voz ou Texto)
        """
        return len([i for i in interactions if i.is_duplicate_channel])

    @staticmethod
    def get_interactions_volume_by_period(interactions: List[Interaction], period: str = "H") -> Dict:
        """
        Retorna o volume de clientes e chamadas por período (H=hora, D=dia).
        """
        if not interactions:
            return {"timestamps": [], "total_customers": [], "total_received_calls": [], "total_answered_calls": []}
        
        df = pd.DataFrame([i.__dict__ for i in interactions])
        df['start_time'] = pd.to_datetime(df['start_time'])
        df = df.set_index('start_time')

        # Agrupar por período
        if period == "H":
            resampled = df.resample('H')
        elif period == "D":
            resampled = df.resample('D')
        else:
            raise ValueError("Período inválido. Use 'H' para hora ou 'D' para dia.")

        # Volume de chamadas recebidas
        received_calls = resampled.size().fillna(0)

        # Volume de chamadas atendidas
        answered_calls = resampled.apply(lambda x: len([i for i in x.status if i == "answered"])).fillna(0)
        
        # Total de clientes (contagem única por período)
        total_customers = resampled['customer_id'].apply(lambda x: len(x.unique())).fillna(0)

        return {
            "timestamps": received_calls.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            "total_customers": total_customers.tolist(),
            "total_received_calls": received_calls.tolist(),
            "total_answered_calls": answered_calls.tolist()
        }

    @staticmethod
    def get_tma_tme_by_period(interactions: List[Interaction], period: str = "H") -> Dict:
        """
        Retorna TMA e TME por período (H=hora, D=dia).
        """
        if not interactions:
            return {"timestamps": [], "tma": [], "tme": []}

        df = pd.DataFrame([i.__dict__ for i in interactions])
        df['start_time'] = pd.to_datetime(df['start_time'])
        df = df.set_index('start_time')
        df_answered = df[df['status'] == 'answered'].copy() # Criar cópia para evitar SettingWithCopyWarning
        
        if df_answered.empty:
             return {"timestamps": [], "tma": [], "tme": []}

        df_answered['tma_calc'] = (df_answered['talk_time'] + df_answered['wait_time']) # Soma para AHT
        df_answered['tme_calc'] = df_answered['wait_time'] # Para TME

        if period == "H":
            resampled = df_answered.resample('H')
        elif period == "D":
            resampled = df_answered.resample('D')
        else:
            raise ValueError("Período inválido. Use 'H' para hora ou 'D' para dia.")

        tma_series = resampled['tma_calc'].mean().fillna(0) # Média do TMA
        tme_series = resampled['tme_calc'].mean().fillna(0) # Média do TME

        return {
            "timestamps": tma_series.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            "tma": tma_series.tolist(),
            "tme": tme_series.tolist()
        }

    @staticmethod
    def calculate_csat_metrics(csat_scores: List[CSAT]) -> Dict:
        """
        Calcula métricas de CSAT
        """
        if not csat_scores:
            return {
                "average_score": 0.0,
                "clarity_score": 0.0,
                "wait_time_score": 0.0,
                "navigation_score": 0.0,
                "total_evaluations": 0
            }
            
        return {
            "average_score": np.mean([s.score for s in csat_scores if s.score is not None]),
            "clarity_score": np.mean([s.clarity_score for s in csat_scores if s.clarity_score is not None]),
            "wait_time_score": np.mean([s.wait_time_score for s in csat_scores if s.wait_time_score is not None]),
            "navigation_score": np.mean([s.navigation_score for s in csat_scores if s.navigation_score is not None]),
            "total_evaluations": len(csat_scores)
        }

    @staticmethod
    def calculate_hsm_metrics(hsm_messages: List[HSM]) -> Dict:
        """
        Calcula métricas de HSM
        """
        if not hsm_messages:
            return {
                "total_sent": 0,
                "total_delivered": 0,
                "total_read": 0,
                "total_failed": 0,
                "delivery_rate": 0.0,
                "read_rate": 0.0
            }
            
        total_sent = len(hsm_messages)
        total_delivered = len([m for m in hsm_messages if m.delivered_at])
        total_read = len([m for m in hsm_messages if m.read_at])
        total_failed = len([m for m in hsm_messages if m.failed_at])
        
        return {
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_read": total_read,
            "total_failed": total_failed,
            "delivery_rate": (total_delivered / total_sent) * 100 if total_sent > 0 else 0.0,
            "read_rate": (total_read / total_delivered) * 100 if total_delivered > 0 else 0.0
        }

    @staticmethod
    def calculate_agent_metrics(
        interactions: List[Interaction],
        csat_scores: List[CSAT],
        start_date: datetime,
        end_date: datetime
    ) -> List[AgentMetrics]:
        """
        Calcula métricas por agente
        """
        agent_metrics = []
        
        # Agrupar interações por agente
        agent_interactions = {}
        for interaction in interactions:
            if interaction.agent_id not in agent_interactions:
                agent_interactions[interaction.agent_id] = []
            agent_interactions[interaction.agent_id].append(interaction)
            
        # Calcular métricas para cada agente
        for agent_id, agent_interactions_list in agent_interactions.items():
            answered_interactions = [i for i in agent_interactions_list if i.status == "answered"]
            
            metrics = AgentMetrics(
                agent_id=agent_id,
                date=start_date.date(), # Apenas a data para métricas diárias
                total_interactions=len(agent_interactions_list),
                answered_interactions=len(answered_interactions),
                average_handle_time=MetricsService.calculate_aht(answered_interactions),
                average_wait_time=MetricsService.calculate_awt(answered_interactions),
                average_talk_time=MetricsService.calculate_att(answered_interactions),
                service_level=MetricsService.calculate_service_level(answered_interactions),
                csat_score=np.mean([
                    s.score for s in csat_scores 
                    if s.agent_id == agent_id and start_date <= s.created_at <= end_date and s.score is not None
                ]) if csat_scores else 0.0
            )
            
            agent_metrics.append(metrics)
            
        return agent_metrics

    @staticmethod
    def calculate_queue_metrics(
        interactions: List[Interaction],
        start_date: datetime,
        end_date: datetime
    ) -> List[QueueMetrics]:
        """
        Calcula métricas por fila
        """
        queue_metrics = []
        
        # Agrupar interações por fila
        queue_interactions = {}
        for interaction in interactions:
            if interaction.queue_id not in queue_interactions:
                queue_interactions[interaction.queue_id] = []
            queue_interactions[interaction.queue_id].append(interaction)
            
        # Calcular métricas para cada fila
        for queue_id, queue_interactions_list in queue_interactions.items():
            answered_interactions = [i for i in queue_interactions_list if i.status == "answered"]
            abandoned_interactions = [i for i in queue_interactions_list if i.status == "abandoned"]
            
            metrics = QueueMetrics(
                queue_id=queue_id,
                date=start_date.date(), # Apenas a data para métricas diárias
                total_interactions=len(queue_interactions_list),
                answered_interactions=len(answered_interactions),
                abandoned_interactions=len(abandoned_interactions),
                average_wait_time=MetricsService.calculate_awt(queue_interactions_list),
                service_level=MetricsService.calculate_service_level(queue_interactions_list)
            )
            
            queue_metrics.append(metrics)
            
        return queue_metrics 