# from fastapi import APIRouter, Depends, Request, Response
# from urllib.parse import urlparse

# from app.application.dto.dto import Actor, AuthResult, RegisterCmd
# from app.application.use_cases import auth as uc
# from app.core.config import settings
# from app.core.exceptions import ForbiddenError
# from app.core.rate_limit import limiter
# from app.presentation import mappers
# from app.presentation.dependencies.security import get_current_actor, provide
# from app.presentation.schemas import auth as s
# from app.presentation.schemas.common import Message
# from app.application.dto.dto import UserView
# from app.application.use_cases.users import GetUser

# router = APIRouter(prefix="/auth", tags=["Authentification"])
# COOKIE = "refresh_token"
# COOKIE_PATH = "/api/v1/auth"


# def _set_cookie(response: Response, token: str) -> None:
#     response.set_cookie(COOKIE, token, max_age=settings.refresh_token_expire_days * 86400, httponly=True,
#                         secure=settings.cookie_secure, samesite=settings.cookie_samesite, path=COOKIE_PATH)


# def _check_origin(request: Request) -> None:
#     """Défense CSRF supplémentaire pour les routes basées sur le cookie."""
#     origin = request.headers.get("origin")
#     if origin and origin not in settings.cors_origins:
#         raise ForbiddenError("Origine non autorisée.")


# def _token_out(r: AuthResult, db_user_view: UserView) -> s.TokenOut:
#     return s.TokenOut(access_token=r.access_token, user=mappers.user_out(db_user_view))


# @router.post("/register", response_model=s.UserOut, status_code=201)
# @limiter.limit("10/hour")
# def register(request: Request, body: s.RegisterIn, usecase: uc.RegisterUser = Depends(provide(uc.RegisterUser)),
#              get_user: GetUser = Depends(provide(GetUser))):
#     user = usecase.execute(RegisterCmd(**body.model_dump()))
#     return mappers.user_out(get_user.execute(user.id))


# @router.post("/login", response_model=s.TokenOut)
# @limiter.limit("10/minute")
# def login(request: Request, response: Response, body: s.LoginIn, usecase: uc.LoginUser = Depends(provide(uc.LoginUser)),
#           get_user: GetUser = Depends(provide(GetUser))):
#     result = usecase.execute(body.email, body.password)
#     _set_cookie(response, result.refresh_token)
#     return _token_out(result, get_user.execute(result.user.id))


# @router.post("/refresh", response_model=s.TokenOut)
# @limiter.limit("60/minute")
# def refresh(request: Request, response: Response, usecase: uc.RefreshSession = Depends(provide(uc.RefreshSession)),
#             get_user: GetUser = Depends(provide(GetUser))):
#     _check_origin(request)
#     result = usecase.execute(request.cookies.get(COOKIE))
#     _set_cookie(response, result.refresh_token)
#     return _token_out(result, get_user.execute(result.user.id))


# @router.post("/logout", response_model=Message)
# def logout(request: Request, response: Response, usecase: uc.LogoutUser = Depends(provide(uc.LogoutUser))):
#     _check_origin(request)
#     usecase.execute(request.cookies.get(COOKIE))
#     response.delete_cookie(COOKIE, path=COOKIE_PATH)
#     return Message(detail="Vous êtes déconnecté.")


# @router.post("/forgot-password", response_model=Message)
# @limiter.limit("5/hour")
# def forgot_password(request: Request, body: s.ForgotPasswordIn, usecase: uc.RequestPasswordReset = Depends(provide(uc.RequestPasswordReset))):
#     usecase.execute(body.email)
#     return Message(detail="Si un compte existe avec cette adresse, un e-mail vient d'être envoyé.")


# @router.post("/reset-password", response_model=Message)
# @limiter.limit("10/hour")
# def reset_password(request: Request, body: s.ResetPasswordIn, usecase: uc.ResetPassword = Depends(provide(uc.ResetPassword))):
#     usecase.execute(body.token, body.new_password)
#     return Message(detail="Votre mot de passe a été modifié. Vous pouvez vous connecter.")


from fastapi import APIRouter, Depends, Request, Response

from app.application.dto.dto import AuthResult, RegisterCmd, UserView
from app.application.use_cases import auth as uc
from app.application.use_cases.users import GetUser
from app.core.config import settings
from app.core.exceptions import ForbiddenError
from app.core.rate_limit import limiter
from app.presentation import mappers
from app.presentation.dependencies.security import provide
from app.presentation.schemas import auth as s
from app.presentation.schemas.common import Message

router = APIRouter(prefix="/auth", tags=["Authentification"])
COOKIE = "refresh_token"
COOKIE_PATH = "/api/v1/auth"


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(COOKIE, token, max_age=settings.refresh_token_expire_days * 86400, httponly=True,
                        secure=settings.cookie_secure, samesite=settings.cookie_samesite, path=COOKIE_PATH)


def _check_origin(request: Request) -> None:
    """Défense CSRF supplémentaire pour les routes basées sur le cookie."""
    origin = request.headers.get("origin")
    if origin and origin not in settings.cors_origins:
        raise ForbiddenError("Origine non autorisée.")


def _token_out(r: AuthResult, db_user_view: UserView) -> s.TokenOut:
    return s.TokenOut(access_token=r.access_token, user=mappers.user_out(db_user_view))


@router.post("/register", response_model=s.UserOut, status_code=201)
@limiter.limit("10/hour")
def register(request: Request, body: s.RegisterIn, usecase: uc.RegisterUser = Depends(provide(uc.RegisterUser)),
             get_user: GetUser = Depends(provide(GetUser))):
    data = body.model_dump()
    role = data.pop("role")                       # SEEKER ou OWNER (jamais ADMIN)
    user = usecase.execute(RegisterCmd(**data, roles=[role]))
    return mappers.user_out(get_user.execute(user.id))


@router.post("/login", response_model=s.TokenOut)
@limiter.limit("10/minute")
def login(request: Request, response: Response, body: s.LoginIn, usecase: uc.LoginUser = Depends(provide(uc.LoginUser)),
          get_user: GetUser = Depends(provide(GetUser))):
    result = usecase.execute(body.email, body.password)
    _set_cookie(response, result.refresh_token)
    return _token_out(result, get_user.execute(result.user.id))


@router.post("/refresh", response_model=s.TokenOut)
@limiter.limit("60/minute")
def refresh(request: Request, response: Response, usecase: uc.RefreshSession = Depends(provide(uc.RefreshSession)),
            get_user: GetUser = Depends(provide(GetUser))):
    _check_origin(request)
    result = usecase.execute(request.cookies.get(COOKIE))
    _set_cookie(response, result.refresh_token)
    return _token_out(result, get_user.execute(result.user.id))


@router.post("/logout", response_model=Message)
def logout(request: Request, response: Response, usecase: uc.LogoutUser = Depends(provide(uc.LogoutUser))):
    _check_origin(request)
    usecase.execute(request.cookies.get(COOKIE))
    response.delete_cookie(COOKIE, path=COOKIE_PATH)
    return Message(detail="Vous êtes déconnecté.")


@router.post("/forgot-password", response_model=Message)
@limiter.limit("5/hour")
def forgot_password(request: Request, body: s.ForgotPasswordIn, usecase: uc.RequestPasswordReset = Depends(provide(uc.RequestPasswordReset))):
    usecase.execute(body.email)
    return Message(detail="Si un compte existe avec cette adresse, un e-mail vient d'être envoyé.")


@router.post("/reset-password", response_model=Message)
@limiter.limit("10/hour")
def reset_password(request: Request, body: s.ResetPasswordIn, usecase: uc.ResetPassword = Depends(provide(uc.ResetPassword))):
    usecase.execute(body.token, body.new_password)
    return Message(detail="Votre mot de passe a été modifié. Vous pouvez vous connecter.")