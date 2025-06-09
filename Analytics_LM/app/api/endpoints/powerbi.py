from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from datetime import datetime
from app.services.powerbi.client import PowerBIService
from app.services.genesys.client import GenesysService

router = APIRouter()
powerbi_service = PowerBIService()
genesys_service = GenesysService()

@router.post("/powerbi/refresh")
async def refresh_powerbi_dataset(
    dataset_id: str = Query(...)
):
    """
    Força um refresh do dataset do Power BI
    """
    try:
        success = await powerbi_service.refresh_dataset(dataset_id)
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao atualizar dataset")
        return {"message": "Dataset atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/powerbi/report-url")
async def get_report_url(
    report_id: str = Query(...)
):
    """
    Obtém URL de embed do relatório do Power BI
    """
    try:
        url = await powerbi_service.get_report_embed_url(report_id)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/powerbi/update-interactions")
async def update_interactions_dataset(
    dataset_id: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    queue_ids: Optional[List[str]] = Query(default=None),
    team_ids: Optional[List[str]] = Query(default=None),
    channel_types: Optional[List[str]] = Query(default=None)
):
    """
    Atualiza o dataset de interações no Power BI
    """
    try:
        # Obter dados da Genesys
        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids,
            team_ids=team_ids,
            channel_types=channel_types
        )
        
        # Atualizar dataset
        success = await powerbi_service.update_dataset(dataset_id, interactions)
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao atualizar dataset")
            
        return {"message": "Dataset atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/powerbi/update-csat")
async def update_csat_dataset(
    dataset_id: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    agent_id: Optional[str] = Query(default=None)
):
    """
    Atualiza o dataset de CSAT no Power BI
    """
    try:
        # Obter dados da Genesys
        csat_data = await genesys_service.get_csat_scores(
            start_date=start_date,
            end_date=end_date,
            agent_id=agent_id
        )
        
        # Atualizar dataset
        success = await powerbi_service.update_dataset(dataset_id, csat_data)
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao atualizar dataset")
            
        return {"message": "Dataset atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/powerbi/update-hsm")
async def update_hsm_dataset(
    dataset_id: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...)
):
    """
    Atualiza o dataset de HSM no Power BI
    """
    try:
        # Obter dados da Genesys
        hsm_data = await genesys_service.get_hsm_metrics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Atualizar dataset
        success = await powerbi_service.update_dataset(dataset_id, hsm_data)
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao atualizar dataset")
            
        return {"message": "Dataset atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/powerbi/update-speech-analytics")
async def update_speech_analytics_dataset(
    dataset_id: str = Query(...),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    topic: Optional[str] = Query(default=None)
):
    """
    Atualiza o dataset de Speech Analytics no Power BI
    """
    try:
        # Obter dados da Genesys
        speech_data = await genesys_service.get_speech_analytics(
            start_date=start_date,
            end_date=end_date,
            topic=topic
        )
        
        # Atualizar dataset
        success = await powerbi_service.update_dataset(dataset_id, speech_data)
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao atualizar dataset")
            
        return {"message": "Dataset atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/powerbi/create-report")
async def create_powerbi_report(
    name: str = Query(...),
    dataset_id: str = Query(...),
    definition: Dict = Query(...)
):
    """
    Cria um novo relatório no Power BI
    """
    try:
        report_id = await powerbi_service.create_report(name, dataset_id, definition)
        return {"report_id": report_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/powerbi/update-report")
async def update_powerbi_report(
    report_id: str = Query(...),
    definition: Dict = Query(...)
):
    """
    Atualiza um relatório existente no Power BI
    """
    try:
        success = await powerbi_service.update_report(report_id, definition)
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao atualizar relatório")
        return {"message": "Relatório atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 