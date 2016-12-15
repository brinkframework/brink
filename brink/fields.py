import sys


class FieldError(Exception):
    """
    FieldError base class. All field errors inherit from this exception class.
    """
    pass


class FieldRequired(FieldError):
    """
    Thrown whenever a required field is not provided.
    """
    pass


class FieldInvalidType(FieldError):
    """
    Thrown whenever a value of an invalid type is provided to the field.
    """
    pass


class FieldInvalidLength(FieldError):
    """
    Thrown when the provided value either is too short or too long.
    """
    pass


def validator(m):
    """
    Marks a field method as a validator, and thus it will be executed whenever
    ``validate`` is called on the field.
    """
    m.validator = True
    return m


class FieldBase(type):

    def __init__(self, name, bases, attrs):
        self.validators = []

        for k in dir(self):
            v = getattr(self, k)
            if hasattr(v, "validator") and v.validator:
                self.validators.append(v)


class Field(object, metaclass=FieldBase):
    """
    Field base class. All other fields inherit from this class, so usually you
    want to use one of the more specialized fields. However, there might be
    cases where you wanna store an arbitrary value that does not fit well into
    any other standard field, and in that case you could use Field to store any
    value.
    """

    def __init__(self, pk=False, required=False, hidden=False):
        self.pk = pk
        self.required = required
        self.hidden = hidden

    def treat(self, data):
        """
        All field values will be passed through this method before being
        saved to the database. Thus, you can make any final modifications
        to the value here.
        """
        return data

    def show(self, data):
        """
        All field values will be passed through this method before being
        rendered as json. Thus you can perform any desired modifications to the
        final output here.
        """
        return data

    def validate(self, data):
        """
        Runs all field validators.
        """
        for v in self.validators:
            v(self, data)
        return data

    @validator
    def validate_required(self, data):
        """
        Validates that a value is present if the field is required.
        """
        if self.required and data is None:
            raise FieldRequired()
        return data


class IntegerField(Field):
    """
    IntegerField. Use to hold integers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @validator
    def validate_type(self, data):
        if data is None:
            return

        if type(data) is not int:
            raise FieldInvalidType()


class CharField(Field):
    """
    CharField holds a char sequence.
    """

    def __init__(self, *args, min_length=0, max_length=sys.maxsize, **kwargs):
        self.min_length = min_length
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    @validator
    def validate_type(self, data):
        if data is None:
            return

        if type(data) is not str:
            raise FieldInvalidType()

    @validator
    def validate_min_length(self, data):
        if not hasattr(data, "__len__"):
            return

        if len(data) < self.min_length:
            raise FieldInvalidLength()

    @validator
    def validate_max_length(self, data):
        if not hasattr(data, "__len__"):
            return

        if len(data) > self.max_length:
            raise FieldInvalidLength()


class PasswordField(CharField):
    """
    PasswordField is suitable for holding passwords (duh). Hides the value by
    default when rendered to json.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, hidden=True, **kwargs)


class BooleanField(Field):
    """
    BooleanField is suitable to hold boolean values.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @validator
    def validate_type(self, data):
        if data is None:
            return

        if type(data) is not bool:
            raise FieldInvalidType()


class ListField(Field):
    """
    Holds a list of values. Takes another field type as the list value.
    """

    def __init__(self, field_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_type = field_type

    def treat(self, data):
        if data is None:
            return []
        return data

    def show(self, data):
        if data is None:
            return []
        return [self.field_type.show(val) for val in data]

    def validate(self, data):
        data = data or []
        for item in data:
            self.field_type.validate(item)
        return data


class ReferenceField(Field):
    """
    Holds a reference to another model. Will be represented as the other
    object's id in the database, and later possibly resolved as it is fetched
    from the database.
    """

    def __init__(self, model_ref_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_ref_type = model_ref_type

    def treat(self, data):
        if not hasattr(data, "id") or data is None:
            return data
        return data.id

    def validate(self, data):
        pass
