from fastapi import APIRouter
from src.routers.auth import router as auth_router
from src.routers.posts import router as posts_router
from src.routers.users import router as users_router
from src.routers.votes import router as votes_router


main_router = APIRouter()

main_router.include_router(auth_router, tags=['auth'])
main_router.include_router(users_router, tags=['users'])
main_router.include_router(posts_router, tags=['posts'])
main_router.include_router(votes_router, tags=['votes'])
