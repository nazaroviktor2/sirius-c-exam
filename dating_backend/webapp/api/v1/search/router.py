from fastapi import APIRouter

from webapp.api.v1.search.form.router import search_form_router
from webapp.api.v1.search.params.router import search_params_router

search_router = APIRouter()

search_router.include_router(search_form_router, prefix='/form', tags=['SEARCH FORM API'])
search_router.include_router(search_params_router, prefix='/params', tags=['SEARCH PARAMS API'])
