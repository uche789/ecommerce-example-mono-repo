from fastapi import APIRouter

router = APIRouter()

@router.get('/discount/test')
def get_discount_test():
    return {
        "testing": "testing"
    }