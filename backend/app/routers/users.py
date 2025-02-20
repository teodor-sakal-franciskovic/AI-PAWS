from fastapi import (
    APIRouter,
    Depends,
    Body,
)
from fastapi.responses import JSONResponse, Response
from transformers import AutoModel, AutoTokenizer

from sqlalchemy.orm import Session
from typing import Annotated

from ..dependencies.db import get_db
from ..dependencies.auth import get_current_active_user, get_current_active_user_role
from ..dependencies.users import (
    get_create_user,
    get_retrieve_logged_in_user,
    get_update_user_info,
    get_update_user_password,
    get_deactivate_user,
)

from ..models.user import User
from ..models.role import Role

from ..schemas.users import (
    UpdatedUserInfo,
    UserCreate,
    UserResponse,
    UpdatedUserPassword,
)
from ..schemas.response import GenericResponse

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/registration", tags=["users"], response_model=GenericResponse)
def register(
    user: Annotated[
        UserCreate,
        Body(
            examples=[
                {
                    "email": "example@email.com",
                    "password": "Example123!",
                    "name": "John",
                    "surname": "Padilla",
                    "role_id": 1,
                }
            ]
        ),
    ],
    db: Session = Depends(get_db),
    create_user=Depends(get_create_user),
) -> GenericResponse:
    created_user: UserResponse = create_user(user, db)
    return JSONResponse(
        status_code=201,
        content=GenericResponse(
            message="Successfully created user", data=created_user
        ).model_dump(),
    )


@router.get("/me", tags=["users"], response_model=GenericResponse)
def retrieve_logged_in_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    retrieve_logged_in_user=Depends(get_retrieve_logged_in_user),
) -> GenericResponse:
    logged_in_user: UserResponse = retrieve_logged_in_user(current_user, role)
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Successfully retrieved the logged-in user", data=logged_in_user
        ).model_dump(),
    )


@router.get("/generate-text")
def generate_text():
    tokenizer = AutoTokenizer.from_pretrained(
        "sambanovasystems/SambaLingo-Serbian-Chat", use_fast=False
    )
    model = AutoModelForCausalLM.from_pretrained(
        "sambanovasystems/SambaLingo-Serbian-Chat",
        device_map="auto",
        torch_dtype="auto",
    )
    text_generator = pipeline(
        "text-generation", model=model, tokenizer=tokenizer, device_map="auto"
    )
    user_input = "Koja su pravila tenisa?"

    prompt = f"<|user|>\n{user_input}</s>\n<|assistant|>\n"

    response = text_generator(
        prompt,
        max_length=512,
        temperature=0.8,
        top_p=0.9,
        repetition_penalty=1.0,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    print(f"Response {response[0]['generated_text']}")

    # Extract and print the generated text
    generated_text = response[0]["generated_text"]
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Succesfully generated text", data=generated_text
        ).model_dump(),
    )


@router.put("/info", tags=["users"], response_model=GenericResponse)
def update_user_info(
    updated_user_info: Annotated[
        UpdatedUserInfo,
        Body(examples=[{"name": "Peter", "surname": "Hecox!"}]),
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    db: Session = Depends(get_db),
    update_user_info=Depends(get_update_user_info),
) -> GenericResponse:
    updated_user: UserResponse = update_user_info(
        current_user, updated_user_info, role, db
    )
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Succesfully updated user info", data=updated_user
        ).model_dump(),
    )


@router.put("/password", tags=["users"], response_model=GenericResponse)
def update_user_password(
    updated_password: Annotated[
        UpdatedUserPassword,
        Body(
            examples=[
                {"password": "NewPassword123!", "confirmed_password": "NewPassword123!"}
            ]
        ),
    ],
    current_user: Annotated[User, Depends(get_current_active_user)],
    role: Annotated[Role, Depends(get_current_active_user_role)],
    db: Session = Depends(get_db),
    update_user_password=Depends(get_update_user_password),
):
    updated_user: UserResponse = update_user_password(
        current_user, updated_password, role, db
    )
    return JSONResponse(
        status_code=200,
        content=GenericResponse(
            message="Succesfully updated user password", data=updated_user
        ).model_dump(),
    )


@router.delete("/", tags=["users"], status_code=204)
def deactivate_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    deactivate_user=Depends(get_deactivate_user),
):
    deactivate_user(current_user, db)
    return Response(
        status_code=204,
    )
