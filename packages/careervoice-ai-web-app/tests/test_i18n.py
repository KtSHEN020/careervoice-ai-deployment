import pytest

from careervoice_ai_web_app.i18n import (
    DEFAULT_LANGUAGE,
    LANGUAGE_STATE_KEY,
    TRANSLATIONS,
    AppLanguage,
    get_app_language,
    parse_app_language,
    set_app_language,
    translate,
)


def test_default_language_is_english() -> None:
    assert (
        get_app_language({})
        is DEFAULT_LANGUAGE
    )

    assert (
        DEFAULT_LANGUAGE
        is AppLanguage.ENGLISH
    )


def test_stored_simplified_chinese_is_loaded() -> None:
    state: dict[str, object] = {
        LANGUAGE_STATE_KEY: "zh-CN",
    }

    assert (
        get_app_language(state)
        is AppLanguage.SIMPLIFIED_CHINESE
    )


def test_invalid_language_falls_back_to_default() -> None:
    state: dict[str, object] = {
        LANGUAGE_STATE_KEY: "invalid",
    }

    assert (
        get_app_language(state)
        is AppLanguage.ENGLISH
    )


def test_language_can_be_stored() -> None:
    state: dict[str, object] = {}

    set_app_language(
        state,
        AppLanguage.SIMPLIFIED_CHINESE,
    )

    assert state == {
        LANGUAGE_STATE_KEY: "zh-CN",
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            "en",
            AppLanguage.ENGLISH,
        ),
        (
            "zh-CN",
            AppLanguage.SIMPLIFIED_CHINESE,
        ),
        (
            AppLanguage.ENGLISH,
            AppLanguage.ENGLISH,
        ),
        (
            None,
            None,
        ),
        (
            "unsupported",
            None,
        ),
    ],
)
def test_parse_app_language(
    value: object,
    expected: AppLanguage | None,
) -> None:
    assert (
        parse_app_language(value)
        is expected
    )


def test_translation_catalogs_have_identical_keys() -> None:
    english_keys = set(
        TRANSLATIONS[
            AppLanguage.ENGLISH
        ]
    )

    chinese_keys = set(
        TRANSLATIONS[
            AppLanguage.SIMPLIFIED_CHINESE
        ]
    )

    assert chinese_keys == english_keys


def test_translation_supports_format_values() -> None:
    assert translate(
        AppLanguage.ENGLISH,
        "quota.used",
        used=7,
        limit=20,
    ) == "7 / 20 AI units used"

    assert translate(
        AppLanguage.SIMPLIFIED_CHINESE,
        "quota.used",
        used=7,
        limit=20,
    ) == "已使用 7 / 20 个 AI 单位"


def test_missing_translation_raises_error() -> None:
    with pytest.raises(
        KeyError,
        match="Missing translation",
    ):
        translate(
            AppLanguage.ENGLISH,
            "does.not.exist",
        )


def test_poor_match_level_is_localized() -> None:
    assert translate(
        AppLanguage.ENGLISH,
        "recommendation.level.poor_match",
    ) == "Poor Match"

    assert translate(
        AppLanguage.SIMPLIFIED_CHINESE,
        "recommendation.level.poor_match",
    ) == "较低匹配"