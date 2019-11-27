import json
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import parsers
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import APIException

from bothub.api.v2.mixins import MultipleFieldLookupMixin
from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryCategory
from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryUpdate

from ..metadata import Metadata
from .serializers import RepositorySerializer
from .serializers import RepositoryAuthorizationRoleSerializer
from .serializers import RepositoryContributionsSerializer
from .serializers import RepositoryVotesSerializer
from .serializers import ShortRepositorySerializer
from .serializers import RepositoryCategorySerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import RequestRepositoryAuthorizationSerializer
from .serializers import RepositoryExampleSerializer
from .serializers import AnalyzeTextSerializer
from .serializers import EvaluateSerializer
from .serializers import RepositoryUpdateSerializer
from .serializers import RepositoryUpload
from .permissions import RepositoryPermission
from .permissions import RepositoryAdminManagerAuthorization
from .permissions import RepositoryExamplePermission
from .permissions import RepositoryUpdateHasPermission
from .filters import RepositoriesFilter
from .filters import RepositoryAuthorizationFilter
from .filters import RepositoryAuthorizationRequestsFilter
from .filters import RepositoryUpdatesFilter


class RepositoryViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Manager repository (bot).
    """

    queryset = Repository.objects
    lookup_field = "uuid"
    lookup_fields = ["uuid"]
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, RepositoryPermission]
    metadata_class = Metadata

    @action(
        detail=True,
        methods=["GET"],
        url_name="repository-languages-status",
        lookup_fields=["uuid"],
    )
    def languagesstatus(self, request, **kwargs):
        """
        Get current language status.
        """
        if self.lookup_field not in kwargs:
            return Response(status=405)

        repository = self.get_object()
        return Response({"languages_status": repository.languages_status})

    @action(
        detail=True,
        methods=["GET"],
        url_name="repository-train",
        lookup_fields=["uuid"],
    )
    def train(self, request, **kwargs):
        """
        Train current update using Bothub NLP service
        """
        if self.lookup_field not in kwargs:
            return Response({}, status=403)
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()
        request = repository.request_nlp_train(user_authorization)  # pragma: no cover
        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": request.status_code}, code=request.status_code
            )
        return Response(request.json())  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-analyze",
        permission_classes=[],
        lookup_fields=["uuid"],
    )
    def analyze(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = AnalyzeTextSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        if (
            request.data.get("update")
            and RepositoryUpdate.objects.filter(
                pk=request.data.get("update"), repository=kwargs.get("uuid")
            ).count()
            == 0
        ):
            raise PermissionDenied()

        request = repository.request_nlp_analyze(
            user_authorization, serializer.data
        )  # pragma: no cover

        if request.status_code == status.HTTP_200_OK:  # pragma: no cover
            return Response(request.json())  # pragma: no cover

        response = None  # pragma: no cover
        try:  # pragma: no cover
            response = request.json()  # pragma: no cover
        except Exception:
            pass

        if not response:  # pragma: no cover
            raise APIException(  # pragma: no cover
                detail=_(
                    "Something unexpected happened! " + "We couldn't analyze your text."
                )
            )
        error = response.get("error")  # pragma: no cover
        message = error.get("message")  # pragma: no cover
        raise APIException(detail=message)  # pragma: no cover

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-evaluate",
        lookup_fields=["uuid"],
    )
    def evaluate(self, request, **kwargs):
        """
        Evaluate repository using Bothub NLP service
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()
        serializer = EvaluateSerializer(data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        if not repository.evaluations(language=request.data.get("language")).count():
            raise APIException(
                detail=_("You need to have at least " + "one registered test phrase")
            )  # pragma: no cover

        if len(repository.intents) <= 1:
            raise APIException(
                detail=_("You need to have at least " + "two registered intents")
            )  # pragma: no cover

        request = repository.request_nlp_evaluate(  # pragma: no cover
            user_authorization, serializer.data
        )
        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {"status_code": request.status_code}, code=request.status_code
            )
        return Response(request.json())  # pragma: no cover


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user",
                openapi.IN_QUERY,
                description="Nickname User to find repositories votes",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "repository",
                openapi.IN_QUERY,
                description="Repository UUID, returns a list of "
                "users who voted for this repository",
                type=openapi.TYPE_STRING,
            ),
        ]
    ),
)
class RepositoryVotesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Manager repository votes (bot).
    """

    queryset = RepositoryVote.objects.all()
    lookup_field = "repository"
    lookup_fields = ["repository"]
    serializer_class = RepositoryVotesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    metadata_class = Metadata

    def get_queryset(self, *args, **kwargs):
        if self.request.query_params.get("repository", None):
            return self.queryset.filter(
                repository=self.request.query_params.get("repository", None)
            )
        elif self.request.query_params.get("user", None):
            return self.queryset.filter(
                user__nickname=self.request.query_params.get("user", None)
            )
        else:
            return self.queryset.all()

    def destroy(self, request, *args, **kwargs):
        self.queryset.filter(
            repository=self.request.query_params.get("repository", None),
            user=self.request.user,
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all public repositories.
    """

    serializer_class = ShortRepositorySerializer
    queryset = Repository.objects.all().publics().order_by_relevance()
    filter_class = RepositoriesFilter
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["$name", "^name", "=name"]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="Nickname User",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
class RepositoriesContributionsViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List Repositories Contributions by user.
    """

    serializer_class = RepositoryContributionsSerializer
    queryset = RepositoryAuthorization.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "nickname"

    def get_queryset(self):
        if self.request.query_params.get("nickname", None):
            return self.queryset.filter(
                user__nickname=self.request.query_params.get("nickname", None)
            )
        else:
            return self.queryset.none()


class RepositoryCategoriesView(mixins.ListModelMixin, GenericViewSet):
    """
    List all categories.
    """

    serializer_class = RepositoryCategorySerializer
    queryset = RepositoryCategory.objects.all()
    pagination_class = None


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="Nickname User to find repositories",
                type=openapi.TYPE_STRING,
            )
        ]
    ),
)
class SearchRepositoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all user's repositories
    """

    queryset = Repository.objects
    serializer_class = RepositorySerializer
    lookup_field = "nickname"

    def get_queryset(self, *args, **kwargs):
        try:
            if self.request.query_params.get("nickname", None):
                return self.queryset.filter(
                    owner__nickname=self.request.query_params.get(
                        "nickname", self.request.user
                    ),
                    is_private=False,
                )
            else:
                return self.queryset.filter(owner=self.request.user)
        except TypeError:
            return self.queryset.none()


class RepositoryAuthorizationViewSet(
    MultipleFieldLookupMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = RepositoryAuthorization.objects.exclude(
        role=RepositoryAuthorization.ROLE_NOT_SETTED
    )
    serializer_class = RepositoryAuthorizationSerializer
    filter_class = RepositoryAuthorizationFilter
    lookup_fields = ["repository__uuid", "user__nickname"]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        repository_uuid = self.kwargs.get("repository__uuid")
        user_nickname = self.kwargs.get("user__nickname")

        repository = get_object_or_404(Repository, uuid=repository_uuid)
        user = get_object_or_404(User, nickname=user_nickname)

        obj = repository.get_user_authorization(user)

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, *args, **kwargs):
        self.lookup_field = "user__nickname"

        self.filter_class = None
        self.serializer_class = RepositoryAuthorizationRoleSerializer
        self.permission_classes = [IsAuthenticated, RepositoryAdminManagerAuthorization]
        response = super().update(*args, **kwargs)
        instance = self.get_object()
        if instance.role is not RepositoryAuthorization.ROLE_NOT_SETTED:
            instance.send_new_role_email(self.request.user)
        return response

    def list(self, request, *args, **kwargs):
        self.lookup_fields = []
        return super().list(request, *args, **kwargs)


class RepositoryAuthorizationRequestsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    List of all authorization requests for a repository
    """

    queryset = RequestRepositoryAuthorization.objects.exclude(approved_by__isnull=False)
    serializer_class = RequestRepositoryAuthorizationSerializer
    filter_class = RepositoryAuthorizationRequestsFilter
    permission_classes = [IsAuthenticated]
    metadata_class = Metadata

    def create(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        self.permission_classes = [IsAuthenticated, RepositoryAdminManagerAuthorization]
        try:
            return super().update(request, *args, **kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.message)

    def destroy(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        self.permission_classes = [IsAuthenticated, RepositoryAdminManagerAuthorization]
        return super().destroy(request, *args, **kwargs)


class RepositoryExampleViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    Manager repository example.

    retrieve:
    Get repository example data.

    delete:
    Delete repository example.

    update:
    Update repository example.

    """

    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [RepositoryExamplePermission]

    def create(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        return super().create(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-upload-examples",
        parser_classes=[parsers.MultiPartParser],
        serializer_class=RepositoryUpload,
    )
    def upload_examples(self, request, **kwargs):
        try:
            repository = get_object_or_404(
                Repository, pk=request.data.get("repository")
            )
        except DjangoValidationError:
            raise PermissionDenied()

        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()

        f = request.FILES.get("file")
        try:
            json_data = json.loads(f.read().decode())
        except json.decoder.JSONDecodeError:
            raise UnsupportedMediaType("json")

        count_added = 0
        not_added = []

        for data in json_data:
            response_data = data
            response_data["repository"] = request.data.get("repository")
            serializer = RepositoryExampleSerializer(
                data=response_data, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                count_added += 1
            else:
                not_added.append(data)

        return Response({"added": count_added, "not_added": not_added})

    def perform_destroy(self, obj):
        if obj.deleted_in:
            raise APIException(_("Example already deleted"))
        obj.delete()


class RepositoryUpdatesViewSet(
    mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    queryset = (
        RepositoryUpdate.objects.filter(training_started_at__isnull=False)
        .order_by("-trained_at")
        .order_by("-publish")
    )
    serializer_class = RepositoryUpdateSerializer
    permission_classes = [IsAuthenticated, RepositoryUpdateHasPermission]

    def list(self, request, *args, **kwargs):
        self.filter_class = RepositoryUpdatesFilter
        return super().list(request, *args, **kwargs)
