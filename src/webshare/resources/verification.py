"""The account verification (compliance) resource (`client.verification`).

Nested subresources: ``flows``, ``questions``, ``appeals``, ``abuse_reports``,
plus singleton getters for suspension, categories, limits and thresholds.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Literal

from webshare._http import FileInput, RequestSpec, buffer_files, drop_json_nulls
from webshare._pagination import AsyncPage, SyncPage
from webshare._requester import AsyncRequester, AsyncResource, SyncRequester, SyncResource
from webshare.types.account import (
    AbuseReport,
    Suspension,
    VerificationAnswer,
    VerificationAppeal,
    VerificationCategory,
    VerificationFlow,
    VerificationLimits,
    VerificationQuestion,
    VerificationThreshold,
)

FlowType = Literal["acceptable_use_violation", "abuse_report", "fraudulent_payment"]
FlowState = Literal["inflow", "successful_verification", "failed_verification"]
AppealState = Literal["approved", "rejected", "submitted"]


def _flows_list_spec(*, page: int | None, page_size: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/verification/flow/",
        query={"page": page, "page_size": page_size},
    )


def _flows_get_spec(id: int) -> RequestSpec:
    return RequestSpec(method="GET", path=f"/api/v2/verification/flow/{id}/")


def _submit_evidence_spec(
    id: int, *, explanation: str | None, files: Sequence[FileInput] | None
) -> RequestSpec:
    data: dict[str, str] = {}
    if explanation is not None:
        data["explanation"] = explanation
    return RequestSpec(
        method="POST",
        path=f"/api/v2/verification/flow/{id}/submit_evidence/",
        multipart_data=data,
        # Buffered here so retried attempts re-send the same bytes.
        multipart_files=buffer_files(files) if files is not None else None,
    )


def _submit_security_code_spec(id: int, *, security_code: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/api/v2/verification/flow/{id}/submit_verification_code/",
        json_body={"security_code": security_code},
    )


def _questions_list_spec(
    *,
    flow__type: FlowType | None,
    flow__state: FlowState | None,
    answer__isnull: bool | None,
    flow__started_at__gte: str | datetime | None,
    flow__started_at__lte: str | datetime | None,
    question: str | None,
    answer__answer: str | None,
    page: int | None,
    page_size: int | None,
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/verification/question/",
        query={
            "flow__type": flow__type,
            "flow__state": flow__state,
            "answer__isnull": answer__isnull,
            "flow__started_at__gte": flow__started_at__gte,
            "flow__started_at__lte": flow__started_at__lte,
            "question": question,
            "answer__answer": answer__answer,
            "page": page,
            "page_size": page_size,
        },
    )


def _submit_answer_spec(
    question_id: int, *, answer: str, files: Sequence[FileInput] | None
) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path=f"/api/v2/verification/question/{question_id}/answer/",
        multipart_data={"answer": answer},
        # Buffered here so retried attempts re-send the same bytes.
        multipart_files=buffer_files(files) if files is not None else None,
    )


def _appeals_list_spec(
    *, state: AppealState | None, page: int | None, page_size: int | None
) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/verification/appeal/",
        query={"state": state, "page": page, "page_size": page_size},
    )


def _appeals_create_spec(*, appeal: str) -> RequestSpec:
    return RequestSpec(
        method="POST",
        path="/api/v2/verification/appeal/",
        json_body=drop_json_nulls({"appeal": appeal}),
    )


def _abuse_reports_list_spec(*, page: int | None, page_size: int | None) -> RequestSpec:
    return RequestSpec(
        method="GET",
        path="/api/v2/verification/abuse_report/",
        query={"page": page, "page_size": page_size},
    )


def _suspension_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/verification/suspension/")


def _categories_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/verification/categories/")


def _limits_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/verification/limits/")


def _thresholds_spec() -> RequestSpec:
    return RequestSpec(method="GET", path="/api/v2/verification/thresholds/")


class VerificationFlows(SyncResource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[VerificationFlow]:
        """List account verification flows."""
        return self._client.request_page(
            _flows_list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )

    def get(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationFlow:
        """Get a verification flow."""
        return self._client.request_model(
            _flows_get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )

    def submit_evidence(
        self,
        id: int,
        *,
        explanation: str | None = None,
        files: Sequence[FileInput] | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationFlow:
        """Submit evidence for a verification flow (multipart/form-data).

        ``files`` accepts file paths, bytes, binary file objects or
        ``(filename, content)`` tuples.
        """
        return self._client.request_model(
            _submit_evidence_spec(id, explanation=explanation, files=files).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )

    def submit_security_code(
        self,
        id: int,
        *,
        security_code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationFlow:
        """Submit the two-character security code from the bank statement
        (fraudulent-payment flows)."""
        return self._client.request_model(
            _submit_security_code_spec(id, security_code=security_code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )


class VerificationQuestions(SyncResource):
    def list(
        self,
        *,
        flow__type: FlowType | None = None,
        flow__state: FlowState | None = None,
        answer__isnull: bool | None = None,
        flow__started_at__gte: str | datetime | None = None,
        flow__started_at__lte: str | datetime | None = None,
        question: str | None = None,
        answer__answer: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[VerificationQuestion]:
        """List questions submitted by the compliance team."""
        return self._client.request_page(
            _questions_list_spec(
                flow__type=flow__type,
                flow__state=flow__state,
                answer__isnull=answer__isnull,
                flow__started_at__gte=flow__started_at__gte,
                flow__started_at__lte=flow__started_at__lte,
                question=question,
                answer__answer=answer__answer,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            VerificationQuestion,
        )

    def submit_answer(
        self,
        question_id: int,
        *,
        answer: str,
        files: Sequence[FileInput] | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationAnswer:
        """Submit an answer with optional attachments (multipart/form-data)."""
        return self._client.request_model(
            _submit_answer_spec(question_id, answer=answer, files=files).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationAnswer,
        )


class VerificationAppeals(SyncResource):
    def list(
        self,
        *,
        state: AppealState | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[VerificationAppeal]:
        """List suspension appeals."""
        return self._client.request_page(
            _appeals_list_spec(state=state, page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationAppeal,
        )

    def create(
        self,
        *,
        appeal: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationAppeal:
        """Submit an appeal for an account suspension (one at a time)."""
        return self._client.request_model(
            _appeals_create_spec(appeal=appeal).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationAppeal,
        )


class VerificationAbuseReports(SyncResource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> SyncPage[AbuseReport]:
        """List abuse reports raised against the account."""
        return self._client.request_page(
            _abuse_reports_list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            AbuseReport,
        )


class Verification(SyncResource):
    def __init__(self, client: SyncRequester) -> None:
        super().__init__(client)
        self.flows = VerificationFlows(client)
        self.questions = VerificationQuestions(client)
        self.appeals = VerificationAppeals(client)
        self.abuse_reports = VerificationAbuseReports(client)

    def get_suspension(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Suspension:
        """Get suspension details. Works even while the account is suspended."""
        return self._client.request_model(
            _suspension_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Suspension,
        )

    def get_categories(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> dict[str, VerificationCategory]:
        """Get verification categories, keyed by category name."""
        return self._client.request_model_dict(
            _categories_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationCategory,
        )

    def get_limits(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationLimits:
        """Get the verification limits currently applied to the account."""
        return self._client.request_model(
            _limits_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationLimits,
        )

    def get_thresholds(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> dict[str, VerificationThreshold]:
        """Get verification thresholds, keyed by category name."""
        return self._client.request_model_dict(
            _thresholds_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationThreshold,
        )


class AsyncVerificationFlows(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[VerificationFlow]:
        """List account verification flows."""
        return await self._client.request_page(
            _flows_list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )

    async def get(
        self,
        id: int,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationFlow:
        """Get a verification flow."""
        return await self._client.request_model(
            _flows_get_spec(id).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )

    async def submit_evidence(
        self,
        id: int,
        *,
        explanation: str | None = None,
        files: Sequence[FileInput] | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationFlow:
        """Submit evidence for a verification flow (multipart/form-data)."""
        return await self._client.request_model(
            _submit_evidence_spec(id, explanation=explanation, files=files).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )

    async def submit_security_code(
        self,
        id: int,
        *,
        security_code: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationFlow:
        """Submit the two-character security code from the bank statement."""
        return await self._client.request_model(
            _submit_security_code_spec(id, security_code=security_code).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationFlow,
        )


class AsyncVerificationQuestions(AsyncResource):
    async def list(
        self,
        *,
        flow__type: FlowType | None = None,
        flow__state: FlowState | None = None,
        answer__isnull: bool | None = None,
        flow__started_at__gte: str | datetime | None = None,
        flow__started_at__lte: str | datetime | None = None,
        question: str | None = None,
        answer__answer: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[VerificationQuestion]:
        """List questions submitted by the compliance team."""
        return await self._client.request_page(
            _questions_list_spec(
                flow__type=flow__type,
                flow__state=flow__state,
                answer__isnull=answer__isnull,
                flow__started_at__gte=flow__started_at__gte,
                flow__started_at__lte=flow__started_at__lte,
                question=question,
                answer__answer=answer__answer,
                page=page,
                page_size=page_size,
            ).with_options(timeout, headers, max_retries, subuser_id, federated_user_id),
            VerificationQuestion,
        )

    async def submit_answer(
        self,
        question_id: int,
        *,
        answer: str,
        files: Sequence[FileInput] | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationAnswer:
        """Submit an answer with optional attachments (multipart/form-data)."""
        return await self._client.request_model(
            _submit_answer_spec(question_id, answer=answer, files=files).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationAnswer,
        )


class AsyncVerificationAppeals(AsyncResource):
    async def list(
        self,
        *,
        state: AppealState | None = None,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[VerificationAppeal]:
        """List suspension appeals."""
        return await self._client.request_page(
            _appeals_list_spec(state=state, page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationAppeal,
        )

    async def create(
        self,
        *,
        appeal: str,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationAppeal:
        """Submit an appeal for an account suspension (one at a time)."""
        return await self._client.request_model(
            _appeals_create_spec(appeal=appeal).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationAppeal,
        )


class AsyncVerificationAbuseReports(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> AsyncPage[AbuseReport]:
        """List abuse reports raised against the account."""
        return await self._client.request_page(
            _abuse_reports_list_spec(page=page, page_size=page_size).with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            AbuseReport,
        )


class AsyncVerification(AsyncResource):
    def __init__(self, client: AsyncRequester) -> None:
        super().__init__(client)
        self.flows = AsyncVerificationFlows(client)
        self.questions = AsyncVerificationQuestions(client)
        self.appeals = AsyncVerificationAppeals(client)
        self.abuse_reports = AsyncVerificationAbuseReports(client)

    async def get_suspension(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> Suspension:
        """Get suspension details. Works even while the account is suspended."""
        return await self._client.request_model(
            _suspension_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            Suspension,
        )

    async def get_categories(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> dict[str, VerificationCategory]:
        """Get verification categories, keyed by category name."""
        return await self._client.request_model_dict(
            _categories_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationCategory,
        )

    async def get_limits(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> VerificationLimits:
        """Get the verification limits currently applied to the account."""
        return await self._client.request_model(
            _limits_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationLimits,
        )

    async def get_thresholds(
        self,
        *,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        max_retries: int | None = None,
        subuser_id: int | str | None = None,
        federated_user_id: int | str | None = None,
    ) -> dict[str, VerificationThreshold]:
        """Get verification thresholds, keyed by category name."""
        return await self._client.request_model_dict(
            _thresholds_spec().with_options(
                timeout, headers, max_retries, subuser_id, federated_user_id
            ),
            VerificationThreshold,
        )
