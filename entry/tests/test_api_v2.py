from unittest import mock
import json
import datetime

from airone.lib.test import AironeViewTest
from airone.lib.types import AttrTypeValue, AttrTypeStr
from entity.models import Entity, EntityAttr
from entry import tasks
from entry.models import Entry
from group.models import Group
from user.models import User


class ViewTest(AironeViewTest):
    def setUp(self):
        super(ViewTest, self).setUp()

        self.user: User = self.guest_login()

        # create Entities, Entries and Group for using this test case
        self.ref_entity: Entity = self.create_entity(self.user, "ref_entity")
        self.ref_entry: Entry = self.add_entry(self.user, "r-0", self.ref_entity)
        self.group: Group = Group.objects.create(name="group0")

        self.entity: Entity = self.create_entity(
            **{
                "user": self.user,
                "name": "test-entity",
                "attrs": self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY,
            }
        )

    def test_retrieve_entry(self):
        entry: Entry = self.add_entry(
            self.user,
            "Entry",
            self.entity,
            values={
                "val": "hoge",
                "ref": self.ref_entry.id,
                "name": {"name": "hoge", "id": self.ref_entry.id},
                "bool": False,
                "date": "2018-12-31",
                "group": self.group.id,
                "groups": [self.group.id],
                "text": "fuga",
                "vals": ["foo", "bar"],
                "refs": [self.ref_entry.id],
                "names": [
                    {"name": "foo", "id": self.ref_entry.id},
                    {"name": "bar", "id": self.ref_entry.id},
                ],
            },
        )
        # add an optional attribute after creating entry
        optional_attr = EntityAttr.objects.create(
            **{
                "name": "opt",
                "type": AttrTypeValue["string"],
                "is_mandatory": False,
                "parent_entity": self.entity,
                "created_user": self.user,
            }
        )
        self.entity.attrs.add(optional_attr)

        resp = self.client.get("/entry/api/v2/%d/" % entry.id)
        self.assertEqual(resp.status_code, 200)

        resp_data = resp.json()
        self.assertEqual(resp_data["id"], entry.id)
        self.assertEqual(resp_data["name"], entry.name)
        self.assertEqual(resp_data["schema"], {"id": entry.schema.id, "name": entry.schema.name})

        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "val", resp_data["attrs"])),
            {
                "type": AttrTypeValue["string"],
                "value": "hoge",
                "id": entry.attrs.get(schema__name="val").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="val").schema.id,
                    "name": "val",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "ref", resp_data["attrs"])),
            {
                "type": AttrTypeValue["object"],
                "value": {
                    "id": self.ref_entry.id,
                    "name": self.ref_entry.name,
                    "schema": {
                        "id": self.ref_entry.schema.id,
                        "name": self.ref_entry.schema.name,
                    },
                },
                "id": entry.attrs.get(schema__name="ref").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="ref").schema.id,
                    "name": "ref",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "name", resp_data["attrs"])),
            {
                "type": AttrTypeValue["named_object"],
                "value": {
                    "hoge": {
                        "id": self.ref_entry.id,
                        "name": self.ref_entry.name,
                        "schema": {
                            "id": self.ref_entry.schema.id,
                            "name": self.ref_entry.schema.name,
                        },
                    },
                },
                "id": entry.attrs.get(schema__name="name").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="name").schema.id,
                    "name": "name",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "bool", resp_data["attrs"])),
            {
                "type": AttrTypeValue["boolean"],
                "value": False,
                "id": entry.attrs.get(schema__name="bool").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="bool").schema.id,
                    "name": "bool",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "date", resp_data["attrs"])),
            {
                "type": AttrTypeValue["date"],
                "value": "2018-12-31",
                "id": entry.attrs.get(schema__name="date").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="date").schema.id,
                    "name": "date",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "group", resp_data["attrs"])),
            {
                "type": AttrTypeValue["group"],
                "value": {
                    "id": self.group.id,
                    "name": self.group.name,
                },
                "id": entry.attrs.get(schema__name="group").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="group").schema.id,
                    "name": "group",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "groups", resp_data["attrs"])),
            {
                "type": AttrTypeValue["array_group"],
                "value": [
                    {
                        "id": self.group.id,
                        "name": self.group.name,
                    }
                ],
                "id": entry.attrs.get(schema__name="groups").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="groups").schema.id,
                    "name": "groups",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "text", resp_data["attrs"])),
            {
                "type": AttrTypeValue["text"],
                "value": "fuga",
                "id": entry.attrs.get(schema__name="text").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="text").schema.id,
                    "name": "text",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "vals", resp_data["attrs"])),
            {
                "type": AttrTypeValue["array_string"],
                "value": ["foo", "bar"],
                "id": entry.attrs.get(schema__name="vals").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="vals").schema.id,
                    "name": "vals",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "refs", resp_data["attrs"])),
            {
                "type": AttrTypeValue["array_object"],
                "value": [
                    {
                        "id": self.ref_entry.id,
                        "name": self.ref_entry.name,
                        "schema": {
                            "id": self.ref_entry.schema.id,
                            "name": self.ref_entry.schema.name,
                        },
                    }
                ],
                "id": entry.attrs.get(schema__name="refs").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="refs").schema.id,
                    "name": "refs",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "names", resp_data["attrs"])),
            {
                "type": AttrTypeValue["array_named_object"],
                "value": [
                    {
                        "foo": {
                            "id": self.ref_entry.id,
                            "name": self.ref_entry.name,
                            "schema": {
                                "id": self.ref_entry.schema.id,
                                "name": self.ref_entry.schema.name,
                            },
                        },
                    },
                    {
                        "bar": {
                            "id": self.ref_entry.id,
                            "name": self.ref_entry.name,
                            "schema": {
                                "id": self.ref_entry.schema.id,
                                "name": self.ref_entry.schema.name,
                            },
                        },
                    },
                ],
                "id": entry.attrs.get(schema__name="names").id,
                "schema": {
                    "id": entry.attrs.get(schema__name="names").schema.id,
                    "name": "names",
                },
            },
        )
        self.assertEqual(
            next(filter(lambda x: x["schema"]["name"] == "opt", resp_data["attrs"])),
            {
                "type": AttrTypeValue["string"],
                "value": AttrTypeStr.DEFAULT_VALUE,
                "id": None,
                "schema": {
                    "id": self.entity.attrs.get(name="opt").id,
                    "name": "opt",
                },
            },
        )

    def test_retrieve_entry_without_permission(self):
        entry: Entry = self.add_entry(self.user, "test-entry", self.entity)

        # permission nothing entity
        self.entity.is_public = False
        self.entity.save()
        resp = self.client.get("/entry/api/v2/%d/" % entry.id)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readble entity
        self.user.permissions.add(self.entity.readable)
        resp = self.client.get("/entry/api/v2/%d/" % entry.id)
        self.assertEqual(resp.status_code, 200)

        # permission nothing entry
        entry.is_public = False
        entry.save()
        resp = self.client.get("/entry/api/v2/%d/" % entry.id)
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readble entry
        self.user.permissions.add(entry.readable)
        resp = self.client.get("/entry/api/v2/%d/" % entry.id)
        self.assertEqual(resp.status_code, 200)

    def test_retrieve_entry_with_invalid_param(self):
        resp = self.client.get("/entry/api/v2/%s/" % "hoge")
        self.assertEqual(resp.status_code, 404)

        resp = self.client.get("/entry/api/v2/%s/" % 9999)
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"detail": "Not found."})

    @mock.patch("custom_view.is_custom", mock.Mock(return_value=True))
    @mock.patch("custom_view.call_custom")
    def test_retrieve_entry_with_customview(self, mock_call_custom):
        def side_effect(handler_name, entity_name, entry, entry_attrs):
            self.assertEqual(handler_name, "get_entry_attr")
            self.assertEqual(entity_name, "test-entity")
            self.assertEqual(entry.name, "test-entry")
            self.assertEqual(len(entry_attrs), len(self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY))

            # add attribute
            entry_attrs.append(
                {
                    "id": 0,
                    "type": AttrTypeValue["string"],
                    "value": "hoge",
                    "schema": {
                        "id": 0,
                        "name": "fuga",
                    },
                }
            )

            return entry_attrs

        mock_call_custom.side_effect = side_effect

        entry: Entry = self.add_entry(self.user, "test-entry", self.entity)

        resp = self.client.get("/entry/api/v2/%s/" % entry.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            len(resp.json()["attrs"]), len(self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY) + 1
        )
        self.assertEqual(
            resp.json()["attrs"][-1],
            {
                "id": 0,
                "type": AttrTypeValue["string"],
                "value": "hoge",
                "schema": {
                    "id": 0,
                    "name": "fuga",
                },
            },
        )

    def test_update_entry(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)

        attr = {}
        for attr_name in [x["name"] for x in self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY]:
            attr[attr_name] = self.entity.attrs.get(name=attr_name)

        params = {
            "name": "entry-change",
            "attrs": [
                {"id": attr["val"].id, "value": "hoge"},
                {"id": attr["vals"].id, "value": ["hoge", "fuga"]},
                {"id": attr["ref"].id, "value": self.ref_entry.id},
                {"id": attr["refs"].id, "value": [self.ref_entry.id]},
                {"id": attr["name"].id, "value": {"name": "hoge", "id": self.ref_entry.id}},
                {"id": attr["names"].id, "value": [{"name": "hoge", "id": self.ref_entry.id}]},
                {"id": attr["group"].id, "value": self.group.id},
                {"id": attr["groups"].id, "value": [self.group.id]},
                {"id": attr["text"].id, "value": "hoge\nfuga"},
                {"id": attr["bool"].id, "value": True},
                {"id": attr["date"].id, "value": "2018-12-31"},
            ],
        }
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(
            resp.json(),
            {
                "id": entry.id,
                "name": "entry-change",
            },
        )
        self.assertEqual(entry.status, 0)
        self.assertEqual(
            {
                attrv.parent_attr.name: attrv.get_value()
                for attrv in [attr.get_latest_value() for attr in entry.attrs.all()]
            },
            {
                "bool": True,
                "date": datetime.date(2018, 12, 31),
                "group": "group0",
                "groups": ["group0"],
                "name": {"hoge": "r-0"},
                "names": [{"hoge": "r-0"}],
                "ref": "r-0",
                "refs": ["r-0"],
                "text": "hoge\nfuga",
                "val": "hoge",
                "vals": ["hoge", "fuga"],
            },
        )
        search_result = self._es.search(body={"query": {"term": {"name": "entry-change"}}})
        self.assertEqual(search_result["hits"]["total"], 1)

    def test_update_entry_without_permission(self):
        params = {
            "name": "entry-change",
        }
        entry: Entry = self.add_entry(self.user, "entry", self.entity)

        # permission nothing entity
        self.entity.is_public = False
        self.entity.save()
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readable entity
        self.user.permissions.add(self.entity.readable)
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission writable entity
        self.user.permissions.add(self.entity.writable)
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 200)

        # permission nothing entry
        entry.is_public = False
        entry.save()
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readable entry
        self.user.permissions.add(entry.readable)
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission writable entry
        self.user.permissions.add(entry.writable)
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 200)

    def test_update_entry_without_permission_attr(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        entity_attr = {}
        attr = {}
        for attr_name in [x["name"] for x in self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY]:
            entity_attr[attr_name] = self.entity.attrs.get(name=attr_name)
            attr[attr_name] = entry.attrs.get(schema__name=attr_name)

        params = {
            "attrs": [
                {"id": entity_attr["val"].id, "value": "hoge"},
                {"id": entity_attr["vals"].id, "value": ["hoge"]},
            ]
        }

        entity_attr["vals"].is_public = False
        entity_attr["vals"].save()
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(attr["val"].get_latest_value().get_value(), "hoge")
        self.assertEqual(attr["vals"].get_latest_value().get_value(), [])

        params = {
            "attrs": [
                {"id": entity_attr["val"].id, "value": "fuga"},
                {"id": entity_attr["vals"].id, "value": ["fuga"]},
            ]
        }

        entity_attr["vals"].is_public = True
        entity_attr["vals"].save()
        attr["vals"].is_public = False
        attr["vals"].save()
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(attr["val"].get_latest_value().get_value(), "fuga")
        self.assertEqual(attr["vals"].get_latest_value().get_value(), [])

    def test_update_entry_with_invalid_param_entry_id(self):
        resp = self.client.put(
            "/entry/api/v2/%s/" % "hoge", json.dumps({"name": "entry1"}), "application/json"
        )
        self.assertEqual(resp.status_code, 404)

        resp = self.client.put(
            "/entry/api/v2/%s/" % 9999, json.dumps({"name": "entry1"}), "application/json"
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"detail": "Not found."})

    def test_update_entry_with_invalid_param_name(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id,
            json.dumps({"name": "a" * (Entry._meta.get_field("name").max_length + 1)}),
            "application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            resp.json(), {"name": ["Ensure this field has no more than 200 characters."]}
        )

        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id,
            json.dumps({"name": "a" * (Entry._meta.get_field("name").max_length)}),
            "application/json",
        )
        self.assertEqual(resp.status_code, 200)

        hoge_entry: Entry = self.add_entry(self.user, "hoge", self.entity)
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps({"name": "hoge"}), "application/json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), {"non_field_errors": ["specified name(hoge) already exists"]})

        hoge_entry.delete()
        resp = self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps({"name": "hoge"}), "application/json"
        )
        self.assertEqual(resp.status_code, 200)

    def test_update_entry_with_invalid_param_attrs(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        attr = {}
        for attr_name in [x["name"] for x in self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY]:
            attr[attr_name] = self.entity.attrs.get(name=attr_name)

        test_values = [
            {
                "input": "hoge",
                "error_msg": {"attrs": ['Expected a list of items but got type "str".']},
            },
            {
                "input": ["hoge"],
                "error_msg": {
                    "attrs": {
                        "0": {
                            "non_field_errors": [
                                "Invalid data. Expected a dictionary, but got str."
                            ]
                        }
                    }
                },
            },
            {
                "input": [{"attr1": "hoge"}],
                "error_msg": {
                    "attrs": {
                        "0": {
                            "id": ["This field is required."],
                            "value": ["This field is required."],
                        }
                    }
                },
            },
            {
                "input": [
                    {
                        "id": "hoge",
                        "value": "hoge",
                    }
                ],
                "error_msg": {"attrs": {"0": {"id": ["A valid integer is required."]}}},
            },
            {
                "input": [
                    {
                        "id": 9999,
                        "value": "hoge",
                    }
                ],
                "error_msg": {"non_field_errors": ["attrs id(9999) does not exist"]},
            },
            {
                "input": [
                    {
                        "id": attr["ref"].id,
                        "value": "hoge",
                    }
                ],
                "error_msg": {
                    "non_field_errors": ["attrs id(%s) - value(hoge) is not int" % attr["ref"].id]
                },
            },
        ]

        for test_value in test_values:
            params = {"attrs": test_value["input"]}
            resp = self.client.put(
                "/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json"
            )
            self.assertEqual(resp.status_code, 400)
            self.assertEqual(resp.json(), test_value["error_msg"])

    @mock.patch("entry.tasks.notify_update_entry.delay")
    def test_update_entry_notify(self, mock_task):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        self.client.put(
            "/entry/api/v2/%s/" % entry.id, json.dumps({"name": "hoge"}), "application/json"
        )

        self.assertTrue(mock_task.called)

    @mock.patch("custom_view.is_custom", mock.Mock(return_value=True))
    @mock.patch("custom_view.call_custom")
    def test_update_entry_with_customview(self, mock_call_custom):
        def side_effect(handler_name, entity_name, user, *args):
            self.assertEqual(entity_name, self.entity.name)
            self.assertEqual(user, self.user)
            self.assertEqual(args[1], entry)

            # Check specified parameters are expected
            if handler_name == "before_update_entry":
                self.assertEqual(args[0], params)

            if handler_name == "after_update_entry":
                self.assertEqual(args[0], params["attrs"])

        mock_call_custom.side_effect = side_effect

        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        attr = {}
        for attr_name in [x["name"] for x in self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY]:
            attr[attr_name] = self.entity.attrs.get(name=attr_name)
        params = {
            "name": "hoge",
            "attrs": [
                {"id": attr["val"].id, "value": "fuga"},
            ],
        }
        self.client.put("/entry/api/v2/%s/" % entry.id, json.dumps(params), "application/json")

        self.assertTrue(mock_call_custom.called)

    def test_update_entry_with_no_update(self):
        entry: Entry = self.add_entry(
            self.user,
            "Entry",
            self.entity,
            values={
                "val": "hoge",
                "vals": ["hoge"],
            },
        )
        entity_attr = {}
        attr = {}
        for attr_name in [x["name"] for x in self.ALL_TYPED_ATTR_PARAMS_FOR_CREATING_ENTITY]:
            entity_attr[attr_name] = self.entity.attrs.get(name=attr_name)
            attr[attr_name] = entry.attrs.get(schema__name=attr_name)

        params = {
            "attrs": [
                {"id": entity_attr["val"].id, "value": "hoge"},
                {"id": entity_attr["vals"].id, "value": ["fuga"]},
            ]
        }
        self.client.put(
            "/entry/api/v2/%s/" % self.ref_entry.id, json.dumps(params), "application/json"
        )

        self.assertEqual(attr["val"].values.count(), 1)
        self.assertEqual(attr["vals"].values.count(), 2)

    @mock.patch(
        "entry.tasks.register_referrals.delay", mock.Mock(side_effect=tasks.register_referrals)
    )
    def test_update_entry_with_referral(self):
        self.add_entry(
            self.user,
            "Entry",
            self.entity,
            values={
                "ref": self.ref_entry.id,
            },
        )
        params = {
            "name": "ref-change",
        }
        self.client.put(
            "/entry/api/v2/%s/" % self.ref_entry.id, json.dumps(params), "application/json"
        )

        ret = Entry.search_entries(self.user, [self.entity.id], [{"name": "ref"}])
        self.assertEqual(ret["ret_count"], 1)
        self.assertEqual(ret["ret_values"][0]["entry"]["name"], "Entry")
        self.assertEqual(ret["ret_values"][0]["attrs"]["ref"]["value"]["name"], "ref-change")

    def test_destroy_entry(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)

        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(resp.content, b"")

        entry.refresh_from_db()
        self.assertRegex(entry.name, "entry_deleted_")
        self.assertFalse(entry.is_active)

        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), ["specified entry has already been deleted"])

    def test_destroy_entry_without_permission(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)

        # permission nothing entity
        self.entity.is_public = False
        self.entity.save()
        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readable entity
        self.user.permissions.add(self.entity.readable)
        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission writable entity
        self.user.permissions.add(self.entity.writable)
        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 204)

        entry.restore()

        # permission nothing entry
        entry.is_public = False
        entry.save()
        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readable entry
        self.user.permissions.add(entry.readable)
        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission writable entry
        self.user.permissions.add(entry.writable)
        resp = self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 204)

    def test_destory_entry_with_invalid_param(self):
        resp = self.client.delete("/entry/api/v2/%s/" % "hoge", None, "application/json")
        self.assertEqual(resp.status_code, 404)

        resp = self.client.delete("/entry/api/v2/%s/" % 9999, None, "application/json")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"detail": "Not found."})

    @mock.patch("custom_view.is_custom", mock.Mock(return_value=True))
    @mock.patch("custom_view.call_custom")
    def test_destroy_entry_with_custom_view(self, mock_call_custom):
        def side_effect(handler_name, entity_name, user, entry):
            self.assertTrue(handler_name in ["before_delete_entry", "after_delete_entry"])
            self.assertEqual(entity_name, self.entity.name)
            self.assertEqual(user, self.user)
            self.assertEqual(entry, entry)

        mock_call_custom.side_effect = side_effect

        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")
        self.assertTrue(mock_call_custom.called)

    @mock.patch("entry.tasks.notify_delete_entry.delay")
    def test_destroy_entry_notify(self, mock_task):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        self.client.delete("/entry/api/v2/%s/" % entry.id, None, "application/json")

        self.assertTrue(mock_task.called)

    def test_restore_entry(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        entry.delete()

        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.content, b"")

        entry.refresh_from_db()
        self.assertRegex(entry.name, "entry")
        self.assertTrue(entry.is_active)
        self.assertEqual(entry.status, 0)

        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), ["specified entry has not deleted"])

    def test_restore_entry_without_permission(self):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        entry.delete()

        # permission nothing entity
        self.entity.is_public = False
        self.entity.save()
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readable entity
        self.user.permissions.add(self.entity.readable)
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission writable entity
        self.user.permissions.add(self.entity.writable)
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission full entity
        self.user.permissions.add(self.entity.full)
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 201)

        entry.delete()

        # permission nothing entry
        entry.is_public = False
        entry.save()
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission readable entry
        self.user.permissions.add(entry.readable)
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission writable entry
        self.user.permissions.add(entry.writable)
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json(), {"detail": "You do not have permission to perform this action."}
        )

        # permission full entry
        self.user.permissions.add(entry.full)
        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 201)

    def test_restore_entry_with_invalid_param(self):
        resp = self.client.post("/entry/api/v2/%s/restore/" % "hoge", None, "application/json")
        self.assertEqual(resp.status_code, 404)

        resp = self.client.post("/entry/api/v2/%s/restore/" % 9999, None, "application/json")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json(), {"detail": "Not found."})

        entry = self.add_entry(self.user, "entry", self.entity)
        entry.delete()
        self.add_entry(self.user, "entry", self.entity)

        resp = self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), ["specified entry has already exist other"])

    @mock.patch("custom_view.is_custom", mock.Mock(return_value=True))
    @mock.patch("custom_view.call_custom")
    def test_restore_entry_with_custom_view(self, mock_call_custom):
        def side_effect(handler_name, entity_name, user, entry):
            self.assertTrue(handler_name in ["before_restore_entry", "after_restore_entry"])
            self.assertEqual(entity_name, self.entity.name)
            self.assertEqual(user, self.user)
            self.assertEqual(entry, entry)

        mock_call_custom.side_effect = side_effect

        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        entry.delete()
        self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")
        self.assertTrue(mock_call_custom.called)

    @mock.patch("entry.tasks.notify_create_entry.delay")
    def test_restore_entry_notify(self, mock_task):
        entry: Entry = self.add_entry(self.user, "entry", self.entity)
        entry.delete()
        self.client.post("/entry/api/v2/%s/restore/" % entry.id, None, "application/json")

        self.assertTrue(mock_task.called)

    def test_serach_entry(self):
        ref_entry4 = self.add_entry(self.user, "hoge4", self.ref_entity)
        ref_entry5 = self.add_entry(self.user, "hoge5", self.ref_entity)
        ref_entry6 = self.add_entry(self.user, "hoge6", self.ref_entity)
        ref_entry7 = self.add_entry(self.user, "hoge7", self.ref_entity)

        self.add_entry(
            self.user,
            "entry1",
            self.entity,
            values={
                "val": "hoge1",
            },
        )
        self.add_entry(
            self.user,
            "entry2",
            self.entity,
            values={
                "vals": ["hoge2", "fuga2"],
            },
        )
        self.add_entry(
            self.user,
            "entry3",
            self.entity,
            values={
                "text": "hoge3",
            },
        )
        self.add_entry(
            self.user,
            "entry4",
            self.entity,
            values={
                "ref": ref_entry4.id,
            },
        )
        self.add_entry(
            self.user,
            "entry5",
            self.entity,
            values={
                "refs": [ref_entry5.id],
            },
        )
        self.add_entry(
            self.user,
            "entry6",
            self.entity,
            values={
                "name": {"name": "index6", "id": ref_entry6.id},
            },
        )
        self.add_entry(
            self.user,
            "entry7",
            self.entity,
            values={"names": [{"name": "index7", "id": ref_entry7.id}]},
        )

        # test value attribute
        for x in range(1, 3):
            resp = self.client.get("/entry/api/v2/search/?query=hoge%s" % x)
            self.assertEqual(resp.status_code, 200)
            resp_data = resp.json()
            self.assertEqual(len(resp_data), 1)
            entry: Entry = Entry.objects.get(name="entry%s" % x)
            self.assertEqual(resp_data[0]["id"], entry.id)
            self.assertEqual(resp_data[0]["name"], entry.name)

        # test object attribute
        for x in range(4, 4):
            resp = self.client.get("/entry/api/v2/search/?query=hoge%s" % x)
            self.assertEqual(resp.status_code, 200)
            resp_data = resp.json()
            self.assertEqual(len(resp_data), 2)
            ref_entry: Entry = Entry.objects.get(name="hoge%s" % x)
            entry: Entry = Entry.objects.get(name="entry%s" % x)
            self.assertEqual(resp_data[0]["id"], ref_entry.id)
            self.assertEqual(resp_data[0]["name"], ref_entry.name)
            self.assertEqual(resp_data[1]["id"], entry.id)
            self.assertEqual(resp_data[1]["name"], entry.name)

        # test named_object attribute
        for x in range(6, 2):
            resp = self.client.get("/entry/api/v2/search/?query=index%s" % x)
            self.assertEqual(resp.status_code, 200)
            resp_data = resp.json()
            self.assertEqual(len(resp_data), 1)
            entry: Entry = Entry.objects.get(name="entry%s" % x)
            self.assertEqual(resp_data[0]["id"], entry.id)
            self.assertEqual(resp_data[0]["name"], entry.name)

    def test_serach_entry_with_regexp(self):
        entry: Entry = self.add_entry(
            self.user,
            "entry",
            self.entity,
            values={
                "val": "hoge",
                "ref": self.ref_entry.id,
            },
        )

        resp = self.client.get("/entry/api/v2/search/?query=Og")
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertEqual(len(resp_data), 1)
        self.assertEqual(resp_data[0]["id"], entry.id)
        self.assertEqual(resp_data[0]["name"], entry.name)

        resp = self.client.get("/entry/api/v2/search/?query=R-")
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertEqual(len(resp_data), 2)
        self.assertEqual(resp_data[0]["id"], self.ref_entry.id)
        self.assertEqual(resp_data[0]["name"], self.ref_entry.name)
        self.assertEqual(resp_data[1]["id"], entry.id)
        self.assertEqual(resp_data[1]["name"], entry.name)

    def test_serach_entry_multi_match(self):
        entry: Entry = self.add_entry(
            self.user,
            "hoge",
            self.entity,
            values={
                "val": "hoge",
            },
        )

        resp = self.client.get("/entry/api/v2/search/?query=hoge")
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertEqual(len(resp_data), 1)
        self.assertEqual(resp_data[0]["id"], entry.id)
        self.assertEqual(resp_data[0]["name"], entry.name)

    def test_serach_entry_order_by(self):
        self.add_entry(self.user, "z_hoge", self.entity)
        self.add_entry(self.user, "a_hoge", self.entity)
        self.add_entry(
            self.user,
            "a_entry",
            self.entity,
            values={
                "val": "z_hoge",
            },
        )
        self.add_entry(
            self.user,
            "z_entry",
            self.entity,
            values={
                "val": "a_hoge",
            },
        )

        # Entry name match has high priority
        resp = self.client.get("/entry/api/v2/search/?query=hoge")
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertEqual(len(resp_data), 4)
        for i, entry_name in enumerate(["a_hoge", "z_hoge", "a_entry", "z_entry"]):
            entry: Entry = Entry.objects.get(name=entry_name)
            self.assertEqual(resp_data[i]["id"], entry.id)
            self.assertEqual(resp_data[i]["name"], entry.name)

    def test_serach_entry_deleted_entry(self):
        entry1 = self.add_entry(
            self.user,
            "entry1",
            self.entity,
            values={
                "val": "hoge1",
                "ref": self.ref_entry.id,
            },
        )
        entry1.delete()

        self.add_entry(
            self.user,
            "entry2",
            self.entity,
            values={
                "ref": self.ref_entry.id,
            },
        )
        self.ref_entry.delete()

        for query in ["entry1", "hoge", "ref_entry"]:
            resp = self.client.get("/entry/api/v2/search/?query=%s" % query)
            self.assertEqual(resp.status_code, 200)
            resp_data = resp.json()
            self.assertEqual(len(resp_data), 0)

    def test_serach_entry_update_attrv(self):
        ref_entry1 = self.add_entry(self.user, "ref_entry1", self.ref_entity)
        ref_entry2 = self.add_entry(self.user, "ref_entry2", self.ref_entity)
        entry: Entry = self.add_entry(
            self.user,
            "entry",
            self.entity,
            values={
                "val": "hoge",
                "vals": ["hoge"],
                "ref": ref_entry1.id,
                "refs": [ref_entry1.id],
            },
        )
        entry.attrs.get(name="val").add_value(self.user, "fuga")
        entry.attrs.get(name="vals").add_value(self.user, ["fuga"])
        entry.attrs.get(name="ref").add_value(self.user, ref_entry2.id)
        entry.attrs.get(name="refs").add_value(self.user, [ref_entry2.id])

        resp = self.client.get("/entry/api/v2/search/?query=hoge")
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertEqual(len(resp_data), 0)

        resp = self.client.get("/entry/api/v2/search/?query=ref_entry1")
        self.assertEqual(resp.status_code, 200)
        resp_data = resp.json()
        self.assertEqual(len(resp_data), 1)
        self.assertEqual(resp_data[0]["id"], ref_entry1.id)
        self.assertEqual(resp_data[0]["name"], ref_entry1.name)

    def test_entry_after_entity_attr_was_deleted(self):
        entry: Entry = self.add_entry(self.user, "Entry", self.entity)

        # delete EntityAttr, then check it won't be returned in response
        self.entity.attrs.get(name="val", is_active=True).delete()

        resp = self.client.get("/entry/api/v2/%d/" % entry.id)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            sorted([attr["schema"]["name"] for attr in resp.json()["attrs"]]),
            sorted(
                ["ref", "name", "bool", "date", "group", "groups", "text", "vals", "refs", "names"]
            ),
        )
