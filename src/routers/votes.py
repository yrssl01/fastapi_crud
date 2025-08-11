from fastapi import APIRouter, Depends,  HTTPException, status
from typing import Annotated
from sqlalchemy import select
from src.routers.dependencies import SessionDep
from src.schemas.users import UserOut
from src.schemas.votes import Vote
from src.models.votes import Vote as VoteModel
from src.models.posts import Post as PostModel
from src.routers.oauth2 import get_current_user


router = APIRouter(prefix='/votes')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def vote(vote: Vote, current_user: Annotated[UserOut, Depends(get_current_user)], session: SessionDep):
    query = select(PostModel).where(PostModel.id == vote.post_id)
    result = await session.execute(query)
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote.post_id} not found"
        )

    vote_query = await session.execute(
        select(VoteModel).where(VoteModel.post_id == vote.post_id, VoteModel.user_id == current_user.id)
    )

    found_vote = vote_query.scalar_one_or_none()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'user {current_user.id} has already voted on post {vote.post_id}'
            )
        new_vote = VoteModel(post_id=vote.post_id, user_id=current_user.id)
        session.add(new_vote)
        await session.commit()
        return {'message': 'successfully added vote'}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Vote does not exist'
            )
        await session.delete(found_vote)
        await session.commit()
        return {'message': 'successfully deleted vote'}
