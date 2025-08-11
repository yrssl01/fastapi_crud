from fastapi import APIRouter, Depends, HTTPException
from fastapi import status, Response
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from typing import Annotated
from src.schemas.users import UserOut
from src.schemas.posts import PostOut, Post, PostCreate
from src.models.posts import Post as PostModel
from src.models.votes import Vote as VoteModel
from src.routers.dependencies import SessionDep
from src.routers.oauth2 import get_current_user


router = APIRouter(prefix='/posts')


@router.get('', response_model=list[PostOut])
async def get_posts(
    current_user: Annotated[UserOut, Depends(get_current_user)],
    session: SessionDep, 
    skip: int = 0, 
    limit: int = 10,
    search: str = ""
) -> list[PostOut]:
    query = (
        select(
        PostModel, 
        func.count(VoteModel.post_id).label('votes')
        ).options(selectinload(PostModel.owner))
        .join(VoteModel, VoteModel.post_id == PostModel.id, isouter=True)
        .group_by(PostModel.id)
        .filter(PostModel.title.contains(search))
        .limit(limit).offset(skip)
    )
    
    result = await session.execute(query)
    posts = result.all() 
    
    return posts


@router.post('', status_code=status.HTTP_201_CREATED, response_model=Post)
async def create_post(
    post: PostCreate,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    session: SessionDep,
):
    new_post = PostModel(owner_id=current_user.id, **post.model_dump())
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post


@router.get('/{post_id}', response_model=Post)
async def get_post(
    post_id: int, 
    current_user: Annotated[UserOut, Depends(get_current_user)], 
    session: SessionDep
):
    query = await session.execute(
        select(PostModel).options(selectinload(PostModel.owner))
        .where(PostModel.id == post_id)
        )
    retrieved_post = query.scalar_one_or_none()

    if not retrieved_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    return retrieved_post



@router.put('/{post_id}', response_model=Post)
async def update_post(
    post_id: int,
    post: PostCreate,
    current_user: Annotated[UserOut, Depends(get_current_user)],
    session: SessionDep
):
    result = await session.execute(select(PostModel).where(PostModel.id == post_id))
    filtered_post = result.scalars().first()

    if filtered_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} does not exist"
        )
    
    if filtered_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )

    for field, value in post.model_dump(exclude_unset=True).items():
        setattr(filtered_post, field, value)
    
    await session.commit()
    return filtered_post


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int, 
    current_user: Annotated[UserOut, Depends(get_current_user)], 
    session: SessionDep
):
    result = await session.execute(select(PostModel).where(PostModel.id == post_id))
    filtered_post = result.scalars().first()
    
    if filtered_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} was not found"
        )
    if filtered_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )

    await session.delete(filtered_post)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
