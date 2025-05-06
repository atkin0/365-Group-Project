from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

description = """
Gamer Society is a society for gamers
"""
tags_metadata = [
]

app = FastAPI(
    title="Gamer Society",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Tyler Dang",
        "email": "tbdang@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# app.include_router(inventory.router)
#
# @app.get("/")
# async def root():
#     return {"message": "Shop is open for business!"}
