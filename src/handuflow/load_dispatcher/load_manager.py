"""Centralized load manager."""

from __future__ import annotations


import yaml
from pathlib import Path
from typing import Any, cast
from .dataclass.load_manifest import LoadManifest
from ..platform.configurator import ConfigurationContext
from ..platform.storage import StoragePath
from .dataclass.feed_meta import FeedMeta
from .dataclass.address import Address
from .dataclass.feed_specs import FeedSpecs
from .dataclass.optimize_command import OptimizeCommand
from .dataclass.custom_selection import CustomSelection
from .dataclass.enforce_schema import EnforceSchema
from .dataclass.schema_field import SchemaField

# from .load_dispatcher import LoadDispatcher
from .load_planner import LoadPlanner


class LoadManager:
    """Central entry point for load execution."""

    def __init__(self, config_context: ConfigurationContext) -> None:
        """Initialize the load manager."""
        self.config_context = config_context

    def plan_load(self):
        manifest_collection = self.__generate_manifest_collection()
        planner = LoadPlanner()
        plan = planner.build_plan(manifest_collection)

        print(plan)

    def __generate_manifest_collection(self) -> list[LoadManifest]:
        list_of_feed_ymls = self.config_context.list_of_feed_ymls

        load_manifest_list: list[LoadManifest] = []

        for feed_yml in list_of_feed_ymls:
            current_feed_yml_dict = self.__read_yaml(feed_yml)
            feed_meta_raw = current_feed_yml_dict["feed_meta"]
            source_raw = current_feed_yml_dict["source"]
            target_raw = current_feed_yml_dict["target"]
            load_details_raw = current_feed_yml_dict["load_details"]
            feed_specs_raw = current_feed_yml_dict["feed_specs"]

            feed_meta = FeedMeta(
                unique_identifier=feed_meta_raw["unique_identifier"],
                vacuum_hours=int(feed_meta_raw["vacuum_hours"]),
                upstream_identifier=feed_meta_raw.get("upstream_identifier") or "",
                downstream_identifier=feed_meta_raw.get("downstream_identifier") or "",
                batch_key=feed_meta_raw.get("batch_key") or "",
            )

            source_address = Address(
                type=source_raw["type"],
                format=source_raw["format"],
                schema=source_raw["schema"],
                table=source_raw["table"],
            )

            target_address = Address(
                type=target_raw["type"],
                format=target_raw["format"],
                schema=target_raw["schema"],
                table=target_raw["table"],
            )

            load_manifest_list.append(
                LoadManifest(
                    feed_meta=feed_meta,
                    source_address=source_address,
                    target_address=target_address,
                    load_type=load_details_raw["type"],
                    feed_specs=self.__parse_feed_specs(feed_specs_raw),
                )
            )

        return load_manifest_list

    def __parse_feed_specs(self, feed_specs_raw: dict[str, Any]) -> FeedSpecs:
        optimize_command = None
        if "optimize_command" in feed_specs_raw:
            optimize_command = self.__parse_optimize_command(
                feed_specs_raw["optimize_command"]
            )

        custom_selection = None
        if "custom_selection" in feed_specs_raw:
            custom_selection = self.__parse_custom_selection(
                feed_specs_raw["custom_selection"]
            )

        enforce_schema = None
        if "enforce_schema" in feed_specs_raw:
            enforce_schema = self.__parse_enforce_schema(
                feed_specs_raw["enforce_schema"]
            )

        return FeedSpecs(
            primary_key=feed_specs_raw.get("primary_key"),
            composite_key=feed_specs_raw.get("composite_key") or [],
            partition_columns=feed_specs_raw.get("partition_columns") or [],
            optimize_command=optimize_command,
            custom_selection=custom_selection,
            enforce_schema=enforce_schema,
        )

    @staticmethod
    def __parse_optimize_command(
        optimize_command_raw: dict[str, Any],
    ) -> OptimizeCommand:
        where: list[dict[str, str]] = []
        where_raw = optimize_command_raw.get("where")
        if isinstance(where_raw, dict):
            where_raw_dict = cast(dict[str, Any], where_raw)
            where = [{str(key): str(value) for key, value in where_raw_dict.items()}]

        return OptimizeCommand(
            enabled=optimize_command_raw.get("enabled", False),
            where=where,
            zorder_by=optimize_command_raw.get("zorder_by") or [],
        )

    @staticmethod
    def __parse_custom_selection(
        custom_selection_raw: dict[str, Any],
    ) -> CustomSelection:
        return CustomSelection(
            enabled=custom_selection_raw.get("enabled", False),
            sql_file=custom_selection_raw.get("sql_file"),
        )

    @staticmethod
    def __parse_enforce_schema(enforce_schema_raw: dict[str, Any]) -> EnforceSchema:
        fields_raw: list[Any] = enforce_schema_raw.get("fields") or []

        fields = [
            SchemaField(
                name=cast(dict[str, Any], field_raw)["name"],
                type=cast(dict[str, Any], field_raw)["type"],
                nullable=cast(dict[str, Any], field_raw).get("nullable", True),
                metadata=cast(dict[str, Any], field_raw).get("metadata") or {},
            )
            for field_raw in fields_raw
            if isinstance(field_raw, dict)
        ]

        return EnforceSchema(
            type=enforce_schema_raw["type"],
            fields=fields,
        )

    def __read_yaml(self, file_path: StoragePath) -> dict[str, Any]:
        """Read a YAML file and return its contents."""
        path = Path(file_path.uri)

        with path.open("r", encoding="utf-8") as file:
            data: dict[str, Any] = yaml.safe_load(file) or {}

        return data
