from typing import Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo


class AuthenticationConfig(BaseModel):
    """
    Configuration model for the JWT access token authentication/authorization.
    """

    enabled: bool
    public_key_path: Optional[str] = Field(default=None, validate_default=True)
    jwt_algorithm: Optional[str] = Field(default=None, validate_default=True)

    @field_validator("public_key_path", "jwt_algorithm")
    @classmethod
    def validate_optional_fields(
        cls, field_value: str, info: ValidationInfo
    ) -> Optional[str]:
        """
        Validator for the `public_key_path` and `jwt_algorithm` fields to make them mandatory if the value of the
        `enabled` field is `True`. It raises a `ValueError` if no value is provided for the field when the `enabled`
        field has been set to `True`.

        :param field_value: The value of the field.
        :param info: Validation info from pydantic.
        :raises ValueError: If no value is provided for the field when the `enabled` field is set to `True`.
        :return: The value of the field.
        """
        if (
            "enabled" in info.data and info.data["enabled"] is True
        ) and field_value is None:
            raise ValueError("Field required")
        return field_value
