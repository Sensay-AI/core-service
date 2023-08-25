"""Containers module."""

import logging.config
from typing import Any

import boto3
import sentry_sdk
from botocore.client import BaseClient
from dependency_injector import containers, providers
from dependency_injector.providers import Resource
from langchain.llms import OpenAI

from app.infrastructure.auth0.auth0 import Auth0Service
from app.infrastructure.aws.s3 import S3Service
from app.infrastructure.db.database import Database
from app.infrastructure.llm.vocabulary import ChatGPTVocabularyGenerator
from app.models.db.difficulty_levels import DifficultyLevels
from app.models.db.language import Language
from app.models.db.vocabulary import Category, VocabularyPrompt
from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.vocabulary_repository import VocabularyRepository
from app.services.base_service import BaseService
from app.services.user_service import UserService
from app.services.vocabulary_service import VocabularyService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            # "app.routes.api_v1.endpoints.image_upload",
            "app.routes.api_v1.endpoints.user",
            "app.routes.api_v1.endpoints.auth",
            "app.routes.api_v1.endpoints.language",
            "app.routes.api_v1.endpoints.vocabulary",
            "app.routes.api_v1.endpoints.difficulty_level",
        ]
    )

    config = providers.Configuration(yaml_files=["config.yml"])

    env_name = providers.Resource(config.core.app.env)

    logging = providers.Resource(
        logging.config.fileConfig,
        fname=config.core.app.logger.config_file[env_name],
    )

    sentry_sdk = providers.Resource(  # type: ignore [var-annotated]
        sentry_sdk.init,
        dsn=config.infrastructures.sentry.dsn[env_name],
        # TODO: traces_sample_rate may have to update when the app up and running on prod
        traces_sample_rate=1.0,
        environment=env_name,
    )

    db = providers.Singleton(Database, db_url=config.infrastructures.db.url)

    auth = providers.Singleton(
        Auth0Service,
        domain=config.infrastructures.auth0.domain,
        algorithms=config.infrastructures.auth0.algorithms,
        audience=config.infrastructures.auth0.audience,
        issuer=config.infrastructures.auth0.issuer,
    )

    user_repository = providers.Factory(
        UserRepository,
        session_factory=db.provided.session,
    )

    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )

    sts_client: Resource[BaseClient] = providers.Resource(
        boto3.client,
        "sts",
        aws_access_key_id=config.infrastructures.aws.aws_access_key_id,
        aws_secret_access_key=config.infrastructures.aws.aws_secret_access_key,
    )

    temp_credentials = providers.Resource(sts_client.provided.get_session_token.call())

    session: Resource[boto3.session.Session] = providers.Resource(
        boto3.session.Session,
        aws_access_key_id=temp_credentials.provided["Credentials"]["AccessKeyId"],
        aws_secret_access_key=temp_credentials.provided["Credentials"][
            "SecretAccessKey"
        ],
        aws_session_token=temp_credentials.provided["Credentials"]["SessionToken"],
    )

    s3_client = providers.Resource(
        session.provided.client.call(),
        service_name="s3",
    )

    s3_service = providers.Factory(
        S3Service,
        s3_client=s3_client,
    )

    s3_image_bucket = providers.Resource(
        config.infrastructures.aws.s3_image_bucket[env_name]
    )

    open_ai: OpenAI = providers.Singleton(
        OpenAI,
        openai_api_key=config.infrastructures.open_ai.openai_api_key,
        max_tokens=config.infrastructures.open_ai.max_tokens,
        temperature=config.infrastructures.open_ai.temperature,
    )

    chatGPT_vocabulary_generator = providers.Singleton(
        ChatGPTVocabularyGenerator, model=open_ai
    )

    language_repository = providers.Factory(
        BaseRepository, model=Language, session_factory=db.provided.session
    )

    category_repository = providers.Factory(
        BaseRepository[Category, Any, Any],
        model=Category,
        session_factory=db.provided.session,
    )

    difficulty_levels_repository = providers.Factory(
        BaseRepository[DifficultyLevels, Any, Any],
        model=DifficultyLevels,
        session_factory=db.provided.session,
    )

    vocabulary_repository = providers.Factory(
        VocabularyRepository,
        model=VocabularyPrompt,
        session_factory=db.provided.session,
    )

    vocabulary_service = providers.Factory(
        VocabularyService,
        voca_generator=chatGPT_vocabulary_generator,
        voca_repository=vocabulary_repository,
    )

    category_service = providers.Factory(BaseService, repository=category_repository)

    language_service = providers.Factory(BaseService, repository=language_repository)

    difficulty_levels_service = providers.Factory(
        BaseService, repository=difficulty_levels_repository
    )
