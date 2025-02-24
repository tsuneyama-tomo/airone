import enum
from typing import Any

from six import with_metaclass

_ATTR_OBJECT_TYPE = 1 << 0
_ATTR_STRING_TYPE = 1 << 1
_ATTR_TEXT_TYPE = 1 << 2
_ATTR_BOOL_TYPE = 1 << 3
_ATTR_GROUP_TYPE = 1 << 4
_ATTR_DATE_TYPE = 1 << 5
_ATTR_ROLE_TYPE = 1 << 6
_ATTR_ARRAY_TYPE = 1 << 10
_ATTR_NAMED_TYPE = 1 << 11


class MetaAttrType(type):
    def __eq__(cls, comp):
        if isinstance(comp, int):
            return cls.TYPE == comp
        elif isinstance(comp, str):
            return cls.NAME == comp
        else:
            return cls.TYPE == comp.TYPE
        return False

    def __ne__(cls, comp):
        return not cls == comp

    def __repr__(cls):
        return str(cls.TYPE)

    def __int__(cls):
        return cls.TYPE


class AttrTypeObj(with_metaclass(MetaAttrType)):
    NAME = "entry"
    TYPE = _ATTR_OBJECT_TYPE
    DEFAULT_VALUE = None


# STRING-type restricts data size to AttributeValue.MAXIMUM_VALUE_LENGTH
class AttrTypeStr(with_metaclass(MetaAttrType)):
    NAME = "string"
    TYPE = _ATTR_STRING_TYPE
    DEFAULT_VALUE = ""


class AttrTypeNamedObj(with_metaclass(MetaAttrType)):
    NAME = "named_entry"
    TYPE = _ATTR_OBJECT_TYPE | _ATTR_NAMED_TYPE
    DEFAULT_VALUE = {"name": "", "id": None}


class AttrTypeArrObj(with_metaclass(MetaAttrType)):
    NAME = "array_entry"
    TYPE = _ATTR_OBJECT_TYPE | _ATTR_ARRAY_TYPE
    DEFAULT_VALUE = []


class AttrTypeArrStr(with_metaclass(MetaAttrType)):
    NAME = "array_string"
    TYPE = _ATTR_STRING_TYPE | _ATTR_ARRAY_TYPE
    DEFAULT_VALUE = []


class AttrTypeArrNamedObj(with_metaclass(MetaAttrType)):
    NAME = "array_named_entry"
    TYPE = _ATTR_OBJECT_TYPE | _ATTR_NAMED_TYPE | _ATTR_ARRAY_TYPE
    DEFAULT_VALUE: Any = dict().values()


class AttrTypeArrGroup(with_metaclass(MetaAttrType)):
    NAME = "array_group"
    TYPE = _ATTR_GROUP_TYPE | _ATTR_ARRAY_TYPE
    DEFAULT_VALUE = []


class AttrTypeText(with_metaclass(MetaAttrType)):
    NAME = "textarea"
    TYPE = _ATTR_TEXT_TYPE
    DEFAULT_VALUE = ""


class AttrTypeBoolean(with_metaclass(MetaAttrType)):
    NAME = "boolean"
    TYPE = _ATTR_BOOL_TYPE
    DEFAULT_VALUE = False


class AttrTypeGroup(with_metaclass(MetaAttrType)):
    NAME = "group"
    TYPE = _ATTR_GROUP_TYPE
    DEFAULT_VALUE = None


class AttrTypeDate(with_metaclass(MetaAttrType)):
    NAME = "date"
    TYPE = _ATTR_DATE_TYPE
    DEFAULT_VALUE = None


class AttrTypeRole(with_metaclass(MetaAttrType)):
    NAME = "role"
    TYPE = _ATTR_ROLE_TYPE
    DEFAULT_VALUE = None


class AttrTypeArrRole(with_metaclass(MetaAttrType)):
    NAME = "array_role"
    TYPE = _ATTR_ROLE_TYPE | _ATTR_ARRAY_TYPE
    DEFAULT_VALUE = []


AttrTypes = [
    AttrTypeStr,
    AttrTypeObj,
    AttrTypeNamedObj,
    AttrTypeArrStr,
    AttrTypeArrObj,
    AttrTypeArrNamedObj,
    AttrTypeArrGroup,
    AttrTypeText,
    AttrTypeBoolean,
    AttrTypeGroup,
    AttrTypeDate,
    AttrTypeRole,
    AttrTypeArrRole,
]
AttrTypeValue = {
    "object": AttrTypeObj.TYPE,
    "string": AttrTypeStr.TYPE,
    "named": _ATTR_NAMED_TYPE,
    "named_object": AttrTypeNamedObj.TYPE,
    "array": _ATTR_ARRAY_TYPE,
    "array_object": AttrTypeArrObj.TYPE,
    "array_string": AttrTypeArrStr.TYPE,
    "array_named_object": AttrTypeArrNamedObj.TYPE,
    "array_group": AttrTypeArrGroup.TYPE,
    "array_role": AttrTypeArrRole.TYPE,
    "text": AttrTypeText.TYPE,
    "boolean": AttrTypeBoolean.TYPE,
    "group": AttrTypeGroup.TYPE,
    "date": AttrTypeDate.TYPE,
    "role": AttrTypeRole.TYPE,
}
AttrDefaultValue = {
    AttrTypeValue["object"]: AttrTypeObj.DEFAULT_VALUE,
    AttrTypeValue["string"]: AttrTypeStr.DEFAULT_VALUE,
    AttrTypeValue["named_object"]: AttrTypeNamedObj.DEFAULT_VALUE,
    AttrTypeValue["array_object"]: AttrTypeArrObj.DEFAULT_VALUE,
    AttrTypeValue["array_string"]: AttrTypeArrStr.DEFAULT_VALUE,
    AttrTypeValue["array_named_object"]: AttrTypeArrNamedObj.DEFAULT_VALUE,
    AttrTypeValue["array_group"]: AttrTypeArrGroup.DEFAULT_VALUE,
    AttrTypeValue["array_role"]: AttrTypeArrRole.DEFAULT_VALUE,
    AttrTypeValue["text"]: AttrTypeText.DEFAULT_VALUE,
    AttrTypeValue["boolean"]: AttrTypeBoolean.DEFAULT_VALUE,
    AttrTypeValue["group"]: AttrTypeGroup.DEFAULT_VALUE,
    AttrTypeValue["date"]: AttrTypeDate.DEFAULT_VALUE,
    AttrTypeValue["role"]: AttrTypeRole.DEFAULT_VALUE,
}


class AttrType(enum.Enum):
    OBJECT = AttrTypeObj.TYPE
    STRING = AttrTypeStr.TYPE
    NAMED_OBJECT = AttrTypeNamedObj.TYPE
    ARRAY_OBJECT = AttrTypeArrObj.TYPE
    ARRAY_STRING = AttrTypeArrStr.TYPE
    ARRAY_NAMED_OBJECT = AttrTypeArrNamedObj.TYPE
    ARRAY_NAMED_OBJECT_BOOLEAN = 3081  # unmanaged by AttrTypeXXX
    ARRAY_GROUP = AttrTypeArrGroup.TYPE
    ARRAY_ROLE = AttrTypeArrRole.TYPE
    TEXT = AttrTypeText.TYPE
    BOOLEAN = AttrTypeBoolean.TYPE
    GROUP = AttrTypeGroup.TYPE
    DATE = AttrTypeDate.TYPE
    ROLE = AttrTypeRole.TYPE
