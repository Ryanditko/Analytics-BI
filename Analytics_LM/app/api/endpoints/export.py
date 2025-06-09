from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
import os
from app.services.analytics.export import ExportService
from app.services.genesys.client import GenesysService

router = APIRouter()
genesys_service = GenesysService()
export_service = ExportService()

@router.get("/export/interactions")
async def export_interactions(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    queue_ids: Optional[List[str]] = Query(default=None),
    team_ids: Optional[List[str]] = Query(default=None),
    channel_types: Optional[List[str]] = Query(default=None),
    format: str = Query("excel", regex="^(excel|csv|json)$")
):
    """
    Exporta interações para o formato especificado
    """
    try:
        # Obter dados
        interactions = await genesys_service.get_interactions(
            start_date=start_date,
            end_date=end_date,
            queue_ids=queue_ids,
            team_ids=team_ids,
            channel_types=channel_types
        )
        
        # Criar diretório de exportação se não existir
        os.makedirs("exports", exist_ok=True)
        
        # Exportar dados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format == "excel":
            output_path = f"exports/interactions_{timestamp}.xlsx"
            export_service.export_interactions_to_excel(interactions, output_path)
        elif format == "csv":
            output_path = f"exports/interactions_{timestamp}.csv"
            export_service.export_to_csv(interactions, output_path)
        else:  # json
            output_path = f"exports/interactions_{timestamp}.json"
            export_service.export_to_json(interactions, output_path)
            
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csat")
async def export_csat(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    agent_id: Optional[str] = Query(default=None),
    format: str = Query("excel", regex="^(excel|csv|json)$")
):
    """
    Exporta dados de CSAT para o formato especificado
    """
    try:
        # Obter dados
        csat_data = await genesys_service.get_csat_scores(
            start_date=start_date,
            end_date=end_date,
            agent_id=agent_id
        )
        
        # Criar diretório de exportação se não existir
        os.makedirs("exports", exist_ok=True)
        
        # Exportar dados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format == "excel":
            output_path = f"exports/csat_{timestamp}.xlsx"
            export_service.export_csat_to_excel(csat_data, output_path)
        elif format == "csv":
            output_path = f"exports/csat_{timestamp}.csv"
            export_service.export_to_csv(csat_data, output_path)
        else:  # json
            output_path = f"exports/csat_{timestamp}.json"
            export_service.export_to_json(csat_data, output_path)
            
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/hsm")
async def export_hsm(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    format: str = Query("excel", regex="^(excel|csv|json)$")
):
    """
    Exporta dados de HSM para o formato especificado
    """
    try:
        # Obter dados
        hsm_data = await genesys_service.get_hsm_metrics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Criar diretório de exportação se não existir
        os.makedirs("exports", exist_ok=True)
        
        # Exportar dados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format == "excel":
            output_path = f"exports/hsm_{timestamp}.xlsx"
            export_service.export_hsm_to_excel(hsm_data, output_path)
        elif format == "csv":
            output_path = f"exports/hsm_{timestamp}.csv"
            export_service.export_to_csv(hsm_data, output_path)
        else:  # json
            output_path = f"exports/hsm_{timestamp}.json"
            export_service.export_to_json(hsm_data, output_path)
            
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/speech-analytics")
async def export_speech_analytics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    topic: Optional[str] = Query(default=None),
    format: str = Query("excel", regex="^(excel|csv|json)$")
):
    """
    Exporta dados de Speech Analytics para o formato especificado
    """
    try:
        # Obter dados
        speech_data = await genesys_service.get_speech_analytics(
            start_date=start_date,
            end_date=end_date,
            topic=topic
        )
        
        # Criar diretório de exportação se não existir
        os.makedirs("exports", exist_ok=True)
        
        # Exportar dados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if format == "excel":
            output_path = f"exports/speech_analytics_{timestamp}.xlsx"
            export_service.export_speech_analytics_to_excel(speech_data, output_path)
        elif format == "csv":
            output_path = f"exports/speech_analytics_{timestamp}.csv"
            export_service.export_to_csv(speech_data, output_path)
        else:  # json
            output_path = f"exports/speech_analytics_{timestamp}.json"
            export_service.export_to_json(speech_data, output_path)
            
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=os.path.basename(output_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 