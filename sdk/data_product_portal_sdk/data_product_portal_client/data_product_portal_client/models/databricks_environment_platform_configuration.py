from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.databricks_environment_platform_configuration_workspace_urls import (
        DatabricksEnvironmentPlatformConfigurationWorkspaceUrls,
    )


T = TypeVar("T", bound="DatabricksEnvironmentPlatformConfiguration")


@_attrs_define
class DatabricksEnvironmentPlatformConfiguration:
    """
    Attributes:
        workspace_urls (DatabricksEnvironmentPlatformConfigurationWorkspaceUrls):
        account_id (str):
        metastore_id (str):
        credential_name (str):
    """

    workspace_urls: "DatabricksEnvironmentPlatformConfigurationWorkspaceUrls"
    account_id: str
    metastore_id: str
    credential_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_urls = self.workspace_urls.to_dict()

        account_id = self.account_id

        metastore_id = self.metastore_id

        credential_name = self.credential_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_urls": workspace_urls,
                "account_id": account_id,
                "metastore_id": metastore_id,
                "credential_name": credential_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.databricks_environment_platform_configuration_workspace_urls import (
            DatabricksEnvironmentPlatformConfigurationWorkspaceUrls,
        )

        d = src_dict.copy()
        workspace_urls = (
            DatabricksEnvironmentPlatformConfigurationWorkspaceUrls.from_dict(
                d.pop("workspace_urls")
            )
        )

        account_id = d.pop("account_id")

        metastore_id = d.pop("metastore_id")

        credential_name = d.pop("credential_name")

        databricks_environment_platform_configuration = cls(
            workspace_urls=workspace_urls,
            account_id=account_id,
            metastore_id=metastore_id,
            credential_name=credential_name,
        )

        databricks_environment_platform_configuration.additional_properties = d
        return databricks_environment_platform_configuration

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
