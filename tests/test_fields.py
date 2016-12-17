from brink import fields, models
import pytest


class DummyModel(models.Model):
    title = fields.CharField()


def test_field_treat():
    field = fields.Field()
    assert field.validate("val") == "val"


def test_field_validate_required():
    field = fields.Field(required=True)

    with pytest.raises(fields.FieldRequired):
        field.validate(None)

    assert field.validate("val") == "val"


def test_integer_field_validate_required():
    field1 = fields.IntegerField(required=True)

    with pytest.raises(fields.FieldRequired):
        field1.validate(None)

    field2 = fields.IntegerField()

    field2.validate(None)


def test_integer_field_validate_type():
    field = fields.IntegerField()

    with pytest.raises(fields.FieldInvalidType):
        field.validate("test")

    assert field.validate(10) == 10


def test_char_field_validate_required():
    field1 = fields.CharField(required=True)

    with pytest.raises(fields.FieldRequired):
        field1.validate(None)

    field2 = fields.CharField()
    field2.validate(None)


def test_char_field_validate_min_length():
    field = fields.CharField(min_length=5)

    with pytest.raises(fields.FieldInvalidLength):
        field.validate("test")

    assert field.validate("testing") == "testing"


def test_char_field_validate_max_length():
    field = fields.CharField(max_length=5)

    with pytest.raises(fields.FieldInvalidLength):
        field.validate("testing")

    assert field.validate("test") == "test"


def test_char_field_validate_type():
    field = fields.CharField()

    with pytest.raises(fields.FieldInvalidType):
        field.validate(10)

    assert field.validate("test") == "test"


def test_bool_field_validate_required():
    field1 = fields.BooleanField(required=True)

    with pytest.raises(fields.FieldRequired):
        field1.validate(None)

    field2 = fields.BooleanField()
    field2.validate(None)


def test_bool_field_validate_type():
    field = fields.BooleanField()

    with pytest.raises(fields.FieldInvalidType):
        field.validate("test")

    assert field.validate(True)
    assert not field.validate(False)


def test_list_field_validate_subtype():
    field = fields.ListField(fields.CharField())

    with pytest.raises(fields.FieldInvalidType):
        field.validate([1, 2])

    with pytest.raises(fields.FieldInvalidType):
        field.validate([1, "test"])

    field.validate(["test", "test2"])
    assert field.validate(None) == []


def test_reference_field_treat():
    field = fields.ReferenceField(DummyModel)
    model = DummyModel(id="test", title="Test")
    assert field.treat(model) == "test"


def test_reference_field_show():
    field = fields.ReferenceField(DummyModel)
    model = field.show(DummyModel(title="Test"))
    assert model.title == "Test"


def test_reference_list_field_treat():
    field = fields.ReferenceListField(DummyModel)
    model = DummyModel(id="test", title="Test")
    assert field.treat([model]) == ["test"]


def test_reference_list_field_show():
    field = fields.ReferenceListField(DummyModel)
    data = DummyModel(title="Test")
    models = field.show([data])

    for model in models:
        assert model.title == "Test"
