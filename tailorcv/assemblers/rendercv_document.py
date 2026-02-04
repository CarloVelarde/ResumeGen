"""Assemble a full RenderCV document with defaults and overrides."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from tailorcv.defaults.rendercv_defaults import (
    get_default_design,
    get_default_locale,
    get_default_settings,
)


def assemble_rendercv_document(
    cv_dict: Mapping[str, Any],
    *,
    design: Mapping[str, Any] | None = None,
    locale: Mapping[str, Any] | None = None,
    settings: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Assemble a complete RenderCV document with defaults and optional overrides.

    :param cv_dict: RenderCV cv dictionary (expects a top-level ``cv`` key).
    :type cv_dict: collections.abc.Mapping[str, typing.Any]
    :param design: Optional design block override.
    :type design: collections.abc.Mapping[str, typing.Any] | None
    :param locale: Optional locale block override.
    :type locale: collections.abc.Mapping[str, typing.Any] | None
    :param settings: Optional settings block override.
    :type settings: collections.abc.Mapping[str, typing.Any] | None
    :return: Full RenderCV document dictionary.
    :rtype: dict[str, typing.Any]
    """
    document: Dict[str, Any] = {"cv": dict(cv_dict.get("cv", {}))}

    document["design"] = dict(design) if design is not None else get_default_design()
    document["locale"] = dict(locale) if locale is not None else get_default_locale()
    document["settings"] = dict(settings) if settings is not None else get_default_settings()

    return document
