"""Google Sheets task-row mapping with injected native read/write callbacks.

The runtime owns Google authentication and translates ``NativeSheetMutation``
objects into Sheets ``batchUpdate`` requests.  This module owns only the
deterministic row contract: canonical-ID lookup, field ownership, minimum
patches, and verified readback.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from .tasks import TaskError


MANAGED_BY_VALUE = "school-os"
PROVIDER_OBJECT_PREFIX = "sheets:canonical:"


@dataclass(frozen=True)
class SheetScope:
    """Already-authorized private spreadsheet/sheet selection.

    ``scope_id`` is opaque to the adapter.  A runtime may use it to carry the
    private spreadsheet identity, sheet title, bounded range, or all three.
    """

    scope_id: str


@dataclass(frozen=True)
class SheetColumns:
    """The fixed headers required by the Google Sheets task projection."""

    managed_by: str = "Managed By"
    canonical_task_id: str = "Canonical Task ID"
    task_origin: str = "Task Origin"
    action: str = "Action"
    task_context: str = "Task Context"
    source_link: str = "Source Link"
    group: str = "Group"
    workflow_state: str = "Workflow State"
    status: str = "Status"
    source_due: str = "Source Due"
    parent_planned_due: str = "Parent Planned Due"
    parent_progress: str = "Parent Progress"
    completion_comment: str = "Completion Comment"

    @property
    def system_managed(self) -> tuple[str, ...]:
        return (
            self.managed_by,
            self.canonical_task_id,
            self.task_origin,
            self.task_context,
            self.source_link,
            self.workflow_state,
            self.source_due,
        )

    @property
    def parent_editable(self) -> tuple[str, ...]:
        return (
            self.action,
            self.group,
            self.parent_planned_due,
            self.parent_progress,
            self.completion_comment,
        )

    @property
    def provider_owned(self) -> tuple[str, ...]:
        return (self.status,)


@dataclass(frozen=True)
class SheetRow:
    """One normalized row from a bounded Sheet snapshot."""

    row_id: str
    cells: Mapping[str, str | None]


@dataclass(frozen=True)
class SheetSnapshot:
    """A complete, bounded snapshot of one configured task Sheet scope."""

    scope: SheetScope
    rows: tuple[SheetRow, ...]
    complete: bool


@dataclass(frozen=True)
class NativeSheetMutation:
    """A runtime-ready row mutation using safe explicit string cell inputs.

    The runtime maps header keys to the configured column indexes and uses each
    payload as ``userEnteredValue.stringValue``.  Formula-looking text therefore
    remains literal text rather than becoming a Sheet formula.
    """

    kind: str
    scope: SheetScope
    row_id: str | None
    values: Mapping[str, str]
    expected_canonical_task_id: str | None = None
    expected_managed_by: str | None = None
    expected_cells: Mapping[str, str | None] = field(default_factory=dict)

    def native_cells(self) -> dict[str, dict[str, dict[str, str]]]:
        return {
            column: {"userEnteredValue": {"stringValue": value}}
            for column, value in self.values.items()
        }

    def guard_cells(self, columns: SheetColumns) -> dict[str, str | None]:
        """Return the observed identity cells a mutable-row write must match.

        A Sheet row location is only a locator.  For a patch or claim, the
        native bridge must resolve that locator immediately before writing and
        require these values to match.  An append has no pre-existing row to
        guard and is instead established by exact readback.
        """

        if self.row_id is None:
            return {}
        return {
            columns.managed_by: self.expected_managed_by,
            columns.canonical_task_id: self.expected_canonical_task_id,
            **dict(self.expected_cells),
        }


@dataclass(frozen=True)
class UnboundParentCandidate:
    """A visible, untouched parent row that core may admit by guarded claim."""

    row_id: str
    action: str
    group: str | None
    status: str | None
    parent_planned_due: str | None
    parent_progress: str | None
    completion_comment: str | None
    expected_cells: Mapping[str, str | None]


class GoogleSheetsRowsPort(Protocol):
    """Injected provider bridge; implementations make the actual API calls.

    ``apply_mutation`` must re-resolve a non-append ``row_id`` immediately
    before its native write and compare ``mutation.guard_cells(columns)``.  A
    mismatch is a blocked operation, not a best-effort write.  Google Sheets
    does not offer an asserted row-version compare-and-swap through this
    contract, so the selected runtime must also enforce its admitted
    single-writer scope or block when that guarantee is unavailable.
    """

    def read_complete(self, scope: SheetScope) -> SheetSnapshot: ...

    def apply_mutation(self, mutation: NativeSheetMutation) -> str: ...

    def read_exact(self, scope: SheetScope, row_id: str) -> SheetRow | None: ...


class GoogleSheetsCommentsPort(Protocol):
    """Optional native-comment bridge when the selected surface supports it."""

    def list_comments(self, scope: SheetScope, row_id: str, effect_id: str) -> Sequence[Mapping[str, Any]]: ...

    def write_comment(self, scope: SheetScope, row_id: str, effect_id: str, text: str) -> Mapping[str, Any]: ...


def normalized_snapshot(
    scope: SheetScope, rows: Sequence[Mapping[str, Any]], *, complete: bool
) -> SheetSnapshot:
    """Build a normalized snapshot from runtime-extracted CellData/range rows.

    Runtime extraction provides the current opaque row locator and only scalar
    displayed/user-entered cell strings.  Google Sheets row locations are
    mutable locators, never task identity; guarded writes re-check canonical
    identity before using them.  Formula evaluation and native API response
    parsing intentionally remain at the connector boundary.
    """

    normalized: list[SheetRow] = []
    for raw in rows:
        row_id = raw.get("row_id")
        cells = raw.get("cells")
        if not isinstance(row_id, str) or not row_id:
            raise TaskError("Sheet snapshot row is missing a row locator")
        if not isinstance(cells, Mapping):
            raise TaskError("Sheet snapshot row is missing normalized cells")
        values: dict[str, str | None] = {}
        for name, value in cells.items():
            if not isinstance(name, str):
                raise TaskError("Sheet column names must be strings")
            if value is not None and not isinstance(value, str):
                raise TaskError("Sheet cell values must be strings or null")
            values[name] = value
        normalized.append(SheetRow(row_id=row_id, cells=values))
    return SheetSnapshot(scope=scope, rows=tuple(normalized), complete=complete)


class GoogleSheetsTaskAdapter:
    """Create isolated, complete-snapshot task sync sessions for one scope.

    The adapter itself deliberately holds no provider snapshot.  Runtime code
    calls :meth:`begin_sync` once for a reconciliation and passes that returned
    session to the generic task reconciler.  A later reconciliation must start
    another session and therefore observes a new complete native snapshot.
    """

    def __init__(
        self,
        scope: SheetScope,
        rows: GoogleSheetsRowsPort,
        *,
        columns: SheetColumns = SheetColumns(),
        comments: GoogleSheetsCommentsPort | None = None,
    ) -> None:
        self.scope = scope
        self.rows = rows
        self.columns = columns
        self.comments = comments

    def begin_sync(self) -> GoogleSheetsTaskSync:
        return GoogleSheetsTaskSync(
            self.scope, self.rows, columns=self.columns, comments=self.comments
        )


class GoogleSheetsTaskSync:
    """Map one verified complete Sheet snapshot to task-provider operations."""

    def __init__(
        self,
        scope: SheetScope,
        rows: GoogleSheetsRowsPort,
        *,
        columns: SheetColumns = SheetColumns(),
        comments: GoogleSheetsCommentsPort | None = None,
    ) -> None:
        self.scope = scope
        self.rows = rows
        self.columns = columns
        self.comments = comments
        self._managed_by_canonical: dict[str, SheetRow] | None = None
        self._unbound_by_row_id: dict[str, SheetRow] | None = None

    def list_tasks(self) -> list[dict[str, Any]]:
        return [self._provider_task(row) for row in self._managed_rows()]

    def create_task(self, candidate: Mapping[str, Any]) -> dict[str, Any]:
        projection = self._projection(candidate)
        if self._find_managed_row(projection["canonical_task_id"]) is not None:
            raise TaskError("canonical task ID already has a Sheet row")
        values = {
            self.columns.managed_by: MANAGED_BY_VALUE,
            self.columns.canonical_task_id: projection["canonical_task_id"],
            self.columns.task_origin: projection["origin"],
            self.columns.action: projection["title"],
            self.columns.task_context: projection["description"],
            self.columns.source_link: projection["source_link"],
            self.columns.group: projection["group"],
            self.columns.workflow_state: projection["workflow_state"],
            self.columns.source_due: projection["source_due"],
        }
        row_id = self._apply_mutation(
            NativeSheetMutation(
                "append",
                self.scope,
                None,
                values,
                expected_canonical_task_id=projection["canonical_task_id"],
                expected_managed_by=MANAGED_BY_VALUE,
            )
        )
        return self._verified_projection(row_id, projection)

    def read_task(self, provider_object_id: str) -> dict[str, Any] | None:
        canonical_id = self._canonical_from_object_id(provider_object_id)
        row = self._find_managed_row(canonical_id)
        if row is None:
            return None
        exact = self.rows.read_exact(self.scope, row.row_id)
        if exact is None:
            self._invalidate_snapshot()
            return None
        task = self._provider_task(exact)
        if task["canonical_task_id"] != canonical_id:
            self._invalidate_snapshot()
            raise TaskError("Sheet exact-row readback resolved a different canonical task")
        self._replace_verified_row(exact)
        return task

    def apply_patch(self, provider_object_id: str, patch: Mapping[str, Any]) -> dict[str, Any]:
        canonical_id = self._canonical_from_object_id(provider_object_id)
        current = self._find_managed_row(canonical_id)
        if current is None:
            raise TaskError("cannot patch an absent Sheet task row")
        proposed = self._projection({**self._provider_task(current), **dict(patch)})
        if proposed["canonical_task_id"] != canonical_id:
            raise TaskError("canonical task ID cannot be changed through a Sheet patch")
        changes = self._changed_cells(current, proposed)
        if changes:
            row_id = self._apply_mutation(
                NativeSheetMutation(
                    "patch",
                    self.scope,
                    current.row_id,
                    changes,
                    expected_canonical_task_id=canonical_id,
                    expected_managed_by=MANAGED_BY_VALUE,
                )
            )
        else:
            row_id = current.row_id
        return self._verified_projection(row_id, proposed)

    def find_comments(self, provider_object_id: str, effect_id: str) -> list[dict[str, Any]]:
        row = self._required_row(provider_object_id)
        if self.comments is None:
            raise TaskError("selected Sheets surface does not provide comment operations")
        return [dict(comment) for comment in self.comments.list_comments(self.scope, row.row_id, effect_id)]

    def write_comment(self, provider_object_id: str, effect_id: str, text: str) -> dict[str, Any]:
        row = self._required_row(provider_object_id)
        if self.comments is None:
            raise TaskError("selected Sheets surface does not provide comment operations")
        written = dict(self.comments.write_comment(self.scope, row.row_id, effect_id, text))
        matches = self.find_comments(provider_object_id, effect_id)
        if len(matches) != 1 or matches[0] != written:
            raise TaskError("Sheet comment readback does not establish one immutable effect")
        return written

    def parent_observations(self) -> list[dict[str, str | None]]:
        """Return non-canonical parent fields without treating them as source truth."""

        observations: list[dict[str, str | None]] = []
        for row in self._managed_rows():
            task = self._provider_task(row)
            observations.append(
                {
                    "canonical_task_id": task["canonical_task_id"],
                    "status": task["status"],
                    "parent_planned_due": task["parent_planned_due"],
                    "parent_progress": task["parent_progress"],
                    "completion_comment": task["completion_comment"],
                }
            )
        return observations

    def unbound_parent_candidates(self) -> list[UnboundParentCandidate]:
        """Expose deliberate parent rows for core admission without title match.

        The returned packet carries the exact cells that a later guarded claim
        must still observe.  It is not a canonical task and must not be bound
        until core has journaled a parent-origin canonical task ID.
        """

        self._ensure_snapshot_index()
        assert self._unbound_by_row_id is not None
        candidates: list[UnboundParentCandidate] = []
        for row in self._unbound_by_row_id.values():
            action = self._required_parent_text(
                row.cells.get(self.columns.action), self.columns.action
            )
            candidates.append(
                UnboundParentCandidate(
                    row_id=row.row_id,
                    action=action,
                    group=self._optional_text(row.cells.get(self.columns.group)),
                    status=self._optional_text(row.cells.get(self.columns.status)),
                    parent_planned_due=self._optional_text(
                        row.cells.get(self.columns.parent_planned_due)
                    ),
                    parent_progress=self._optional_text(
                        row.cells.get(self.columns.parent_progress)
                    ),
                    completion_comment=self._optional_text(
                        row.cells.get(self.columns.completion_comment)
                    ),
                    expected_cells=dict(row.cells),
                )
            )
        return candidates

    def claim_parent_candidate(
        self,
        candidate: UnboundParentCandidate,
        *,
        canonical_task_id: str,
        workflow_state: str,
    ) -> dict[str, Any]:
        """Mark one core-admitted parent row with its already-journaled ID.

        This cannot create or infer canonical state.  It only marks the exact
        unbound packet supplied by core, preserving the row's Action, Group,
        status, dates, progress, comments, and unrelated cells.
        """

        if not canonical_task_id:
            raise TaskError("claimed parent Sheet row needs a canonical task ID")
        if workflow_state not in {"needs_action", "waiting_external", "needs_review"}:
            raise TaskError("claimed parent Sheet row has an invalid workflow state")
        self._ensure_snapshot_index()
        assert self._unbound_by_row_id is not None
        current = self._unbound_by_row_id.get(candidate.row_id)
        if current is None or dict(current.cells) != dict(candidate.expected_cells):
            raise TaskError("parent Sheet candidate changed before guarded claim")
        if self._find_managed_row(canonical_task_id) is not None:
            raise TaskError("canonical task ID already has a Sheet row")
        action = self._required_parent_text(
            current.cells.get(self.columns.action), self.columns.action
        )
        group = self._required_parent_text(
            current.cells.get(self.columns.group), self.columns.group
        )
        projection = self._projection(
            {
                "canonical_task_id": canonical_task_id,
                "title": action,
                "description": "",
                "group": group,
                "workflow_state": workflow_state,
                "source_link": "",
                "source_due": "",
                "origin": "parent",
            }
        )
        values = {
            self.columns.managed_by: MANAGED_BY_VALUE,
            self.columns.canonical_task_id: canonical_task_id,
            self.columns.task_origin: "parent",
            self.columns.task_context: "",
            self.columns.source_link: "",
            self.columns.workflow_state: workflow_state,
            self.columns.source_due: "",
        }
        row_id = self._apply_mutation(
            NativeSheetMutation(
                "claim",
                self.scope,
                current.row_id,
                values,
                expected_canonical_task_id=None,
                expected_managed_by=None,
                expected_cells=dict(candidate.expected_cells),
            )
        )
        return self._verified_projection(row_id, projection)

    def verify_expected_system_fields(
        self, expected_projections: Mapping[str, Mapping[str, str]]
    ) -> None:
        """Fail closed on unplanned managed-field drift before a runtime writes.

        The runtime derives this expectation from its verified binding state
        after excluding fields that the canonical reconciliation has explicitly
        planned to change.  Parent/provider-owned cells are intentionally not
        compared here.
        """

        for canonical_id, expected in expected_projections.items():
            row = self._find_managed_row(canonical_id)
            if row is None:
                raise TaskError("expected canonical Sheet row is absent")
            actual = self._provider_task(row)
            for field in ("canonical_task_id", "description", "source_link", "workflow_state"):
                if field in expected and actual[field] != expected[field]:
                    raise TaskError("unexpected system-managed Sheet field drift")

    def apply_parent_state(
        self,
        provider_object_id: str,
        *,
        status: str | None = None,
        parent_planned_due: str | None = None,
        parent_progress: str | None = None,
        completion_comment: str | None = None,
    ) -> dict[str, Any]:
        """Apply a policy-authorized provider/parent state change and read it back.

        ``None`` means leave a field untouched; an empty string is an explicit
        clear.  The core completion policy decides whether a completed status
        with no qualifying freeform comment must instead be reopened/reviewed.
        This adapter neither infers completion from silence nor manufactures a
        comment.
        """

        row = self._required_row(provider_object_id)
        requested = {
            self.columns.status: status,
            self.columns.parent_planned_due: parent_planned_due,
            self.columns.parent_progress: parent_progress,
            self.columns.completion_comment: completion_comment,
        }
        changes: dict[str, str] = {}
        for column, value in requested.items():
            if value is None:
                continue
            if not isinstance(value, str):
                raise TaskError("Sheet parent state values must be strings or null")
            if row.cells.get(column) != value:
                changes[column] = value
        row_id = row.row_id
        if changes:
            row_id = self._apply_mutation(
                NativeSheetMutation(
                    "patch",
                    self.scope,
                    row.row_id,
                    changes,
                    expected_canonical_task_id=self._canonical_from_object_id(provider_object_id),
                    expected_managed_by=MANAGED_BY_VALUE,
                )
            )
        exact = self.rows.read_exact(self.scope, row_id)
        if exact is None:
            self._invalidate_snapshot()
            raise TaskError("Sheet parent-state readback is unavailable")
        actual = self._provider_task(exact)
        canonical_id = self._canonical_from_object_id(provider_object_id)
        if actual["canonical_task_id"] != canonical_id:
            self._invalidate_snapshot()
            raise TaskError("Sheet parent-state readback resolved a different canonical task")
        expected = {
            "status": status,
            "parent_planned_due": parent_planned_due,
            "parent_progress": parent_progress,
            "completion_comment": completion_comment,
        }
        if any(value is not None and actual[key] != value for key, value in expected.items()):
            self._invalidate_snapshot()
            raise TaskError("Sheet parent-state readback does not match requested values")
        self._replace_verified_row(exact)
        return actual

    def _complete_snapshot(self) -> SheetSnapshot:
        snapshot = self.rows.read_complete(self.scope)
        if snapshot.scope != self.scope:
            raise TaskError("Sheet provider returned a snapshot for a different scope")
        if not snapshot.complete:
            raise TaskError("Sheet task snapshot is incomplete")
        return snapshot

    def _apply_mutation(self, mutation: NativeSheetMutation) -> str:
        """Apply one native request, dropping this index on any unknown result."""

        try:
            return self.rows.apply_mutation(mutation)
        except Exception:
            # A guard failure, transport failure, or unknown provider outcome
            # makes this in-sync row-location index unsafe for another write.
            self._invalidate_snapshot()
            raise

    def _managed_rows(self) -> list[SheetRow]:
        self._ensure_snapshot_index()
        assert self._managed_by_canonical is not None
        return list(self._managed_by_canonical.values())

    def _ensure_snapshot_index(self) -> None:
        """Load and validate one complete snapshot for this explicit sync."""

        if self._managed_by_canonical is not None:
            return
        managed: dict[str, SheetRow] = {}
        unbound: dict[str, SheetRow] = {}
        seen: set[str] = set()
        for row in self._complete_snapshot().rows:
            marker = row.cells.get(self.columns.managed_by)
            canonical_id = row.cells.get(self.columns.canonical_task_id)
            if marker in (None, ""):
                if canonical_id not in (None, ""):
                    raise TaskError("Sheet row has a canonical task ID without the system marker")
                if self._optional_text(row.cells.get(self.columns.action)):
                    unbound[row.row_id] = row
                continue
            if marker != MANAGED_BY_VALUE:
                raise TaskError("Sheet row has an unknown system marker")
            if not canonical_id:
                raise TaskError("system-managed Sheet row is missing canonical task ID")
            if canonical_id in seen:
                raise TaskError("multiple Sheet rows match one canonical task ID")
            self._provider_task(row)  # validates all managed fields before mutation
            seen.add(canonical_id)
            managed[canonical_id] = row
        self._managed_by_canonical = managed
        self._unbound_by_row_id = unbound

    def _invalidate_snapshot(self) -> None:
        """Forget an in-sync index after observed drift; caller may explicitly reload."""

        self._managed_by_canonical = None
        self._unbound_by_row_id = None

    def reload_after_observed_drift(self) -> None:
        """Explicitly re-read a complete scope after a blocked/observed drift."""

        self._invalidate_snapshot()
        self._ensure_snapshot_index()

    def _replace_verified_row(self, exact: SheetRow) -> None:
        """Advance this sync's index only from an exact verified native read."""

        self._ensure_snapshot_index()
        assert self._managed_by_canonical is not None
        actual = self._provider_task(exact)
        canonical_id = actual["canonical_task_id"]
        existing = self._managed_by_canonical.get(canonical_id)
        if existing is not None and existing.row_id != exact.row_id:
            self._invalidate_snapshot()
            raise TaskError("exact Sheet readback introduced an ambiguous canonical task ID")
        self._managed_by_canonical[canonical_id] = exact
        if self._unbound_by_row_id is not None:
            self._unbound_by_row_id.pop(exact.row_id, None)

    def _find_managed_row(self, canonical_id: str) -> SheetRow | None:
        self._ensure_snapshot_index()
        assert self._managed_by_canonical is not None
        return self._managed_by_canonical.get(canonical_id)

    def _required_row(self, provider_object_id: str) -> SheetRow:
        canonical_id = self._canonical_from_object_id(provider_object_id)
        row = self._find_managed_row(canonical_id)
        if row is None:
            raise TaskError("Sheet task row is absent")
        return row

    def _provider_task(self, row: SheetRow) -> dict[str, Any]:
        cells = row.cells
        if cells.get(self.columns.managed_by) != MANAGED_BY_VALUE:
            raise TaskError("Sheet row is not system managed")
        origin = cells.get(self.columns.task_origin)
        if origin not in {"source", "parent"}:
            raise TaskError("system-managed Sheet row has an invalid Task Origin")
        required = {
            "canonical_task_id": self.columns.canonical_task_id,
            "workflow_state": self.columns.workflow_state,
        }
        values: dict[str, str] = {}
        for name, column in required.items():
            value = cells.get(column)
            if not isinstance(value, str) or not value:
                raise TaskError(f"system-managed Sheet row is missing {column}")
            values[name] = value
        description = self._optional_text(cells.get(self.columns.task_context))
        source_link = self._optional_text(cells.get(self.columns.source_link))
        if origin == "source" and (not description or not source_link):
            raise TaskError("source-managed Sheet row is missing source context or link")
        return {
            "provider_object_id": PROVIDER_OBJECT_PREFIX + values["canonical_task_id"],
            "canonical_task_id": values["canonical_task_id"],
            "origin": origin,
            "title": self._required_parent_text(cells.get(self.columns.action), self.columns.action),
            "description": description or "",
            "group": self._required_parent_text(cells.get(self.columns.group), self.columns.group),
            "workflow_state": values["workflow_state"],
            "source_link": source_link or "",
            "status": self._optional_text(cells.get(self.columns.status)),
            "source_due": self._optional_text(cells.get(self.columns.source_due)),
            "parent_planned_due": self._optional_text(cells.get(self.columns.parent_planned_due)),
            "parent_progress": self._optional_text(cells.get(self.columns.parent_progress)),
            "completion_comment": self._optional_text(cells.get(self.columns.completion_comment)),
        }

    def _projection(self, value: Mapping[str, Any]) -> dict[str, str]:
        allowed = {
            "canonical_task_id",
            "origin",
            "title",
            "description",
            "group",
            "workflow_state",
            "source_link",
            "source_due",
        }
        unexpected = set(value) - (allowed | {"provider_object_id", "status", "parent_planned_due", "parent_progress", "completion_comment"})
        if unexpected:
            raise TaskError("Sheet task patch contains unsupported fields: " + ", ".join(sorted(unexpected)))
        projection: dict[str, str] = {}
        origin = value.get("origin", "source")
        if origin not in {"source", "parent"}:
            raise TaskError("Sheet task projection has an invalid origin")
        projection["origin"] = origin
        for field in allowed - {"origin"}:
            item = value.get(field, "" if field == "source_due" else None)
            required = field not in {"description", "source_link", "source_due"} or origin == "source" and field in {"description", "source_link"}
            if not isinstance(item, str) or (required and not item):
                raise TaskError(f"Sheet task projection is missing {field}")
            projection[field] = item
        return projection

    def _changed_cells(self, current: SheetRow, projection: Mapping[str, str]) -> dict[str, str]:
        mapped = {
            self.columns.canonical_task_id: projection["canonical_task_id"],
            self.columns.task_origin: projection["origin"],
            self.columns.action: projection["title"],
            self.columns.task_context: projection["description"],
            self.columns.group: projection["group"],
            self.columns.workflow_state: projection["workflow_state"],
            self.columns.source_link: projection["source_link"],
            self.columns.source_due: projection["source_due"],
        }
        return {
            column: value for column, value in mapped.items()
            if current.cells.get(column) != value
        }

    def _verified_projection(self, row_id: str, projection: Mapping[str, str]) -> dict[str, Any]:
        exact = self.rows.read_exact(self.scope, row_id)
        if exact is None:
            self._invalidate_snapshot()
            raise TaskError("Sheet exact-row readback is unavailable")
        actual = self._provider_task(exact)
        if any(actual.get(field) != value for field, value in projection.items()):
            self._invalidate_snapshot()
            raise TaskError("Sheet exact-row readback does not match managed projection")
        self._replace_verified_row(exact)
        return actual

    @staticmethod
    def _optional_text(value: str | None) -> str | None:
        return value if isinstance(value, str) else None

    @staticmethod
    def _required_parent_text(value: str | None, column: str) -> str:
        if not isinstance(value, str) or not value:
            raise TaskError(f"system-managed Sheet row is missing {column}")
        return value

    @staticmethod
    def _canonical_from_object_id(provider_object_id: str) -> str:
        if not provider_object_id.startswith(PROVIDER_OBJECT_PREFIX):
            raise TaskError("Sheet provider object ID is not a canonical-ID binding")
        canonical_id = provider_object_id.removeprefix(PROVIDER_OBJECT_PREFIX)
        if not canonical_id:
            raise TaskError("Sheet provider object ID omits canonical task ID")
        return canonical_id
