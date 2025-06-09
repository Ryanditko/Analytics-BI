from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta
from dateutil.tz import tzutc
import purecloudplatformclientv2 as gc_client
from app.models.interaction import Interaction # Importando o modelo Interaction

class GenesysService:
    def __init__(self):
        self.client_id = os.getenv("GENESYS_CLIENT_ID")
        self.client_secret = os.getenv("GENESYS_CLIENT_SECRET")
        self.environment = os.getenv("GENESYS_ENVIRONMENT")

        if not all([self.client_id, self.client_secret, self.environment]):
            raise ValueError("As variáveis de ambiente GENESYS_CLIENT_ID, GENESYS_CLIENT_SECRET e GENESYS_ENVIRONMENT devem ser configuradas.")

        # Configura as credenciais da Genesys Cloud para autenticação
        gc_client.Configuration.set_default_client_id_and_secret(self.client_id, self.client_secret)
        gc_client.Configuration.set_default_host(f"https://api.{self.environment}.mypurecloud.com")

        self.conversations_api = gc_client.ConversationsApi()
        self.routing_api = gc_client.RoutingApi()

    async def get_interactions(
        self,
        start_date: datetime,
        end_date: datetime,
        queue_ids: Optional[List[str]] = None,
        team_ids: Optional[List[str]] = None,
        channel_types: Optional[List[str]] = None
    ) -> List[Interaction]: # Retorna lista de objetos Interaction
        """
        Obtém interações da Genesys Cloud com filtros (Dados Reais ou Simulados)
        """
        try:
            # A autenticação já está configurada no __init__

            # Construção da query de analytics de conversas
            # Para a Tela Inicial, vamos buscar um conjunto amplo de dados
            query_body = gc_client.ConversationQuery({
                'interval': f"{start_date.isoformat()}Z/{end_date.isoformat()}Z",
                'metrics': ['tWait', 'tTalk', 'tHandle', 'nConnected', 'nOffered', 'nAbandon', 'nConsult', 'nOutbound', 'nTransferred'],
                'groupBy': ['queueId', 'mediaType', 'agentId', 'direction', 'wrapUpCode'] # Adicionado wrapUpCode para motivo
            })

            predicates = []
            if queue_ids:
                predicates.append(gc_client.ConversationPredicate({
                    'type': 'DIMENSION',
                    'dimension': 'queueId',
                    'operator': 'IN',
                    'value': queue_id
                }) for queue_id in queue_ids)

            if channel_types:
                predicates.append(gc_client.ConversationPredicate({
                    'type': 'DIMENSION',
                    'dimension': 'mediaType',
                    'operator': 'IN',
                    'value': channel_type.upper() # Genesys usa maiúsculas para tipos de mídia
                }) for channel_type in channel_types)
            
            if predicates:
                query_body.filter = gc_client.ConversationFilter({
                    'type': 'AND',
                    'predicates': list(predicates)
                })

            # Executa a query
            response = self.conversations_api.post_analytics_conversations_details_query(query_body)
            
            interactions_data = []
            if response.conversations:
                for conv in response.conversations:
                    customer_id = next((p.participant_id for p in conv.participants if p.purpose == "customer"), None)

                    for participant in conv.participants:
                        if participant.purpose == "agent" and participant.sessions:
                            for session in participant.sessions:
                                for segment in session.segments:
                                    if segment.segment_type == "interact" and segment.queue_id:
                                        # Extrair motivo/assunto (exemplo simplificado, pode variar na Genesys)
                                        reason = next((w.code for w in participant.wrapup if w.code) for p in conv.participants if p.wrapup and p.purpose == "agent" ) if participant.wrapup else None
                                        if not reason: # Tenta pegar de outros participantes se o agente não tiver wrapup
                                             reason = next((w.code for w in p.wrapup if w.code) for p in conv.participants if p.wrapup and p.purpose != "agent" and p.purpose != "external")
                                        
                                        # Preenchimento de outros campos com lógica simulada/simplificada para começar
                                        is_auto_service = False
                                        auto_service_type = None
                                        #TODO: Implementar lógica de auto serviço baseado em fluxo real da URA/Bot

                                        is_callback = False
                                        callback_reason = None
                                        #TODO: Implementar lógica de rechamada

                                        is_duplicate_channel = False
                                        #TODO: Implementar lógica de canal duplicado

                                        # Convertendo as datas para datetime objects
                                        start_time = datetime.fromisoformat(conv.conversation_start_time.replace('Z', '+00:00')) if conv.conversation_start_time else None
                                        end_time = datetime.fromisoformat(conv.conversation_end_time.replace('Z', '+00:00')) if conv.conversation_end_time else None

                                        duration = (end_time - start_time).total_seconds() if start_time and end_time else 0
                                        wait_time = next((m.value for m in session.metrics if m.metric == "tWait"), 0) if session.metrics else 0
                                        talk_time = next((m.value for m in session.metrics if m.metric == "tTalk"), 0) if session.metrics else 0
                                        status = "answered" if next((m.value for m in session.metrics if m.metric == "nConnected"), 0) > 0 else "abandoned"

                                        interaction = Interaction(
                                            id=conv.conversation_id,
                                            customer_id=customer_id,
                                            agent_id=participant.participant_id,
                                            queue_id=segment.queue_id,
                                            channel_type=session.media_type,
                                            start_time=start_time,
                                            end_time=end_time,
                                            duration=duration,
                                            wait_time=wait_time,
                                            talk_time=talk_time,
                                            status=status,
                                            reason=reason,
                                            is_auto_service=is_auto_service,
                                            auto_service_type=auto_service_type,
                                            is_callback=is_callback,
                                            callback_reason=callback_reason,
                                            is_duplicate_channel=is_duplicate_channel
                                        )
                                        interactions_data.append(interaction)

            return interactions_data
        except Exception as e:
            raise Exception(f"Erro ao buscar interações da Genesys Cloud: {str(e)}")

    async def get_agent_metrics(
        self,
        agent_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Obtém métricas de um agente específico (MOCK DATA)
        """
        try:
            # TODO: Implementar lógica real da API
            # Exemplo de chamada à API:
            # user_performance_query = gc_client.UserPerformanceQuery()... # Construir a query
            # response = self.analytics_api.post_analytics_users_details_query(user_performance_query)
            # Processar a resposta

            return {"tma": 120, "interactions": 10, "login_time": 480}
        except Exception as e:
            raise Exception(f"Erro ao buscar métricas do agente: {str(e)}")

    async def get_queue_metrics(
        self,
        queue_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Obtém métricas de uma fila específica (MOCK DATA)
        """
        try:
            # TODO: Implementar lógica real da API
            return {"service_level": 0.85, "total_interactions": 500}
        except Exception as e:
            raise Exception(f"Erro ao buscar métricas da fila: {str(e)}")

    async def get_csat_scores(
        self,
        start_date: datetime,
        end_date: datetime,
        agent_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém scores de CSAT (MOCK DATA)
        """
        try:
            # TODO: Implementar lógica real da API
            return []
        except Exception as e:
            raise Exception(f"Erro ao buscar scores CSAT: {str(e)}")

    async def get_hsm_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Obtém métricas de HSM (MOCK DATA)
        """
        try:
            # TODO: Implementar lógica real da API
            return {"total_sent": 0, "total_delivered": 0, "total_read": 0, "total_failed": 0}
        except Exception as e:
            raise Exception(f"Erro ao buscar métricas HSM: {str(e)}")

    async def get_speech_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        topic: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtém dados de Speech Analytics (MOCK DATA)
        """
        try:
            # TODO: Implementar lógica real da API
            return []
        except Exception as e:
            raise Exception(f"Erro ao buscar Speech Analytics: {str(e)}") 