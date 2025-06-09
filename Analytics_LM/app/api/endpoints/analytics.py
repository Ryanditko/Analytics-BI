from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from app.services.genesys.client import GenesysService
from app.services.powerbi.client import PowerBIService

router = APIRouter()
genesys_service = GenesysService()
powerbi_service = PowerBIService()

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    queue_ids: Optional[List[str]] = Query(default=None),
    team_ids: Optional[List[str]] = Query(default=None),
    channel_types: Optional[List[str]] = Query(default=None)
):
    """
    Obtém dados para o dashboard principal
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=1)
        if not end_date:
            end_date = datetime.now()

        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids,
            team_ids=team_ids,
            channel_types=channel_types
        )

        # Processar dados para o dashboard
        metrics = {
            "total_customers": len(set(i["customer_id"] for i in interactions)),
            "total_calls": len(interactions),
            "answered_calls": len([i for i in interactions if i["status"] == "answered"]),
            "service_level": calculate_service_level(interactions),
            "average_handle_time": calculate_aht(interactions),
            "average_wait_time": calculate_awt(interactions),
            "average_talk_time": calculate_att(interactions),
            "logged_in_agents": len(set(i["agent_id"] for i in interactions if i["agent_id"])),
            "auto_service_interactions": len([i for i in interactions if i["type"] == "auto_service"]),
            "top_reasons": get_top_reasons(interactions),
            "callback_count": len([i for i in interactions if i["type"] == "callback"]),
            "duplicate_channel_interactions": len([i for i in interactions if i["duplicate_channel"]])
        }

        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/csat")
async def get_csat_analytics(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    agent_id: Optional[str] = Query(default=None)
):
    """
    Obtém dados de CSAT
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        csat_data = await genesys_service.get_csat_scores(
            start_date=start_date,
            end_date=end_date,
            agent_id=agent_id
        )

        return {
            "total_evaluations": len(csat_data),
            "average_score": calculate_average_csat(csat_data),
            "scores_by_question": get_scores_by_question(csat_data),
            "word_cloud": generate_word_cloud(csat_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/hsm")
async def get_hsm_analytics(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None)
):
    """
    Obtém dados de HSM
    """
    try:
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()

        hsm_data = await genesys_service.get_hsm_metrics(
            start_date=start_date,
            end_date=end_date
        )

        return {
            "total_sent": hsm_data["total_sent"],
            "total_delivered": hsm_data["total_delivered"],
            "total_read": hsm_data["total_read"],
            "total_failed": hsm_data["total_failed"],
            "mass_messages": hsm_data["mass_messages"],
            "individual_messages": hsm_data["individual_messages"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Funções auxiliares
def calculate_service_level(interactions):
    # Implementar cálculo de nível de serviço
    pass

def calculate_aht(interactions):
    # Implementar cálculo de tempo médio de atendimento
    pass

def calculate_awt(interactions):
    # Implementar cálculo de tempo médio de espera
    pass

def calculate_att(interactions):
    # Implementar cálculo de tempo médio de conversação
    pass

def get_top_reasons(interactions):
    # Implementar obtenção dos principais motivos
    pass

def calculate_average_csat(csat_data):
    # Implementar cálculo da média de CSAT
    pass

def get_scores_by_question(csat_data):
    # Implementar obtenção de scores por questão
    pass

def generate_word_cloud(csat_data):
    # Implementar geração de nuvem de palavras
    pass 