import json
import uuid

from django.test import TestCase
from django.test import RequestFactory
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import Repository
from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryUpdate
from bothub.common import languages

from bothub.api.v2.tests.utils import create_user_and_token

from bothub.api.v2.repository.views import RepositoryViewSet
from bothub.api.v2.repository.views import \
    NewRepositoryTranslatedExampleViewSet
from bothub.api.v2.repository.views import RepositoriesContributionsViewSet
from bothub.api.v2.repository.views import RepositoriesViewSet
from bothub.api.v2.repository.views import RepositoryVotesViewSet
from bothub.api.v2.repository.views import RepositoryCategoriesViewSet
from bothub.api.v2.repository.views import NewRepositoryViewSet
from bothub.api.v2.repository.views import RepositoryTranslatedExampleViewSet
from bothub.api.v2.repository.views import RepositoryExampleViewSet
from bothub.api.v2.repository.views import SearchRepositoriesViewSet
from bothub.api.v2.repository.views import RepositoryTranslationsViewSet
from bothub.api.v2.repository.views import RepositoryUpdatesViewSet
from bothub.api.v2.repository.views import RequestAuthorizationViewSet
from bothub.api.v2.repository.views import ReviewAuthorizationRequestViewSet
from bothub.api.v2.repository.views import RepositoryAuthorizationViewSet
from bothub.api.v2.repository.views import RepositoryAuthorizationRoleViewSet
from bothub.api.v2.repository.views import \
    RepositoryAuthorizationRequestsViewSet
from bothub.api.v2.repository.serializers import RepositorySerializer


def get_valid_mockups(categories):
    return [
        {
            'name': 'Repository 1',
            'slug': 'repository-1',
            'language': languages.LANGUAGE_EN,
            'categories': [
                category.pk
                for category in categories
            ],
            'is_private': True,
        },
        {
            'name': 'Repository 2',
            'slug': 'repo2',
            'language': languages.LANGUAGE_PT,
            'categories': [
                category.pk
                for category in categories
            ],
            'is_private': False,
        },
    ]


def get_invalid_mockups(categories):
    return [
        {
            'name': '',
            'slug': 'repository-1',
            'language': languages.LANGUAGE_EN,
            'categories': [
                category.pk
                for category in categories
            ],
            'is_private': True,
        },
        {
            'name': 'Repository 2',
            'slug': '',
            'language': languages.LANGUAGE_PT,
            'categories': [
                category.pk
                for category in categories
            ],
            'is_private': False,
        },
        {
            'name': 'Repository 3',
            'slug': 'repo3',
            'language': 'out',
            'categories': [
                category.pk
                for category in categories
            ],
            'is_private': False,
        },
        {
            'name': 'Repository 4',
            'slug': 'repository 4',
            'language': languages.LANGUAGE_EN,
            'categories': [
                category.pk
                for category in categories
            ],
            'is_private': True,
        },
    ]


def create_repository_from_mockup(owner, categories, **mockup):
    r = Repository.objects.create(
        owner_id=owner.id,
        **mockup)
    for category in categories:
        r.categories.add(category)
    return r


class CreateRepositoryAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token('user')
        self.category = RepositoryCategory.objects.create(name='Category 1')

    def request(self, data, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.post(
            '/v2/repository/repository/',
            data,
            **authorization_header)

        response = RepositoryViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        for mockup in get_valid_mockups([self.category]):
            response, content_data = self.request(
                mockup,
                self.owner_token)

            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED)

            repository = self.owner.repositories.get(
                uuid=content_data.get('uuid'))

            self.assertEqual(
                repository.name,
                mockup.get('name'))
            self.assertEqual(
                repository.slug,
                mockup.get('slug'))
            self.assertEqual(
                repository.language,
                mockup.get('language'))
            self.assertEqual(
                repository.is_private,
                mockup.get('is_private'))

    def test_invalid_data(self):
        for mockup in get_invalid_mockups([self.category]):
            response, content_data = self.request(
                mockup,
                self.owner_token)

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST)


class RetriveRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.category = RepositoryCategory.objects.create(name='Category 1')

        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.get(
            '/v2/repository/repository/{}/'.format(repository.uuid),
            **authorization_header)

        response = RepositoryViewSet.as_view({'get': 'retrieve'})(
            request,
            uuid=repository.uuid)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        for repository in self.repositories:
            response, content_data = self.request(repository, self.owner_token)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK)

    def test_private_repository(self):
        for repository in self.repositories:
            response, content_data = self.request(repository)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED
                if repository.is_private else status.HTTP_200_OK)


class UpdateRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token('user')
        self.category = RepositoryCategory.objects.create(name='Category 1')

        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, data={}, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.patch(
            '/v2/repository/repository/{}/'.format(repository.uuid),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header)

        response = RepositoryViewSet.as_view({'patch': 'update'})(
            request,
            uuid=repository.uuid,
            partial=True)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay_update_name(self):
        for repository in self.repositories:
            response, content_data = self.request(
                repository,
                {
                    'name': 'Repository {}'.format(repository.uuid),
                },
                self.owner_token)

            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK)

    def test_unauthorized(self):
        for repository in self.repositories:
            response, content_data = self.request(
                repository,
                {
                    'name': 'Repository {}'.format(repository.uuid),
                },
                self.user_token)

            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN)


class RepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user, self.user_token = create_user_and_token()
        self.owner, self.owner_token = create_user_and_token('owner')
        self.category = RepositoryCategory.objects.create(name='Category 1')

        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.get(
            '/v2/repository/repository/{}/'.format(repository.uuid),
            **authorization_header)

        response = RepositoryViewSet.as_view({'get': 'retrieve'})(
            request,
            uuid=repository.uuid)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_authorization_without_user(self):
        for repository in self.repositories:
            # ignore private repositories
            if repository.is_private:
                continue
            response, content_data = self.request(repository)
            self.assertIsNone(content_data.get('authorization'))

    def test_authorization_with_user(self):
        for repository in self.repositories:
            user, user_token = (self.owner, self.owner_token) \
                if repository.is_private else (self.user, self.user_token)
            response, content_data = self.request(repository, user_token)
            authorization = content_data.get('authorization')
            self.assertIsNotNone(authorization)
            self.assertEqual(
                authorization.get('uuid'),
                str(repository.get_user_authorization(user).uuid))


class RepositoryAvailableRequestAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user, self.user_token = create_user_and_token()
        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, repository, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.get(
            '/v2/repository/repository/{}/'.format(repository.uuid),
            **authorization_header)

        response = RepositoryViewSet.as_view({'get': 'retrieve'})(
            request,
            uuid=repository.uuid)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_owner_ever_false(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token)
        available_request_authorization = content_data.get(
            'available_request_authorization')
        self.assertFalse(available_request_authorization)

    def test_user_available(self):
        response, content_data = self.request(
            self.repository,
            self.user_token)
        available_request_authorization = content_data.get(
            'available_request_authorization')
        self.assertTrue(available_request_authorization)

    def test_false_when_request(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            text='r')
        response, content_data = self.request(
            self.repository,
            self.user_token)
        available_request_authorization = content_data.get(
            'available_request_authorization')
        self.assertFalse(available_request_authorization)


class IntentsInRepositorySerializerTestCase(TestCase):
    def setUp(self):
        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')

    def test_count_1(self):
        repository_data = RepositorySerializer(self.repository).data
        intent = repository_data.get('intents')[0]
        self.assertEqual(intent.get('examples__count'), 1)

    def test_example_deleted(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        repository_data = RepositorySerializer(self.repository).data
        intent = repository_data.get('intents')[0]
        self.assertEqual(intent.get('examples__count'), 2)
        example.delete()
        repository_data = RepositorySerializer(self.repository).data
        intent = repository_data.get('intents')[0]
        self.assertEqual(intent.get('examples__count'), 1)


class RepositoriesViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token('owner')
        self.category_1 = RepositoryCategory.objects.create(name='Category 1')
        self.category_2 = RepositoryCategory.objects.create(name='Category 2')
        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category_1])
        ]
        self.public_repositories = list(
            filter(
                lambda r: not r.is_private,
                self.repositories,
            )
        )

    def request(self, data={}, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.get(
            '/v2/repository/repositories/',
            data,
            **authorization_header,
        )
        response = RepositoriesViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_count(self):
        public_repositories_length = len(self.public_repositories)
        response, content_data = self.request()
        self.assertEqual(
            content_data.get('count'),
            public_repositories_length,
        )

    def test_name_filter(self):
        response, content_data = self.request({
            'name': self.public_repositories[0].name,
        })
        self.assertEqual(
            content_data.get('count'),
            1,
        )
        response, content_data = self.request({
            'name': 'abc',
        })
        self.assertEqual(
            content_data.get('count'),
            0,
        )

    def test_category_filter(self):
        response, content_data = self.request({
            'categories': [
                self.category_1.id,
            ],
        })
        self.assertEqual(
            content_data.get('count'),
            1,
        )
        response, content_data = self.request({
            'categories': [
                self.category_2.id,
            ],
        })
        self.assertEqual(
            content_data.get('count'),
            0,
        )


class RepositoriesLanguageFilterTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository_en_1 = Repository.objects.create(
            owner=self.owner,
            name='Testing en_1',
            slug='test en_1',
            language=languages.LANGUAGE_EN)
        self.repository_en_2 = Repository.objects.create(
            owner=self.owner,
            name='Testing en_2',
            slug='en_2',
            language=languages.LANGUAGE_EN)
        self.repository_pt = Repository.objects.create(
            owner=self.owner,
            name='Testing pt',
            slug='pt',
            language=languages.LANGUAGE_PT)

    def request(self, data={}, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.get(
            '/v2/repository/repositories/',
            data,
            **authorization_header,
        )
        response = RepositoriesViewSet.as_view({'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_main_language(self):
        response, content_data = self.request({
            'language': languages.LANGUAGE_EN,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            content_data.get('count'),
            2,
        )
        response, content_data = self.request({
            'language': languages.LANGUAGE_PT,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            content_data.get('count'),
            1,
        )

    def test_example_language(self):
        language = languages.LANGUAGE_ES
        example = RepositoryExample.objects.create(
            repository_update=self.repository_en_1.current_update(language),
            text='hi',
            intent='greet')
        response, content_data = self.request({
            'language': language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            content_data.get('count'),
            1,
        )
        example.delete()
        response, content_data = self.request({
            'language': language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            content_data.get('count'),
            0,
        )

    def test_translated_example(self):
        language = languages.LANGUAGE_ES
        example = RepositoryExample.objects.create(
            repository_update=self.repository_en_1.current_update(),
            text='hi',
            intent='greet')
        translated = RepositoryTranslatedExample.objects.create(
            original_example=example,
            language=language,
            text='hola'
        )
        response, content_data = self.request({
            'language': language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            content_data.get('count'),
            1,
        )
        translated.delete()
        response, content_data = self.request({
            'language': language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            content_data.get('count'),
            0,
        )


class ListRepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN
        )

        self.repository_empty = Repository.objects.create(
            owner=self.owner,
            name='Testing_empty',
            slug='test_empty',
            language=languages.LANGUAGE_EN
        )

        self.repository_votes = RepositoryVote.objects.create(
            user=self.owner,
            repository=self.repository
        )

    def request(self, param, value, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token),
        }
        request = self.factory.get(
            '/v2/repository/repository-votes/?{}={}'.format(
                param,
                value
            ), **authorization_header
        )
        response = RepositoryVotesViewSet.as_view({'get': 'list'})(
            request,
            repository=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_repository_okay(self):
        response, content_data = self.request(
            'repository',
            self.repository.uuid,
            self.owner_token.key
        )

        self.assertEqual(content_data['count'], 1)
        self.assertEqual(len(content_data['results']), 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_private_repository_okay(self):
        response, content_data = self.request(
            'repository',
            self.repository.uuid,
            ''
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED)

    def test_user_okay(self):
        response, content_data = self.request(
            'user',
            self.owner.nickname,
            self.owner_token.key
        )

        self.assertEqual(content_data['count'], 1)
        self.assertEqual(len(content_data['results']), 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

    def test_private_user_okay(self):
        response, content_data = self.request(
            'user',
            self.owner.nickname,
            ''
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED)

    def test_repository_empty(self):
        response, content_data = self.request(
            'repository',
            self.repository_empty.uuid,
            self.owner_token.key
        )
        self.assertEqual(content_data['count'], 0)
        self.assertEqual(len(content_data['results']), 0)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)


class NewRepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN
        )

    def request(self, data, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token),
        }
        request = self.factory.post(
            '/v2/repository/repository-votes/',
            json.dumps(data),
            content_type='application/json',
            **authorization_header
        )
        response = RepositoryVotesViewSet.as_view({'post': 'create'})(
            request,
            repository=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'repository': str(self.repository.uuid)
            }, self.owner_token.key)
        self.assertEqual(content_data['user'], self.owner.id)
        self.assertEqual(
            content_data['repository'],
            str(self.repository.uuid)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_private_okay(self):
        response, content_data = self.request(
            {
                'repository': str(self.repository.uuid)
            }, '')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class DestroyRepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN
        )

        self.repository_votes = RepositoryVote.objects.create(
            user=self.owner,
            repository=self.repository
        )

    def request(self, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token),
        }
        request = self.factory.delete(
            '/v2/repository/repository-votes/{}/'.format(
                str(self.repository.uuid)
            ), **authorization_header
        )
        response = RepositoryVotesViewSet.as_view({'delete': 'destroy'})(
            request,
            repository=self.repository.uuid
        )
        response.render()
        return response

    def test_okay(self):
        response = self.request(self.owner_token.key)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_private_okay(self):
        response = self.request('')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class ListRepositoryContributionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN
        )

        text = 'I can contribute'
        self.repository_request_auth = \
            RequestRepositoryAuthorization.objects.create(
                user=self.user,
                repository=self.repository,
                approved_by=self.owner,
                text=text
            )

        self.repository_auth = RepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            role=0
        )

    def request(self, nickname):
        request = self.factory.get(
            '/v2/repository/repositories-contributions/?nickname={}'.format(
                nickname
            )
        )
        response = RepositoriesContributionsViewSet.as_view({'get': 'list'})(
            request,
            nickname=nickname
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(self.user.nickname)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            content_data['count'],
            1
        )
        self.assertEqual(
            len(content_data['results']),
            1
        )

    def test_without_nickname(self):
        response, content_data = self.request('')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(content_data['count'], 0)
        self.assertEqual(len(content_data['results']), 0)


class ListRepositoryCategoriesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.category = RepositoryCategory.objects.create(name='Category 1')
        self.business_category = RepositoryCategory.objects.create(
            name='Business',
            icon='business')

    def request(self):
        request = self.factory.get('/v2/repository/categories/')
        response = RepositoryCategoriesViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_default_category_icon(self):
        response, content_data = self.request()
        self.assertEqual(
            content_data[0].get('id'),
            self.category.id)
        self.assertEqual(
            content_data[0].get('icon'),
            'botinho')

    def test_custom_category_icon(self):
        response, content_data = self.request()
        self.assertEqual(
            content_data[1].get('id'),
            self.business_category.id)
        self.assertEqual(
            content_data[1].get('icon'),
            self.business_category.icon)


class NewRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user, self.token = create_user_and_token()
        self.authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
        }

        self.category = RepositoryCategory.objects.create(
            name='ID')

    def request(self, data):
        request = self.factory.post(
            '/v2/repository/new/',
            data,
            **self.authorization_header)
        response = NewRepositoryViewSet.as_view({'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'name': 'Testing',
            'slug': 'test',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
            'description': '',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_fields_required(self):
        def request_and_check(field, data):
            response, content_data = self.request(data)
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, content_data.keys())

        request_and_check('name', {
            'slug': 'test',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })

        request_and_check('slug', {
            'name': 'Testing',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })

        request_and_check('language', {
            'name': 'Testing',
            'slug': 'test',
            'categories': [self.category.id],
        })

        request_and_check('categories', {
            'name': 'Testing',
            'slug': 'test',
            'language': languages.LANGUAGE_EN,
        })

    def test_invalid_slug(self):
        response, content_data = self.request({
            'name': 'Testing',
            'slug': 'invalid slug',
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('slug', content_data.keys())

    def test_invalid_language(self):
        response, content_data = self.request({
            'name': 'Testing',
            'slug': 'test',
            'language': 'jj',
            'categories': [self.category.id],
            'description': '',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('language', content_data.keys())

    def test_unique_slug(self):
        same_slug = 'test'
        Repository.objects.create(
            owner=self.user,
            name='Testing',
            slug=same_slug,
            language=languages.LANGUAGE_EN)
        response, content_data = self.request({
            'name': 'Testing',
            'slug': same_slug,
            'language': languages.LANGUAGE_EN,
            'categories': [self.category.id],
            'description': '',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', content_data.keys())


class RepositoryTranslatedExampleRetrieveTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='oi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')
        self.private_translated = RepositoryTranslatedExample.objects.create(
            original_example=self.private_example,
            language=languages.LANGUAGE_PT,
            text='oi')

    def request(self, translated, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/v2/repository/translation/{}/'.format(translated.id),
            **authorization_header)
        response = RepositoryTranslatedExampleViewSet.as_view(
            {'get': 'retrieve'})(request, pk=translated.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.translated,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.translated.id)

    def test_private_okay(self):
        response, content_data = self.request(
            self.private_translated,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('id'),
            self.private_translated.id)

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            self.private_translated,
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryTranslatedExampleDestroyTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='oi')

    def request(self, translated, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/v2/repository/translation/{}/'.format(translated.id),
            **authorization_header)
        response = RepositoryTranslatedExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=translated.id)
        return response

    def test_okay(self):
        response = self.request(
            self.translated,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response = self.request(
            self.translated,
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryExampleDestroyTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')

    def request(self, example, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.delete(
            '/v2/repository/example/{}/'.format(example.id),
            **authorization_header)
        response = RepositoryExampleViewSet.as_view(
            {'delete': 'destroy'})(request, pk=example.id)
        return response

    def test_okay(self):
        response = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(
            self.private_example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        response = self.request(
            self.example,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_private_forbidden(self):
        response = self.request(
            self.private_example,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.example.delete()

        response = self.request(
            self.example,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR)


class RepositoryExampleUpdateTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing Private',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)
        self.private_example = RepositoryExample.objects.create(
            repository_update=self.private_repository.current_update(),
            text='hi')

    def request(self, example, token, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.patch(
            '/v2/repository/example/{}/'.format(example.id),
            json.dumps(data),
            content_type='application/json',
            **authorization_header)
        response = RepositoryExampleViewSet.as_view(
            {'patch': 'update'})(request, pk=example.id)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        text = 'teste'
        intent = 'teste1234'

        response, content_data = self.request(
            self.example,
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": text,
                "intent": intent
            }
        )

        print(content_data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('text'),
            text)
        self.assertEqual(
            content_data.get('intent'),
            intent)

    def test_private_forbidden(self):
        response, content_data = self.request(
            self.private_example,
            self.user_token,
            {"text": 'teste', "intent": 'teste1234'})

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class SearchRepositoriesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.category = RepositoryCategory.objects.create(
            name='ID')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.repository.categories.add(self.category)

    def request(self, nickname):
        request = self.factory.get(
            '/v2/repository/search-repositories/?nickname={}'.format(nickname)
        )
        response = SearchRepositoriesViewSet.as_view(
            {'get': 'list'}
        )(request, nickname=nickname)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request('owner')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            uuid.UUID(content_data.get('results')[0].get('uuid')),
            self.repository.uuid)

    def test_empty_with_user_okay(self):
        response, content_data = self.request('fake')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('count'),
            0)

    def test_empty_without_user_okay(self):
        response, content_data = self.request('')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content_data.get('count'),
            0)


class TranslateExampleTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')

    def request(self, data, user_token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(user_token.key),
        }
        request = self.factory.post(
            '/v2/repository/translate-example/',
            json.dumps(data),
            content_type='application/json',
            **authorization_header)
        response = NewRepositoryTranslatedExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'oi',
                'entities': [],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_unique_translate(self):
        language = languages.LANGUAGE_PT
        text = 'oi'

        RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=language,
            text=text)

        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': language,
                'text': text,
                'entities': [],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'non_field_errors',
            content_data.keys())

    def test_forbidden(self):
        user, user_token = create_user_and_token()

        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'oi',
                'entities': [],
            },
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_okay_with_entities(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=example,
            start=11,
            end=18,
            entity='name')
        response, content_data = self.request(
            {
                'original_example': example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'meu nome é douglas',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                ],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_entities_no_valid(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')
        response, content_data = self.request(
            {
                'original_example': example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'meu nome é douglas',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'nome',
                    },
                ],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_entities_no_valid_2(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='my name is douglas')
        RepositoryExampleEntity.objects.create(
            repository_example=self.example,
            start=11,
            end=18,
            entity='name')
        response, content_data = self.request(
            {
                'original_example': example.id,
                'language': languages.LANGUAGE_PT,
                'text': 'meu nome é douglas',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                    {
                        'start': 0,
                        'end': 3,
                        'entity': 'my',
                    },
                ],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_can_not_translate_to_same_language(self):
        response, content_data = self.request(
            {
                'original_example': self.example.id,
                'language': self.example.repository_update.language,
                'text': 'oi',
                'entities': [],
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'language',
            content_data.keys())


class TranslationsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        self.example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(),
            text='hi')
        self.translated = RepositoryTranslatedExample.objects.create(
            original_example=self.example,
            language=languages.LANGUAGE_PT,
            text='oi')

    def request(self, data, user_token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(user_token.key),
        } if user_token else {}
        request = self.factory.get(
            '/v2/repository/translations/',
            data,
            **authorization_header)
        response = RepositoryTranslationsViewSet.as_view(
            {'get': 'list'}
        )(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_repository_not_found(self):
        response, content_data = self.request({
            'repository_uuid': uuid.uuid4(),
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_repository_uuid_invalid(self):
        response, content_data = self.request({
            'repository_uuid': 'invalid',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND)

    def test_forbidden(self):
        private_repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='private',
            language=languages.LANGUAGE_EN,
            is_private=True)

        response, content_data = self.request({
            'repository_uuid': private_repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

        user, user_token = create_user_and_token('user')
        response, content_data = self.request(
            {
                'repository_uuid': private_repository.uuid,
            },
            user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_filter_from_language(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_ES),
            text='hola')
        translated = RepositoryTranslatedExample.objects.create(
            original_example=example,
            language=languages.LANGUAGE_PT,
            text='oi')

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'from_language': self.example.repository_update.language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            content_data.get('results')[0].get('id'),
            self.translated.id)

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'from_language': example.repository_update.language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            content_data.get('results')[0].get('id'),
            translated.id)

    def test_filter_to_language(self):
        example = RepositoryExample.objects.create(
            repository_update=self.repository.current_update(
                languages.LANGUAGE_ES),
            text='hola')
        RepositoryTranslatedExample.objects.create(
            original_example=example,
            language=languages.LANGUAGE_PT,
            text='oi')

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'to_language': self.translated.language,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'to_language': languages.LANGUAGE_DE,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            0)


class RepositoryUpdatesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)
        current_update = self.repository.current_update()
        RepositoryExample.objects.create(
            repository_update=current_update,
            text='my name is Douglas',
            intent='greet')
        RepositoryExample.objects.create(
            repository_update=current_update,
            text='my name is John',
            intent='greet')
        current_update.start_training(self.owner)

    def request(self, data, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.get(
            '/v2/repository/updates/',
            data,
            **authorization_header)
        response = RepositoryUpdatesViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            {
                'repository_uuid': str(self.repository.uuid),
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_not_authenticated(self):
        response, content_data = self.request(
            {
                'repository_uuid': str(self.repository.uuid),
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED)

    def test_without_repository(self):
        response, content_data = self.request(
            {},
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)


class NewRepositoryExampleTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, token, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.post(
            '/v2/repository/example/',
            json.dumps(data),
            content_type='application/json',
            **authorization_header)
        response = RepositoryExampleViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        text = 'hi'
        intent = 'greet'
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'intent': intent,
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('text'),
            text)
        self.assertEqual(
            content_data.get('intent'),
            intent)

    def test_okay_with_language(self):
        text = 'hi'
        intent = 'greet'
        language = languages.LANGUAGE_PT
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'language': language,
                'intent': intent,
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            content_data.get('text'),
            text)
        self.assertEqual(
            content_data.get('intent'),
            intent)
        repository_update_pk = content_data.get('repository_update')
        repository_update = RepositoryUpdate.objects.get(
            pk=repository_update_pk)
        self.assertEqual(repository_update.language, language)

    def test_forbidden(self):
        response, content_data = self.request(
            self.user_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_repository_uuid_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_repository_does_not_exists(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(uuid.uuid4()),
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'repository',
            content_data.keys())

    def test_invalid_repository_uuid(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': 'invalid',
                'text': 'hi',
                'intent': 'greet',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_with_entities(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_exists_example(self):
        text = 'hi'
        intent = 'greet'
        response_created, content_data_created = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'intent': intent,
                'entities': [],
            })

        self.assertEqual(
            response_created.status_code,
            status.HTTP_201_CREATED)

        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': text,
                'intent': intent,
                'entities': [],
            })

        self.assertEqual(
            content_data.get('non_field_errors')[0],
            'Intention and Sentence already exists'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_with_entities_with_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'subject',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)
        self.assertEqual(
            len(content_data.get('entities')),
            1)
        id = content_data.get('id')
        repository_example = RepositoryExample.objects.get(id=id)
        example_entity = repository_example.entities.all()[0]
        self.assertIsNotNone(example_entity.entity.label)

    def test_with_entities_with_invalid_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'other',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'entities',
            content_data.keys())
        entities_errors = content_data.get('entities')
        self.assertIn(
            'label',
            entities_errors[0])

    def test_with_entities_with_equal_label(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'greet',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'name',
                        'label': 'name',
                    },
                ],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'entities',
            content_data.keys())
        entities_errors = content_data.get('entities')
        self.assertIn(
            'label',
            entities_errors[0])

    def test_intent_or_entity_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'hi',
                'intent': '',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_entity_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': '',
                'entities': [
                    {
                        'start': 11,
                        'end': 18,
                        'entity': 'nam&',
                    },
                ],
            })
        print(content_data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('entities')),
            1)

    def test_intent_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                'repository': str(self.repository.uuid),
                'text': 'my name is douglas',
                'intent': 'nam$s',
                'entities': [],
            })
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('intent')),
            1)


class RequestAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, data, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.post(
            '/v2/repository/request-authorization/',
            data,
            **authorization_header)
        response = RequestAuthorizationViewSet.as_view(
            {'post': 'create'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'repository': self.repository.uuid,
            'text': 'I can contribute',
        }, self.token)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED)

    def test_forbidden_two_requests(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            text='I can contribute')
        response, content_data = self.request({
            'repository': self.repository.uuid,
            'text': 'I can contribute',
        }, self.token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            'non_field_errors',
            content_data.keys())


class ReviewAuthorizationRequestTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.admin, self.admin_token = create_user_and_token('admin')
        self.user, self.user_token = create_user_and_token()

        repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

        self.ra = RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=repository,
            text='I can contribute')

        admin_autho = repository.get_user_authorization(self.admin)
        admin_autho.role = RepositoryAuthorization.ROLE_ADMIN
        admin_autho.save()

    def request_approve(self, ra, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.put(
            '/v2/repository/review-authorization-request/{}/'.format(ra.pk),
            self.factory._encode_data({}, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header)
        response = ReviewAuthorizationRequestViewSet.as_view(
            {'put': 'update'})(request, pk=ra.pk)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def request_reject(self, ra, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.delete(
            '/v1/review-authorization-request/{}/'.format(ra.pk),
            **authorization_header)
        response = ReviewAuthorizationRequestViewSet.as_view(
            {'delete': 'destroy'})(request, pk=ra.pk)
        response.render()
        return response

    def test_approve_okay(self):
        response, content_data = self.request_approve(
            self.ra,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('approved_by'),
            self.owner.id)

    def test_admin_approve_okay(self):
        response, content_data = self.request_approve(
            self.ra,
            self.admin_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('approved_by'),
            self.admin.id)

    def test_approve_twice(self):
        self.ra.approved_by = self.owner
        self.ra.save()
        response, content_data = self.request_approve(
            self.ra,
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_approve_forbidden(self):
        response, content_data = self.request_approve(
            self.ra,
            self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_reject_okay(self):
        response = self.request_reject(self.ra, self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_admin_reject_okay(self):
        response = self.request_reject(self.ra, self.admin_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT)

    def test_reject_forbidden(self):
        response = self.request_reject(self.ra, self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class ListAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

        self.user_auth = self.repository.get_user_authorization(self.user)
        self.user_auth.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        self.user_auth.save()

    def request(self, repository, token):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.get(
            '/v2/repository/authorizations/',
            {
                'repository': repository.uuid,
            },
            **authorization_header)
        response = RepositoryAuthorizationViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)

        self.assertEqual(
            content_data.get('count'),
            1)

        self.assertEqual(
            content_data.get('results')[0].get('user'),
            self.user.id)

    def test_user_forbidden(self):
        response, content_data = self.request(
            self.repository,
            self.user_token)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class UpdateAuthorizationRoleTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

    def request(self, repository, token, user, data):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        }
        request = self.factory.patch(
            '/v2/repository/authorization-role/{}/{}/'.format(
                repository.uuid, user.nickname),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header)
        view = RepositoryAuthorizationRoleViewSet.as_view(
            {'patch': 'update'})
        response = view(
            request,
            repository__uuid=repository.uuid,
            user__nickname=user.nickname)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            self.user,
            {
                'role': RepositoryAuthorization.ROLE_CONTRIBUTOR,
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('role'),
            RepositoryAuthorization.ROLE_CONTRIBUTOR)

        user_authorization = self.repository.get_user_authorization(self.user)
        self.assertEqual(
            user_authorization.role,
            RepositoryAuthorization.ROLE_CONTRIBUTOR)

    def test_forbidden(self):
        response, content_data = self.request(
            self.repository,
            self.user_token,
            self.user,
            {
                'role': RepositoryAuthorization.ROLE_CONTRIBUTOR,
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)

    def test_owner_can_t_set_your_role(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            self.owner,
            {
                'role': RepositoryAuthorization.ROLE_CONTRIBUTOR,
            })

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)


class RepositoryAuthorizationRequestsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token('owner')
        self.admin, self.admin_token = create_user_and_token('admin')
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Testing',
            slug='test',
            language=languages.LANGUAGE_EN)

        RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            text='I can contribute')

        admin_autho = self.repository.get_user_authorization(self.admin)
        admin_autho.role = RepositoryAuthorization.ROLE_ADMIN
        admin_autho.save()

    def request(self, data, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}
        request = self.factory.get(
            '/v2/repository/authorization-requests/',
            data,
            **authorization_header)
        response = RepositoryAuthorizationRequestsViewSet.as_view(
            {'get': 'list'})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data,)

    def test_okay(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        }, self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_admin_okay(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        }, self.admin_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_repository_uuid_empty(self):
        response, content_data = self.request({}, self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            len(content_data.get('repository_uuid')),
            1)

    def test_forbidden(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        }, self.user_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN)
