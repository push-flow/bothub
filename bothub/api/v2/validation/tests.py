import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.common.models import Repository
from bothub.common.models import RepositoryValidation
from bothub.common.models import RepositoryTranslatedValidation
from bothub.common.models import RepositoryValidationEntity
from bothub.common import languages

from ..tests.utils import create_user_and_token
from .views import ValidationViewSet


class ListExamplesAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token('owner')
        self.user, self.user_token = create_user_and_token('user')

        self.repository = Repository.objects.create(
            owner=self.owner,
            name='Repository 1',
            slug='repo',
            language=languages.LANGUAGE_EN)
        self.example_1 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='hi',
            intent='greet')
        entity_1 = RepositoryValidationEntity.objects.create(
            repository_validation=self.example_1,
            start=0,
            end=0,
            entity='hi')
        entity_1.entity.set_label('greet')
        entity_1.entity.save()
        self.example_2 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='hello',
            intent='greet')
        self.example_3 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='bye',
            intent='farewell')
        self.example_4 = RepositoryValidation.objects.create(
            repository_update=self.repository.current_update(),
            text='bye bye',
            intent='farewell')

        self.repository_2 = Repository.objects.create(
            owner=self.owner,
            name='Repository 2',
            slug='repo2',
            language=languages.LANGUAGE_EN)
        self.example_5 = RepositoryValidation.objects.create(
            repository_update=self.repository_2.current_update(),
            text='hi',
            intent='greet')
        self.example_6 = RepositoryValidation.objects.create(
            repository_update=self.repository_2.current_update(
                languages.LANGUAGE_PT),
            text='oi',
            intent='greet')
        self.translation_6 = RepositoryTranslatedValidation.objects.create(
            original_validation=self.example_6,
            language=languages.LANGUAGE_EN,
            text='hi')

    def request(self, data={}, token=None):
        authorization_header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(token.key),
        } if token else {}

        request = self.factory.get(
            '/api/v2/validations/',
            data,
            **authorization_header)

        response = ValidationViewSet.as_view({'get': 'list'})(request)
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
            4)

        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

    def test_deleted(self):
        self.example_1.delete()
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            3)

    def test_without_repository_uuid(self):
        response, content_data = self.request()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST)

    def test_filter_text(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'text': self.example_1.text,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
        self.assertEqual(
            content_data.get('results')[0].get('id'),
            self.example_1.id)

    def test_filter_part_text(self):
        response, content_data = self.request({
            'repository_uuid': self.repository.uuid,
            'search': 'h',
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

    def test_filter_language(self):
        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'language': languages.LANGUAGE_PT
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_has_translation(self):
        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_translation': False
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_translation': True
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_has_not_translation_to(self):
        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_not_translation_to': languages.LANGUAGE_ES,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

        response, content_data = self.request({
            'repository_uuid': self.repository_2.uuid,
            'has_not_translation_to': languages.LANGUAGE_EN,
        })
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_order_by_translation(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository_2.uuid,
                'order_by_translation': languages.LANGUAGE_EN,
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        results = content_data.get('results')
        self.assertEqual(
            0,
            len(results[0].get('translations')))
        self.assertEqual(
            1,
            len(results[1].get('translations')))

    def test_filter_order_by_translation_inverted(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository_2.uuid,
                'order_by_translation': '-{}'.format(languages.LANGUAGE_EN),
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        results = content_data.get('results')
        self.assertEqual(
            1,
            len(results[0].get('translations')))
        self.assertEqual(
            0,
            len(results[1].get('translations')))

    def test_filter_intent(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'intent': 'farewell',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            2)

    def test_filter_label(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'label': 'greet',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)

    def test_filter_entity(self):
        response, content_data = self.request(
            {
                'repository_uuid': self.repository.uuid,
                'entity': 'hi',
            },
            self.owner_token)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK)
        self.assertEqual(
            content_data.get('count'),
            1)
