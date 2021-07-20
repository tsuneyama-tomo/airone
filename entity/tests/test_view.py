import json
import yaml

from django.contrib.auth.models import Permission
from django.urls import reverse

from airone.lib.test import AironeViewTest
from airone.lib.types import AttrTypeStr, AttrTypeObj, AttrTypeText
from airone.lib.types import AttrTypeArrStr, AttrTypeArrObj
from airone.lib.types import AttrTypeValue

from entity.models import Entity, EntityAttr
from entity.settings import CONFIG
from entry.models import Entry, Attribute
from user.models import User, History
from unittest import mock
from entity import tasks


class ViewTest(AironeViewTest):
    """
    This has simple tests that check basic functionality
    """
    def setUp(self):
        super(ViewTest, self).setUp()

        # clear data which is used in individual tests
        self._test_data = {}

    def test_index_without_login(self):
        resp = self.client.get(reverse('entity:index'))
        self.assertEqual(resp.status_code, 303)

    def test_index(self):
        self.admin_login()

        resp = self.client.get(reverse('entity:index'))
        self.assertEqual(resp.status_code, 200)

    def test_index_with_objects(self):
        user = self.admin_login()

        entity = Entity(name='test-entity', created_user=user)
        entity.save()

        resp = self.client.get(reverse('entity:index'))
        self.assertEqual(resp.status_code, 200)

    @mock.patch('entity.views.CONFIG.MAX_LIST_ENTITIES', 3)
    def test_index_with_page_param(self):
        user = self.guest_login()

        # create test entities
        [Entity.objects.create(name='e-%d' % i, created_user=user) for i in range(5)]

        # send a request to get entities with page parameter and check returned context
        resp = self.client.get('/entity/?page=1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['entity_count'], 2)
        self.assertEqual(resp.context['total_count'], 5)
        self.assertEqual(resp.context['page_index_start'], 3)
        self.assertEqual(resp.context['page_index_end'], 5)

    def test_index_with_keyword_param(self):
        user = self.guest_login()

        # create test entities
        [foo, _] = [Entity.objects.create(name=x, created_user=user) for x in ['FOO', 'BAR']]

        # send a request to get entities with keyword parameter and check returned context
        resp = self.client.get('/entity/?keyword=foo')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['entities'].first(), foo)
        self.assertEqual(resp.context['entity_count'], 1)
        self.assertEqual(resp.context['total_count'], 1)
        self.assertEqual(resp.context['page_index_start'], 0)
        self.assertEqual(resp.context['page_index_end'], 1)

    def test_create_get(self):
        user = User.objects.create(username='admin', is_superuser=True)

        entity_public = Entity.objects.create(name='public', created_user=user)
        Entity.objects.create(name='private', created_user=user, is_public=False)

        self.guest_login()

        resp = self.client.get(reverse('entity:create'))
        self.assertEqual(resp.status_code, 200)

        # checks that prohibited entity for logined-user to show isn't be returned
        self.assertEqual(len(resp.context['entities']), 1)
        self.assertEqual(resp.context['entities'][0].id, entity_public.id)

    @mock.patch('entity.tasks.create_entity.delay', mock.Mock(side_effect=tasks.create_entity))
    def test_create_post_without_login(self):
        resp = self.client.post(reverse('entity:do_create'), json.dumps({}), 'application/json')
        self.assertEqual(resp.status_code, 401)

    @mock.patch('entity.tasks.create_entity.delay', mock.Mock(side_effect=tasks.create_entity))
    def test_create_post(self):
        self.admin_login()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': True,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '1'},
                {'name': 'bar', 'type': str(AttrTypeText), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '2'},
                {'name': 'baz', 'type': str(AttrTypeArrStr), 'is_delete_in_chain': False,
                 'is_mandatory': False, 'row_index': '3'},
                {'name': 'attr_bool', 'type': str(AttrTypeValue['boolean']),
                 'is_delete_in_chain': False, 'is_mandatory': False, 'row_index': '4'},
                {'name': 'attr_group', 'type': str(AttrTypeValue['group']),
                 'is_delete_in_chain': False, 'is_mandatory': False, 'row_index': '5'},
                {'name': 'attr_date', 'type': str(AttrTypeValue['date']),
                 'is_delete_in_chain': False, 'is_mandatory': False, 'row_index': '6'},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)

        # tests for Entity object
        entity = Entity.objects.first()
        self.assertEqual(entity.name, 'hoge')
        self.assertTrue(entity.status & Entity.STATUS_TOP_LEVEL)

        # tests for EntityAttribute objects
        self.assertEqual(len(EntityAttr.objects.all()), 6)

        # tests for operation history is registered correctly
        self.assertEqual(History.objects.count(), 7)
        self.assertEqual(History.objects.filter(operation=History.ADD_ENTITY).count(), 1)
        self.assertEqual(History.objects.filter(operation=History.ADD_ATTR).count(), 6)

    def test_create_post_without_name_param(self):
        self.admin_login()

        params = {
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '1'},
                {'name': 'bar', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': False, 'row_index': '2'},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertIsNone(Entity.objects.first())

    def test_create_post_with_invalid_attrs(self):
        self.admin_login()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': [
                {'name': '', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '1'},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 400)

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': 'abcd'},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertIsNone(Entity.objects.first())

    def test_create_port_with_invalid_params(self):
        self.admin_login()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': 'puyo',
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertIsNone(Entity.objects.first())

    def test_get_edit_without_login(self):
        resp = self.client.get(reverse('entity:edit', args=[0]))
        self.assertEqual(resp.status_code, 303)

    def test_get_edit_with_invalid_entity_id(self):
        self.admin_login()

        resp = self.client.get(reverse('entity:edit', args=[999]))
        self.assertEqual(resp.status_code, 400)

    def test_get_edit_with_valid_entity_id(self):
        user = self.admin_login()
        entity = Entity.objects.create(name='hoge', created_user=user)

        resp = self.client.get(reverse('entity:edit', args=[entity.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['entity'], entity)

    def test_post_edit_without_login(self):
        resp = self.client.post(reverse('entity:do_edit', args=[0]), '{}', 'application/json')
        self.assertEqual(resp.status_code, 401)

    def test_post_edit_with_invalid_params(self):
        self.admin_login()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '1'},
            ],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[999]),
                                json.dumps(params),
                                'application/json')
        self.assertEqual(resp.status_code, 400)

    @mock.patch('entity.tasks.edit_entity.delay', mock.Mock(side_effect=tasks.edit_entity))
    def test_post_edit_with_valid_params(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        attr = EntityAttr.objects.create(name='puyo',
                                         created_user=user,
                                         is_mandatory=True,
                                         type=AttrTypeStr,
                                         parent_entity=entity)
        entity.attrs.add(attr)

        params = {
            'name': 'foo',
            'note': 'bar',
            'is_toplevel': True,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': False, 'id': attr.id, 'row_index': '1'},
                {'name': 'bar', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '2'},
            ],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Entity.objects.get(id=entity.id).name, 'foo')
        self.assertEqual(Entity.objects.get(id=entity.id).note, 'bar')
        self.assertEqual(Entity.objects.get(id=entity.id).attrs.count(), 2)
        self.assertEqual(Entity.objects.get(id=entity.id).attrs.get(id=attr.id).name, 'foo')
        self.assertEqual(Entity.objects.get(id=entity.id).attrs.last().name, 'bar')
        self.assertTrue(Entity.objects.get(id=entity.id).status & Entity.STATUS_TOP_LEVEL)

        # tests for operation history is registered correctly
        self.assertEqual(History.objects.count(), 5)
        self.assertEqual(History.objects.filter(operation=History.MOD_ENTITY).count(), 2)
        self.assertEqual(History.objects.filter(operation=History.ADD_ATTR).count(), 1)
        self.assertEqual(History.objects.filter(operation=History.MOD_ATTR).count(), 2)

    @mock.patch('entity.tasks.edit_entity.delay', mock.Mock(side_effect=tasks.edit_entity))
    def test_post_edit_after_creating_entry(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        attrbase = EntityAttr.objects.create(name='puyo',
                                             created_user=user,
                                             is_mandatory=True,
                                             type=AttrTypeStr,
                                             parent_entity=entity)
        entity.attrs.add(attrbase)

        entry = Entry.objects.create(name='entry', schema=entity, created_user=user)
        entry.add_attribute_from_base(attrbase, user)

        params = {
            'name': 'foo',
            'note': 'bar',
            'is_toplevel': False,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'id': attrbase.id, 'row_index': '1'},
                {'name': 'bar', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '2'},
            ],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(entity.attrs.count(), 2)
        self.assertEqual(entry.attrs.count(), 1)

    def test_post_edit_attribute_type(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        attr = EntityAttr.objects.create(name='puyo',
                                         type=AttrTypeStr,
                                         created_user=user,
                                         parent_entity=entity)
        entity.attrs.add(attr)

        params = {
            'name': 'foo',
            'note': 'bar',
            'is_toplevel': False,
            'attrs': [{
                'name': 'baz',
                'type': str(AttrTypeObj),
                'ref_ids': [entity.id],
                'is_mandatory': True,
                'is_delete_in_chain': False,
                'row_index': '1',
                'id': attr.id
            }],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(EntityAttr.objects.get(id=attr.id).type, AttrTypeStr)
        self.assertEqual(EntityAttr.objects.get(id=attr.id).referral.count(), 0)

    @mock.patch('entity.tasks.edit_entity.delay', mock.Mock(side_effect=tasks.edit_entity))
    def test_post_edit_attribute_referral(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        attrbase = EntityAttr.objects.create(name='puyo',
                                             type=AttrTypeObj,
                                             created_user=user,
                                             parent_entity=entity)
        entity.attrs.add(attrbase)

        entry = Entry.objects.create(name='entry', schema=entity, created_user=user)
        attr = entry.add_attribute_from_base(attrbase, user)

        params = {
            'name': 'foo',
            'note': 'bar',
            'is_toplevel': False,
            'attrs': [{
                'name': 'baz',
                'type': str(AttrTypeStr),
                'ref_ids': [entity.id],
                'is_mandatory': True,
                'is_delete_in_chain': True,
                'row_index': '1',
                'id': attrbase.id
            }],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)

        # This checks attribute type is not changed to specified Type, but
        # attribute referrals are changed to specified one in the request.
        self.assertEqual(EntityAttr.objects.get(id=attrbase.id).type, AttrTypeObj)
        self.assertEqual([x.id for x in EntityAttr.objects.get(id=attrbase.id).referral.all()],
                         [entity.id])

        # checks that the related Attribute is also changed
        self.assertEqual(Attribute.objects.get(id=attr.id).schema, attrbase)
        self.assertEqual(Attribute.objects.get(id=attr.id).schema.name, 'baz')
        self.assertEqual(Attribute.objects.get(id=attr.id).schema.type, AttrTypeObj)
        self.assertTrue(Attribute.objects.get(id=attr.id).schema.is_mandatory)
        self.assertTrue(Attribute.objects.get(id=attr.id).schema.is_delete_in_chain)
        self.assertEqual([x.id for x in Attribute.objects.get(id=attr.id).schema.referral.all()],
                         [entity.id])

    def test_post_edit_to_array_referral_attribute(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        attr = EntityAttr.objects.create(name='puyo',
                                         type=AttrTypeStr,
                                         created_user=user,
                                         parent_entity=entity)
        entity.attrs.add(attr)

        params = {
            'name': 'foo',
            'note': 'bar',
            'is_toplevel': False,
            'attrs': [{
                'name': 'baz',
                'type': str(AttrTypeArrObj),
                'ref_ids': [entity.id],
                'is_mandatory': True,
                'is_delete_in_chain': False,
                'row_index': '1',
                'id': attr.id
            }],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(EntityAttr.objects.get(id=attr.id).type, AttrTypeStr)
        self.assertEqual(EntityAttr.objects.get(id=attr.id).referral.count(), 0)

    @mock.patch('entity.tasks.edit_entity.delay', mock.Mock())
    def test_post_edit_under_processing(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        attr = EntityAttr.objects.create(name='puyo',
                                         created_user=user,
                                         is_mandatory=True,
                                         type=AttrTypeStr,
                                         parent_entity=entity)
        entity.attrs.add(attr)

        params = {
            'name': 'foo',
            'note': 'bar',
            'is_toplevel': True,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': False, 'id': attr.id, 'row_index': '1'},
                {'name': 'bar', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '2'},
            ],
        }

        # Call a new editing entity
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')
        self.assertEqual(resp.status_code, 200)

        # Call the entity still processing again
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')
        self.assertEqual(resp.status_code, 400)

    def test_post_create_with_invalid_referral_attr(self):
        self.admin_login()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': [
                {'name': 'a', 'type': str(AttrTypeObj), 'is_delete_in_chain': False,
                 'is_mandatory': False, 'row_index': '1'},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 400)

    @mock.patch('entity.tasks.create_entity.delay', mock.Mock(side_effect=tasks.create_entity))
    def test_post_create_with_valid_referral_attr(self):
        user = self.admin_login()

        entity = Entity(name='test-entity', created_user=user)
        entity.save()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': False,
            'attrs': [
                {'name': 'a', 'type': str(AttrTypeObj), 'ref_ids': [entity.id],
                 'is_delete_in_chain': True, 'is_mandatory': False, 'row_index': '1'},
                {'name': 'b', 'type': str(AttrTypeArrObj), 'ref_ids': [entity.id],
                 'is_delete_in_chain': True, 'is_mandatory': False, 'row_index': '2'},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)

        created_entity = Entity.objects.get(name='hoge')
        self.assertEqual(created_entity.attrs.count(), 2)
        self.assertEqual([x.name for x in created_entity.attrs.all()], ['a', 'b'])
        self.assertFalse(any([x.is_mandatory for x in created_entity.attrs.all()]))
        self.assertTrue(all([x.is_delete_in_chain for x in created_entity.attrs.all()]))

    @mock.patch('entity.tasks.edit_entity.delay', mock.Mock(side_effect=tasks.edit_entity))
    def test_post_delete_attribute(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='entity', created_user=user)
        for name in ['foo', 'bar']:
            entity.attrs.add(EntityAttr.objects.create(name=name,
                                                       type=AttrTypeStr,
                                                       created_user=user,
                                                       parent_entity=entity))

        entry = Entry.objects.create(name='entry', schema=entity, created_user=user)
        [entry.add_attribute_from_base(x, user) for x in entity.attrs.all()]

        permission_count = Permission.objects.count()
        params = {
            'name': 'new-entity',
            'note': 'hoge',
            'is_toplevel': False,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'id': entity.attrs.first().id,
                 'is_delete_in_chain': True, 'is_mandatory': False, 'row_index': '1'},
                {'name': 'bar', 'type': str(AttrTypeStr), 'id': entity.attrs.last().id,
                 'is_delete_in_chain': True, 'is_mandatory': False, 'deleted': True,
                 'row_index': '2'},
            ],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 200)

        # Note: delete() method won't actual delete only set delete flag
        self.assertEqual(Permission.objects.count(), permission_count)
        self.assertEqual(entity.attrs.count(), 2)
        self.assertEqual(entry.attrs.count(), 2)

        # tests for operation history is registered correctly
        self.assertEqual(History.objects.count(), 3)
        self.assertEqual(History.objects.filter(operation=History.MOD_ENTITY).count(), 2)
        self.assertEqual(History.objects.filter(operation=History.DEL_ATTR).count(), 1)

    def test_export_data(self):
        user = self.admin_login()

        entity1 = Entity.objects.create(name='entity1', note='hoge', created_user=user)
        for name in ['foo', 'bar']:
            entity1.attrs.add(EntityAttr.objects.create(name=name,
                                                        type=AttrTypeStr,
                                                        created_user=user,
                                                        parent_entity=entity1))

        entity2 = Entity.objects.create(name='entity2', created_user=user)
        attr = EntityAttr.objects.create(name='attr',
                                         type=AttrTypeObj,
                                         created_user=user,
                                         parent_entity=entity2)
        attr.referral.add(entity1)
        entity2.attrs.add(attr)
        entity2.save()

        resp = self.client.get(reverse('entity:export'))
        self.assertEqual(resp.status_code, 200)

        obj = yaml.load(resp.content, Loader=yaml.SafeLoader)
        self.assertTrue(isinstance(obj, dict))
        self.assertEqual(sorted(obj.keys()), ['Entity', 'EntityAttr'])
        self.assertEqual(len(obj['EntityAttr']), 3)
        self.assertEqual(len(obj['Entity']), 2)

        self.assertTrue(list(filter(lambda x: (
                x['name'] == 'foo' and
                x['entity'] == 'entity1' and
                x['type'] == AttrTypeStr and
                x['refer'] == ''
            ), obj['EntityAttr'])))
        self.assertTrue(list(filter(lambda x: (
                x['name'] == 'attr' and
                x['entity'] == 'entity2' and
                x['type'] == AttrTypeObj and
                x['refer'] == 'entity1'
            ), obj['EntityAttr'])))
        self.assertTrue(list(filter(lambda x: (
                x['name'] == 'entity1' and
                x['note'] == 'hoge' and
                x['created_user'] == 'admin'
            ), obj['Entity'])))

    def test_export_with_unpermitted_object(self):
        user = self.guest_login()
        user2 = User.objects.create(username='user2')

        # create an entity object which is created by logined-user
        entity1 = Entity.objects.create(name='entity1', created_user=user)
        entity1.attrs.add(EntityAttr.objects.create(name='attr1',
                                                    type=AttrTypeStr,
                                                    created_user=user,
                                                    parent_entity=entity1))

        # create a public object which is created by the another_user
        entity2 = Entity.objects.create(name='entity2', created_user=user2)
        entity2.attrs.add(EntityAttr.objects.create(name='attr2',
                                                    type=AttrTypeStr,
                                                    created_user=user2,
                                                    parent_entity=entity1))

        # create private objects which is created by the another_user
        for name in ['foo', 'bar']:
            e = Entity.objects.create(name=name, created_user=user2, is_public=False)
            e.attrs.add(EntityAttr.objects.create(name='private_attr',
                                                  type=AttrTypeStr,
                                                  created_user=user2,
                                                  parent_entity=e,
                                                  is_public=False))

        resp = self.client.get(reverse('entity:export'))
        self.assertEqual(resp.status_code, 200)

        obj = yaml.load(resp.content, Loader=yaml.SafeLoader)
        self.assertEqual(len(obj['Entity']), 2)
        self.assertEqual(len(obj['EntityAttr']), 2)
        self.assertTrue([x for x in obj['Entity'] if x['name'] == entity1.name])
        self.assertTrue([x for x in obj['Entity'] if x['name'] == entity2.name])
        self.assertFalse([x for x in obj['EntityAttr'] if x['name'] == 'private_attr'])

    def test_export_with_deleted_object(self):
        user = self.admin_login()

        entity1 = Entity.objects.create(name='entity1', created_user=user)
        entity1.attrs.add(EntityAttr.objects.create(name='attr1',
                                                    type=AttrTypeStr,
                                                    created_user=user,
                                                    parent_entity=entity1))

        # This Entity object won't be exported because this is logically deleted
        entity1 = Entity.objects.create(name='entity2', created_user=user, is_active=False)

        resp = self.client.get(reverse('entity:export'))
        self.assertEqual(resp.status_code, 200)

        obj = yaml.load(resp.content, Loader=yaml.SafeLoader)
        self.assertEqual(len(obj['Entity']), 1)
        self.assertEqual(obj['Entity'][0]['name'], 'entity1')

    @mock.patch('entity.tasks.delete_entity.delay', mock.Mock(side_effect=tasks.delete_entity))
    def test_post_delete(self):
        user1 = self.admin_login()

        entity1 = Entity.objects.create(name='entity1', created_user=user1)
        entity1.save()

        attr = EntityAttr.objects.create(name='attr-test',
                                         created_user=user1,
                                         is_mandatory=True,
                                         type=AttrTypeStr,
                                         parent_entity=entity1)
        entity1.attrs.add(attr)

        entity_count = Entity.objects.all().count()

        params = {}
        resp = self.client.post(reverse('entity:do_delete', args=[entity1.id]),
                                json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Entity.objects.all().count(), entity_count,
                         "Entity should not be deleted from database")

        entity1 = Entity.objects.get(name__icontains='entity1_deleted_')
        self.assertFalse(entity1.is_active)
        for attr in entity1.attrs.all():
            self.assertFalse(attr.is_active)

    def test_post_delete_without_permission(self):
        self.guest_login()
        user2 = User.objects.create(username='mokeke')

        entity1 = Entity.objects.create(name='entity1', created_user=user2)
        entity1.is_public = False
        entity1.save()

        entity_count = Entity.objects.all().count()

        params = {}
        resp = self.client.post(reverse('entity:do_delete', args=[entity1.id]),
                                json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Entity.objects.all().count(), entity_count,
                         "Entity should not be deleted from database")

        entity1 = Entity.objects.get(name='entity1')
        self.assertIsNotNone(entity1)
        self.assertTrue(entity1.is_active)

    def test_post_delete_with_active_entry(self):
        user = self.admin_login()

        entity = Entity.objects.create(name='entity1', created_user=user)

        attrbase = EntityAttr.objects.create(name='puyo',
                                             created_user=user,
                                             is_mandatory=True,
                                             type=AttrTypeStr,
                                             parent_entity=entity)
        entity.attrs.add(attrbase)

        entry = Entry.objects.create(name='entry1', schema=entity, created_user=user)
        entry.add_attribute_from_base(attrbase, user)
        entry.save()

        entity_count = Entity.objects.all().count()

        params = {}
        resp = self.client.post(reverse('entity:do_delete', args=[entity.id]),
                                json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Entity.objects.all().count(), entity_count,
                         "Entity should not be deleted from database")

        entity = Entity.objects.get(name='entity1')
        self.assertIsNotNone(entity)
        self.assertTrue(entity.is_active)
        self.assertTrue(EntityAttr.objects.get(name='puyo').is_active)

    @mock.patch('entity.tasks.delete_entity.delay', mock.Mock())
    def test_post_delete_under_processing(self):
        user1 = self.admin_login()

        entity1 = Entity.objects.create(name='entity1', created_user=user1)
        entity1.save()

        attr = EntityAttr.objects.create(name='attr-test',
                                         created_user=user1,
                                         is_mandatory=True,
                                         type=AttrTypeStr,
                                         parent_entity=entity1)
        entity1.attrs.add(attr)

        params = {}

        # Call a new deleting entity
        resp = self.client.post(reverse('entity:do_delete', args=[entity1.id]),
                                json.dumps(params), 'application/json')
        self.assertEqual(resp.status_code, 200)

        # Call the entity still processing again
        resp = self.client.post(reverse('entity:do_delete', args=[entity1.id]),
                                json.dumps(params), 'application/json')
        self.assertEqual(resp.status_code, 400)

    def test_post_create_entity_with_guest(self):
        self.guest_login()

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': True,
            'attrs': [],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Entity.objects.filter(name='hoge'))

    @mock.patch('entity.tasks.create_entity.delay', mock.Mock(side_effect=tasks.create_entity))
    def test_create_entity_attr_with_multiple_referral(self):
        user = self.admin_login()

        r_entity1 = Entity.objects.create(name='referred_entity1', created_user=user)
        r_entity2 = Entity.objects.create(name='referred_entity2', created_user=user)

        params = {
            'name': 'entity',
            'note': 'note',
            'is_toplevel': False,
            'attrs': [
                {
                    'name': 'attr',
                    'type': str(AttrTypeObj),
                    'ref_ids': [r_entity1.id, r_entity2.id],
                    'is_mandatory': False,
                    'is_delete_in_chain': False,
                    'row_index': '1'
                },
            ],
        }
        resp = self.client.post(reverse('entity:do_create'),
                                json.dumps(params),
                                'application/json')

        self.assertEqual(resp.status_code, 200)

        entity = Entity.objects.get(name='entity')

        self.assertEqual(entity.attrs.count(), 1)
        self.assertEqual(entity.attrs.last().referral.count(), 2)
        self.assertEqual(entity.attrs.last().referral.filter(id=r_entity1.id).count(), 1)
        self.assertEqual(entity.attrs.last().referral.filter(id=r_entity2.id).count(), 1)

    def test_not_to_be_changed_attribute_type(self):
        user = self.admin_login()

        ref_entity = Entity.objects.create(name='ref_entity', created_user=user)

        entity = Entity.objects.create(name='entity', created_user=user)
        for name in ['foo', 'bar']:
            attr = EntityAttr.objects.create(name=name,
                                             type=AttrTypeStr,
                                             created_user=user,
                                             parent_entity=entity)
            entity.attrs.add(attr)

        (attr1, attr2) = entity.attrs.all()

        entry = Entry.objects.create(name='entry', schema=entity, created_user=user)
        entry.complement_attrs(user)

        entry.attrs.get(schema=attr1).add_value(user, 'hoge')
        entry.attrs.get(schema=attr2).add_value(user, 'fuga')

        # This request try to change type of EntityAttr by specifying 'type' parameter in this
        # request. But EntityAttr's type would never been changed once it had been created.
        params = {
            'name': 'new-entity',
            'note': 'hoge',
            'is_toplevel': False,
            'attrs': [
                # change attribute name and mandatory parameter
                {'name': 'new', 'type': str(attr1.type), 'id': attr1.id,
                 'is_delete_in_chain': True, 'is_mandatory': not attr1.is_mandatory,
                 'row_index': '1'},
                # change only attribute type
                {'name': attr2.name, 'type': str(AttrTypeValue['object']), 'id': attr2.id,
                 'is_delete_in_chain': True, 'is_mandatory': attr2.is_mandatory, 'row_index': '2',
                 'ref_ids': [ref_entity.id]}
            ]
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity.id]),
                                json.dumps(params),
                                'application/json')
        self.assertEqual(resp.status_code, 200)

        # When name and mandatory parameters are changed, the attribute value will not be changed.
        attrv = entry.attrs.get(schema=attr1).get_latest_value()
        self.assertIsNotNone(attrv)
        self.assertEqual(attrv.value, 'hoge')

        # This checks data type of EntityAttr and AttributeValue wouldn't be changed.
        attrv = entry.attrs.get(schema=attr2).get_latest_value()
        self.assertEqual(attrv.value, 'fuga')
        self.assertEqual(attrv.data_type, AttrTypeValue['string'])
        self.assertEqual(EntityAttr.objects.get(name=attr2.name).type, AttrTypeValue['string'])

    def test_show_dashboard(self):
        user = self.admin_login()
        entity = Entity.objects.create(name='entity', created_user=user)

        # send request with invalid entity id
        resp = self.client.get(reverse('entity:dashboard', args=[999]))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('entity:dashboard', args=[entity.id]))
        self.assertEqual(resp.status_code, 200)

        # To test dashboard view with correct settings,
        # make entities/entries associated with "entity"
        ref_entity = Entity.objects.create(name='ref_entity', created_user=user)
        ref_entries = [
            Entry.objects.create(
                name='ref_entry-%d' % i, schema=ref_entity, created_user=user
            ) for i in range(0, CONFIG.DASHBOARD_NUM_ITEMS + 3)
        ]

        attr = EntityAttr.objects.create(name='attr', created_user=user, is_summarized=True,
                                         parent_entity=entity, type=AttrTypeValue['object'])
        attr.referral.add(ref_entity)
        entity.attrs.add(attr)

        # create entries
        for i in range(0, CONFIG.DASHBOARD_NUM_ITEMS + 2):
            entry = Entry.objects.create(name='entry-%d' % i, schema=entity, created_user=user)
            entry.complement_attrs(user)

            if i < CONFIG.DASHBOARD_NUM_ITEMS + 1:
                entry.attrs.get(name='attr').add_value(user, ref_entries[i])

        resp = self.client.get(reverse('entity:dashboard', args=[entity.id]))
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['entity'].id, entity.id)
        self.assertEqual(resp.context['total_entry_count'],
                         Entry.objects.filter(schema=entity, is_active=True).count())

        # checks that referral information is set correctly
        for (ret_attr, ret_info) in resp.context['summarized_data'].items():
            self.assertEqual(ret_attr.id, attr.id)
            self.assertEqual(len(ret_info['referral_count']), CONFIG.DASHBOARD_NUM_ITEMS + 1)
            self.assertEqual(ret_info['no_referral_count'], 1)
            self.assertEqual(ret_info['no_referral_ratio'],
                             '%2.1f' % (100 / resp.context['total_entry_count']))
            self.assertTrue(any([x['referral'] == '(Others)' and x['count'] == 1
                            for x in ret_info['referral_count']]))

        # checks statistics information would show correcting value, even if an entry was deleted.
        for i in range(0, 2):
            Entry.objects.get(name='entry-%d' % i, schema=entity).delete()

        # delete no referral entry
        Entry.objects.get(name='entry-%d' % (CONFIG.DASHBOARD_NUM_ITEMS + 1),
                          schema=entity).delete()

        resp = self.client.get(reverse('entity:dashboard', args=[entity.id]))
        self.assertEqual(resp.status_code, 200)

        for (ret_attr, ret_info) in resp.context['summarized_data'].items():
            self.assertEqual(len(ret_info['referral_count']), CONFIG.DASHBOARD_NUM_ITEMS - 1)
            self.assertEqual(ret_info['no_referral_count'], 0)

            for no_referral in ['ref_entry-%d' % i for i in range(0, 2)]:
                self.assertFalse(
                    any([x['referral'] == no_referral for x in ret_info['referral_count']]))

    def test_show_dashboard_config(self):
        user = self.admin_login()
        entity = Entity.objects.create(name='entity', created_user=user)

        # send request with invalid entity id
        resp = self.client.get(reverse('entity:conf_dashboard', args=[999]))
        self.assertEqual(resp.status_code, 400)

        resp = self.client.get(reverse('entity:conf_dashboard', args=[entity.id]))
        self.assertEqual(resp.status_code, 200)

    def test_post_dashboard_config(self):
        user = self.admin_login()

        # send request with invalid entity id
        resp = self.client.post(reverse('entity:do_conf_dashboard', args=[999]))
        self.assertEqual(resp.status_code, 400)

        entity = Entity.objects.create(name='entity', created_user=user)
        attr = EntityAttr.objects.create(name='attr', created_user=user, parent_entity=entity)
        entity.attrs.add(attr)

        # send post request with parameters which contain an invalid EntityAttr-ID
        resp = self.client.post(reverse('entity:do_conf_dashboard', args=[entity.id]),
                                json.dumps({'attrs': [str(attr.id), '9999']}), 'application/json')
        self.assertEqual(resp.status_code, 400)

        # send post request with valid parameter
        resp = self.client.post(reverse('entity:do_conf_dashboard', args=[entity.id]),
                                json.dumps({'attrs': [str(attr.id)]}), 'application/json')
        self.assertEqual(resp.status_code, 200)

        summarized_attr = EntityAttr.objects.get(parent_entity=entity, is_summarized=True)
        self.assertEqual(summarized_attr.id, attr.id)

        # send post request to clear summarized flag
        resp = self.client.post(reverse('entity:do_conf_dashboard', args=[entity.id]),
                                json.dumps({'attrs': []}), 'application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(EntityAttr.objects.filter(parent_entity=entity,
                                                   is_summarized=True).count(), 0)

    @mock.patch('custom_view.is_custom', mock.Mock(return_value=True))
    @mock.patch('custom_view.call_custom')
    def test_create_entity_with_customview(self, mock_call_custom):
        self.guest_login()

        def side_effect(handler_name, entity_name, entity_attrs):
            self._test_data['is_call_custom_called'] = True

            # Check specified parameters are expected
            self.assertEqual(handler_name, 'create_entity')
            self.assertEqual(entity_name, params['name'])
            self.assertEqual(entity_attrs, params['attrs'])

        mock_call_custom.side_effect = side_effect

        params = {
            'name': 'hoge',
            'note': 'fuga',
            'is_toplevel': True,
            'attrs': [
                {'name': 'foo', 'type': str(AttrTypeStr), 'is_delete_in_chain': False,
                 'is_mandatory': True, 'row_index': '1', 'ref_ids': []},
            ],
        }
        resp = self.client.post(reverse('entity:do_create'), json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self._test_data['is_call_custom_called'])

    @mock.patch('custom_view.is_custom', mock.Mock(return_value=True))
    @mock.patch('custom_view.call_custom')
    def test_edit_entity_with_customview(self, mock_call_custom):
        user = self.guest_login()

        def side_effect(handler_name, entity, entity_name, entity_attrs):
            self._test_data['is_call_custom_called'] = True

            # Check specified parameters are expected
            self.assertEqual(handler_name, 'edit_entity')
            self.assertEqual(entity, entity_test)
            self.assertEqual(entity_name, params['name'])
            self.assertEqual(entity_attrs, params['attrs'])

        mock_call_custom.side_effect = side_effect

        entity_test = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        params = {
            'name': 'hoge-changed',
            'note': 'fuga',
            'is_toplevel': True,
            'attrs': [],
        }
        resp = self.client.post(reverse('entity:do_edit', args=[entity_test.id]),
                                json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self._test_data['is_call_custom_called'])

    @mock.patch('custom_view.is_custom', mock.Mock(return_value=True))
    @mock.patch('custom_view.call_custom')
    def test_delete_entity_with_customview(self, mock_call_custom):
        user = self.guest_login()

        def side_effect(handler_name, entity):
            self._test_data['is_call_custom_called'] = True

            # Check specified parameters are expected
            self.assertEqual(handler_name, 'delete_entity')
            self.assertEqual(entity, entity_test)

        mock_call_custom.side_effect = side_effect

        entity_test = Entity.objects.create(name='hoge', note='fuga', created_user=user)
        params = {
            'name': 'hoge-changed',
            'note': 'fuga',
            'is_toplevel': True,
            'attrs': [],
        }
        resp = self.client.post(reverse('entity:do_delete', args=[entity_test.id]),
                                json.dumps(params), 'application/json')

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self._test_data['is_call_custom_called'])
