from rest_framework import routers

from .repository.views import RepositoryViewSet
from .repository.views import RepositoryVotesViewSet
from .repository.views import RepositoriesViewSet
from .repository.views import RepositoriesContributionsViewSet
from .repository.views import RepositoryCategoriesViewSet
from .repository.views import NewRepositoryViewSet
from .repository.views import RepositoryTranslatedExampleViewSet
from .repository.views import RepositoryExampleViewSet
from .repository.views import SearchRepositoriesViewSet
from .repository.views import NewRepositoryTranslatedExampleViewSet
from .repository.views import RepositoryTranslationsViewSet
from .repository.views import RepositoryUpdatesViewSet
from .repository.views import RequestAuthorizationViewSet
from .repository.views import ReviewAuthorizationRequestViewSet
from .repository.views import RepositoryAuthorizationViewSet
from .repository.views import RepositoryAuthorizationRoleViewSet
from .repository.views import RepositoryAuthorizationRequestsViewSet
from .examples.views import ExamplesViewSet
from .evaluate.views import EvaluateViewSet
from .evaluate.views import ResultsListViewSet
from .account.views import LoginViewSet
from .account.views import RegisterUserViewSet
from .account.views import ChangePasswordViewSet
from .account.views import RequestResetPasswordViewSet
from .account.views import UserProfileViewSet
from .account.views import SearchUserViewSet
from .account.views import ResetPasswordViewSet


class Router(routers.SimpleRouter):
    routes = [
        # Dynamically generated list routes.
        # Generated using @action decorator
        # on methods of the viewset.
        routers.DynamicRoute(
            url=r'^{prefix}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={},
        ),
        # Dynamically generated detail routes.
        # Generated using @action decorator on methods of the viewset.
        routers.DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}{trailing_slash}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={},
        ),
    ]

    def get_routes(self, viewset):
        ret = super().get_routes(viewset)
        lookup_field = getattr(viewset, 'lookup_field', None)

        if lookup_field:
            # List route.
            ret.append(routers.Route(
                url=r'^{prefix}{trailing_slash}$',
                mapping={
                    'get': 'list',
                    'post': 'create'
                },
                name='{basename}-list',
                detail=False,
                initkwargs={'suffix': 'List'},
            ))

        detail_url_regex = r'^{prefix}/{lookup}{trailing_slash}$'
        if not lookup_field:
            detail_url_regex = r'^{prefix}{trailing_slash}$'
        # Detail route.
        ret.append(routers.Route(
            url=detail_url_regex,
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ))

        return ret

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        lookup_fields = getattr(viewset, 'lookup_fields', None)
        if lookup_fields:
            base_regex = '(?P<{lookup_prefix}{lookup_url_kwarg}>[^/.]+)'
            return '/'.join(map(
                lambda x: base_regex.format(
                    lookup_prefix=lookup_prefix,
                    lookup_url_kwarg=x),
                lookup_fields))
        return super().get_lookup_regex(viewset, lookup_prefix)


router = Router()
router.register('repository/repository', RepositoryViewSet)
router.register('repository/categories', RepositoryCategoriesViewSet)
router.register('repository/repository-votes', RepositoryVotesViewSet)
router.register('repository/repositories', RepositoriesViewSet)
router.register(
    'repository/repositories-contributions',
    RepositoriesContributionsViewSet
)
router.register('repository/examples', ExamplesViewSet)
router.register('repository/new', NewRepositoryViewSet)
router.register('repository/evaluate/results', ResultsListViewSet)
router.register('repository/evaluate', EvaluateViewSet)
router.register('repository/translation', RepositoryTranslatedExampleViewSet)
router.register('repository/example', RepositoryExampleViewSet)
router.register('repository/search-repositories', SearchRepositoriesViewSet)
router.register(
    'repository/translate-example',
    NewRepositoryTranslatedExampleViewSet
)
router.register('repository/translations', RepositoryTranslationsViewSet)
router.register('repository/updates', RepositoryUpdatesViewSet)
router.register(
    'repository/request-authorization',
    RequestAuthorizationViewSet
)
router.register(
    'repository/review-authorization-request',
    ReviewAuthorizationRequestViewSet
)
router.register('repository/authorizations', RepositoryAuthorizationViewSet)
router.register(
    'repository/authorization-role',
    RepositoryAuthorizationRoleViewSet
)
router.register(
    'repository/authorization-requests',
    RepositoryAuthorizationRequestsViewSet
)
router.register('account/login', LoginViewSet)
router.register('account/register', RegisterUserViewSet)
router.register('account/change-password', ChangePasswordViewSet)
router.register('account/forgot-password', RequestResetPasswordViewSet)
router.register('account/user-profile', UserProfileViewSet)
router.register('account/search-user', SearchUserViewSet)
router.register('account/reset-password', ResetPasswordViewSet)
