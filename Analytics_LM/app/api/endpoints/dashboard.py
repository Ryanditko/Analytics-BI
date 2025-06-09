from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.services.genesys.client import GenesysService
from app.services.analytics.metrics import MetricsService

router = APIRouter()
genesys_service = GenesysService()
metrics_service = MetricsService()

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    queue_ids: Optional[List[str]] = Query(default=None),
    team_ids: Optional[List[str]] = Query(default=None),
    channel_types: Optional[List[str]] = Query(default=None)
):
    """
    Obtém dados para o dashboard principal (Tela Inicial)
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=1)
        if not end_date:
            end_date = datetime.now()

        # Obter dados da Genesys
        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids,
            team_ids=team_ids,
            channel_types=channel_types
        )

        # Calcular todas as métricas da Tela Inicial
        metrics = {
            "total_customers": metrics_service.get_total_customers(interactions),
            "total_received_calls": metrics_service.get_total_received_calls(interactions),
            "total_answered_calls": metrics_service.get_total_answered_calls(interactions),
            "service_level": metrics_service.calculate_service_level(interactions),
            "average_handle_time": metrics_service.calculate_aht(interactions),
            "average_wait_time": metrics_service.calculate_awt(interactions),
            "average_talk_time": metrics_service.calculate_att(interactions),
            "logged_in_agents": metrics_service.get_logged_in_agents(interactions),
            "auto_service_interactions": metrics_service.get_auto_service_interactions(interactions),
            "top_reasons": metrics_service.get_top_reasons(interactions),
            "total_callbacks": metrics_service.get_total_callbacks(interactions),
            "duplicate_channel_interactions": metrics_service.get_duplicate_channel_interactions(interactions)
        }

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados para o dashboard principal: {str(e)}")

@router.get("/dashboard/overview/volume_by_period")
async def get_overview_volume_by_period(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    queue_ids: Optional[List[str]] = Query(default=None),
    channel_types: Optional[List[str]] = Query(default=None),
    period: str = Query("H", regex="^(H|D)$")  # H para hora, D para dia
):
    """
    Obtém o volume de clientes e chamadas por período para a Tela Inicial.
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids,
            channel_types=channel_types
        )

        volume_data = metrics_service.get_interactions_volume_by_period(interactions, period=period)
        return volume_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter volume por período: {str(e)}")

@router.get("/dashboard/overview/tma_tme_by_period")
async def get_overview_tma_tme_by_period(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    queue_ids: Optional[List[str]] = Query(default=None),
    channel_types: Optional[List[str]] = Query(default=None),
    period: str = Query("H", regex="^(H|D)$")  # H para hora, D para dia
):
    """
    Obtém TMA e TME por período para a Tela Inicial.
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids,
            channel_types=channel_types
        )

        tma_tme_data = metrics_service.get_tma_tme_by_period(interactions, period=period)
        return tma_tme_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter TMA e TME por período: {str(e)}")

@router.get("/dashboard/csat")
async def get_csat_dashboard(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    agent_id: Optional[str] = Query(default=None)
):
    """
    Obtém dados para o dashboard de CSAT
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Obter dados da Genesys
        csat_data = await genesys_service.get_csat_scores(
            start_date=start_date,
            end_date=end_date,
            agent_id=agent_id
        )

        # Calcular métricas
        metrics = metrics_service.calculate_csat_metrics(csat_data)

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/hsm")
async def get_hsm_dashboard(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None)
):
    """
    Obtém dados para o dashboard de HSM
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Obter dados da Genesys
        hsm_data = await genesys_service.get_hsm_metrics(
            start_date=start_date,
            end_date=end_date
        )

        # Calcular métricas
        metrics = metrics_service.calculate_hsm_metrics(hsm_data)

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/speech-analytics")
async def get_speech_analytics_dashboard(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    topic: Optional[str] = Query(default=None)
):
    """
    Obtém dados para o dashboard de Speech Analytics
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Obter dados da Genesys
        speech_data = await genesys_service.get_speech_analytics(
            start_date=start_date,
            end_date=end_date,
            topic=topic
        )

        # Calcular métricas
        metrics = {
            "total_interactions": len(speech_data),
            "topics": {
                topic: len([s for s in speech_data if s.topic == topic])
                for topic in set(s.topic for s in speech_data)
            },
            "average_confidence": sum(s.confidence for s in speech_data) / len(speech_data) if speech_data else 0,
            "average_sentiment": sum(s.sentiment_score for s in speech_data) / len(speech_data) if speech_data else 0
        }

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/agent-performance")
async def get_agent_performance_dashboard(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    agent_id: Optional[str] = Query(default=None)
):
    """
    Obtém dados para o dashboard de performance dos agentes
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Obter dados da Genesys
        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            agent_ids=[agent_id] if agent_id else None
        )

        csat_scores = await genesys_service.get_csat_scores(
            start_date=start_date,
            end_date=end_date,
            agent_id=agent_id
        )

        # Calcular métricas
        agent_metrics = metrics_service.calculate_agent_metrics(
            interactions=interactions,
            csat_scores=csat_scores,
            start_date=start_date,
            end_date=end_date
        )

        return agent_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/queue-performance")
async def get_queue_performance_dashboard(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    queue_ids: Optional[List[str]] = Query(default=None)
):
    """
    Obtém dados para o dashboard de performance das filas
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        # Obter dados da Genesys
        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids
        )

        # Calcular métricas
        queue_metrics = metrics_service.calculate_queue_metrics(
            interactions=interactions,
            start_date=start_date,
            end_date=end_date
        )

        return queue_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 