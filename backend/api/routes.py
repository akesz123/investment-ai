from fastapi import APIRouter

router = APIRouter()

@router.get('/scan')
def scan():
    return {'message': 'scan not implemented yet'}
