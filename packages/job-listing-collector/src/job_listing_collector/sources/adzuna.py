from __future__ import annotations

from typing import Any

import httpx

from job_listing_collector.sources.base import JobSource, RawJobRecord, SourceError, SourceRequest


class AdzunaSource(JobSource):
    """
    Source adapter for the Adzuna jobs API.

    This adapter collects raw job records from Adzuna and converts each API
    result into the shared RawJobRecord format.
    """

    source_name = "adzuna"

    def __init__(
        self,
        app_id: str,
        app_key: str,
        country: str = "au",
        client: httpx.Client | None = None,
        base_url: str = "https://api.adzuna.com/v1/api",
    ) -> None:
        self.app_id = self._clean_required_value(app_id, "app_id")
        self.app_key = self._clean_required_value(app_key, "app_key")
        self.country = self._clean_required_value(country, "country").lower()
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(timeout=10.0)

    def collect(self, request: SourceRequest) -> list[RawJobRecord]:
        """
        Collect raw jobs from the Adzuna search endpoint.
        """
        response_data = self._get_search_results(request)
        results = response_data.get("results")

        if not isinstance(results, list):
            raise SourceError("Adzuna response did not contain a valid results list.")

        raw_jobs = []

        for result in results:
            raw_job = self._build_raw_job_record(result)

            if raw_job is not None:
                raw_jobs.append(raw_job)

        return raw_jobs

    def _get_search_results(self, request: SourceRequest) -> dict[str, Any]:
        url = f"{self.base_url}/jobs/{self.country}/search/1"
        params: dict[str, str | int] = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": request.max_results,
            "what": request.query,
            "content-type": "application/json",
        }

        if request.location is not None:
            params["where"] = request.location

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as error:
            raise SourceError(
                f"Adzuna request failed with status {error.response.status_code}."
            ) from error
        except httpx.HTTPError as error:
            raise SourceError("Adzuna request failed.") from error
        except ValueError as error:
            raise SourceError("Adzuna response was not valid JSON.") from error

        if not isinstance(data, dict):
            raise SourceError("Adzuna response JSON was not an object.")

        return data

    def _build_raw_job_record(self, result: object) -> RawJobRecord | None:
        if not isinstance(result, dict):
            return None

        source_job_id = self._string_or_empty(result.get("id"))
        source_url = self._string_or_empty(result.get("redirect_url"))

        if not source_job_id or not source_url:
            return None

        title = self._string_or_default(result.get("title"), "Untitled job")
        company = self._extract_company(result)
        location = self._extract_location(result)
        description = self._string_or_default(result.get("description"), title)

        return RawJobRecord(
            source=self.source_name,
            source_job_id=source_job_id,
            title=title,
            company=company,
            location=location,
            description=description,
            source_url=source_url,
            raw_data=result,
        )

    def _extract_company(self, result: dict[str, Any]) -> str:
        company = result.get("company")

        if isinstance(company, dict):
            return self._string_or_default(
                company.get("display_name"),
                "Unknown company",
            )

        return "Unknown company"

    def _extract_location(self, result: dict[str, Any]) -> str:
        location = result.get("location")

        if not isinstance(location, dict):
            return "Unknown location"

        display_name = self._string_or_empty(location.get("display_name"))

        if display_name:
            return display_name

        area = location.get("area")

        if isinstance(area, list):
            area_parts = [str(part).strip() for part in area if str(part).strip()]

            if area_parts:
                return ", ".join(area_parts)

        return "Unknown location"

    def _string_or_default(self, value: object, default: str) -> str:
        cleaned_value = self._string_or_empty(value)

        if cleaned_value:
            return cleaned_value

        return default

    def _string_or_empty(self, value: object) -> str:
        if value is None:
            return ""

        return str(value).strip()

    def _clean_required_value(self, value: str, name: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(f"{name} must not be empty.")

        return cleaned_value