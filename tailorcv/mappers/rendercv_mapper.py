"""Deterministic mapper from Profile + LLM plan to RenderCV cv dict."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from tailorcv.llm.selection_schema import LlmSelectionPlan
from tailorcv.schema.profile_schema import Profile


def build_cv_dict(profile: Profile, plan: LlmSelectionPlan) -> Dict[str, Any]:
    """
    Build a RenderCV-ready cv dictionary from a profile and selection plan.

    This function is deterministic and assumes the selection plan has already
    been validated. It omits empty fields and sections.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param plan: LLM selection plan describing what to include.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :return: RenderCV-compatible cv dictionary.
    :rtype: dict[str, typing.Any]
    """
    cv: Dict[str, Any] = {}

    _apply_header(cv, profile)

    sections: Dict[str, List[Dict[str, Any]]] = {}

    experience_entries = _map_experience(profile, plan)
    if experience_entries:
        sections["Experience"] = experience_entries

    project_entries = _map_projects(profile, plan)
    if project_entries:
        sections["Projects"] = project_entries

    education_entries = _map_education(profile, plan)
    if education_entries:
        sections["Education"] = education_entries

    skill_entries = _map_skills(profile, plan)
    if skill_entries:
        sections["Skills"] = skill_entries

    ordered_sections = _order_sections(sections, plan.section_order)
    if ordered_sections:
        cv["sections"] = ordered_sections

    return {"cv": cv}


def _apply_header(cv: Dict[str, Any], profile: Profile) -> None:
    """
    Map profile metadata to RenderCV header fields.

    :param cv: RenderCV cv dictionary to mutate.
    :type cv: dict[str, typing.Any]
    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :return: None.
    :rtype: None
    """
    meta = profile.meta
    cv["name"] = meta.name
    _set_if_present(cv, "headline", meta.headline)
    _set_if_present(cv, "location", meta.location)
    _set_if_present(cv, "email", meta.email)
    _set_if_present(cv, "phone", meta.phone)
    _set_if_present(cv, "website", meta.website)

    if meta.socials:
        cv["social_networks"] = [
            {"network": s.network, "username": s.username} for s in meta.socials
        ]


def _map_experience(profile: Profile, plan: LlmSelectionPlan) -> List[Dict[str, Any]]:
    """
    Map experience entries to RenderCV ExperienceEntry dictionaries.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param plan: LLM selection plan.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :return: Experience entry dictionaries.
    :rtype: list[dict[str, typing.Any]]
    """
    entries = _select_items(profile.experience, plan.selected_experience_ids)
    mapped: List[Dict[str, Any]] = []
    for exp in entries:
        item: Dict[str, Any] = {
            "company": exp.company,
            "position": exp.position,
        }
        _set_if_present(item, "location", exp.location)
        _set_if_present(item, "date", exp.date)
        _set_if_present(item, "start_date", exp.start_date)
        _set_if_present(item, "end_date", exp.end_date)
        _set_if_present(item, "summary", exp.summary)

        highlights = _resolve_highlights(exp.id, exp.highlights, plan)
        if highlights:
            item["highlights"] = highlights

        mapped.append(item)
    return mapped


def _map_education(profile: Profile, plan: LlmSelectionPlan) -> List[Dict[str, Any]]:
    """
    Map education entries to RenderCV EducationEntry dictionaries.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param plan: LLM selection plan.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :return: Education entry dictionaries.
    :rtype: list[dict[str, typing.Any]]
    """
    entries = _select_items(profile.education, plan.selected_education_ids)
    mapped: List[Dict[str, Any]] = []
    for edu in entries:
        item: Dict[str, Any] = {
            "institution": edu.institution,
            "area": edu.area,
        }
        _set_if_present(item, "degree", edu.degree)
        _set_if_present(item, "location", edu.location)
        _set_if_present(item, "date", edu.date)
        _set_if_present(item, "start_date", edu.start_date)
        _set_if_present(item, "end_date", edu.end_date)
        _set_if_present(item, "summary", edu.summary)

        highlights = _resolve_highlights(edu.id, edu.highlights, plan)
        if highlights:
            item["highlights"] = highlights

        mapped.append(item)
    return mapped


def _map_projects(profile: Profile, plan: LlmSelectionPlan) -> List[Dict[str, Any]]:
    """
    Map project entries to RenderCV NormalEntry dictionaries.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param plan: LLM selection plan.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :return: Project entry dictionaries.
    :rtype: list[dict[str, typing.Any]]
    """
    entries = _select_items(profile.projects, plan.selected_project_ids)
    mapped: List[Dict[str, Any]] = []
    for proj in entries:
        item: Dict[str, Any] = {
            "name": proj.name,
        }
        _set_if_present(item, "summary", proj.summary)
        _set_if_present(item, "location", proj.location)
        _set_if_present(item, "date", proj.date)
        _set_if_present(item, "start_date", proj.start_date)
        _set_if_present(item, "end_date", proj.end_date)

        highlights = _resolve_highlights(proj.id, proj.highlights, plan)
        if highlights:
            item["highlights"] = highlights

        mapped.append(item)
    return mapped


def _map_skills(profile: Profile, plan: LlmSelectionPlan) -> List[Dict[str, Any]]:
    """
    Map skill entries to RenderCV OneLineEntry dictionaries.

    :param profile: Parsed profile input.
    :type profile: tailorcv.schema.profile_schema.Profile
    :param plan: LLM selection plan.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :return: Skill entry dictionaries.
    :rtype: list[dict[str, typing.Any]]
    """
    selected_labels = set(plan.selected_skill_labels)
    if selected_labels:
        entries = [s for s in profile.skills if s.label in selected_labels]
    else:
        entries = list(profile.skills)

    mapped: List[Dict[str, Any]] = []
    for skill in entries:
        mapped.append({"label": skill.label, "details": skill.details})
    return mapped


def _select_items(items: Iterable[Any], selected_ids: List[str]) -> List[Any]:
    """
    Select items by ID or return all items when selection is empty.

    :param items: Iterable of items with an ``id`` attribute.
    :type items: collections.abc.Iterable[typing.Any]
    :param selected_ids: IDs to include.
    :type selected_ids: list[str]
    :return: Selected items.
    :rtype: list[typing.Any]
    """
    if not selected_ids:
        return list(items)

    selected = set(selected_ids)
    return [item for item in items if item.id in selected]


def _resolve_highlights(
    entry_id: Optional[str],
    highlights: List[str],
    plan: LlmSelectionPlan,
) -> List[str]:
    """
    Resolve highlights using LLM overrides when provided.

    :param entry_id: Entry identifier used for overrides.
    :type entry_id: str | None
    :param highlights: Original highlights from the profile.
    :type highlights: list[str]
    :param plan: LLM selection plan.
    :type plan: tailorcv.llm.selection_schema.LlmSelectionPlan
    :return: Highlights to include.
    :rtype: list[str]
    """
    if entry_id and entry_id in plan.bullet_overrides:
        return list(plan.bullet_overrides[entry_id])
    return list(highlights)


def _order_sections(
    sections: Dict[str, List[Dict[str, Any]]],
    preferred_order: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Order sections based on preferred order and remaining defaults.

    :param sections: Section mapping to order.
    :type sections: dict[str, list[dict[str, typing.Any]]]
    :param preferred_order: Preferred section order from the LLM.
    :type preferred_order: list[str]
    :return: Ordered sections mapping.
    :rtype: dict[str, list[dict[str, typing.Any]]]
    """
    if not preferred_order:
        return sections

    ordered: Dict[str, List[Dict[str, Any]]] = {}
    remaining = {k: v for k, v in sections.items()}

    for title in preferred_order:
        if title in remaining:
            ordered[title] = remaining.pop(title)

    for title, entries in remaining.items():
        ordered[title] = entries

    return ordered


def _set_if_present(target: Dict[str, Any], key: str, value: Any) -> None:
    """
    Set a key only if the value is not None or empty.

    :param target: Dictionary to mutate.
    :type target: dict[str, typing.Any]
    :param key: Key name to set.
    :type key: str
    :param value: Value to set.
    :type value: typing.Any
    :return: None.
    :rtype: None
    """
    if value is None:
        return
    if isinstance(value, list) and not value:
        return
    target[key] = value
