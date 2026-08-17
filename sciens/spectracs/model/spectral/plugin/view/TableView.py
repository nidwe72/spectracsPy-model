from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class TableView(ReportableView):
    """A generic, SELF-DESCRIBING table (SPEC_settled_measurement.md §18.8).

    ⭐⭐ THE FIT IS THE POINT: a `MonitorRecord` is already `columns[{key,label,unit}] + rows[{key: value}]`
    (§15.2), so this view renders ANY plugin's record with no plugin-specific knowledge — the same
    boundary the SDK holds in §10.1a-bis and persistence holds in §15.2. The host draws labels it was
    given over numbers it cannot interpret.

    ⚠ Formatting is per COLUMN and declared by the plugin (`format` as a printf spec), because the host
    has no way to know that a rate wants four decimals and a frame count wants none.
    """

    def __init__(self, title=None, columns=None, rows=None, caption=None):
        self.title = title
        self.caption = caption
        # [{"key": str, "label": str, "unit": str|None, "format": str|None, "align": "left"|"right"}]
        self.columns = list(columns or [])
        self.rows = list(rows or [])        # [{key: value}] — extra keys are ignored, missing ones blank

    def addColumn(self, key, label=None, unit=None, format=None, align="right"):
        self.columns.append({"key": key, "label": label or key, "unit": unit,
                             "format": format, "align": align})
        return self

    def addRow(self, row):
        self.rows.append(dict(row))
        return self

    def headerLabels(self):
        return [(column["label"] + (" (%s)" % column["unit"] if column.get("unit") else ""))
                for column in self.columns]

    def cellText(self, row, column):
        value = row.get(column["key"])
        if value is None or value == "":
            return ""
        if isinstance(value, bool):
            return "✓" if value else ""
        specifier = column.get("format")
        if specifier:
            try:
                return specifier % value
            except (TypeError, ValueError):
                return str(value)
        return str(value)

    def textRows(self):
        return [[self.cellText(row, column) for column in self.columns] for row in self.rows]

    # --- serialization (SPEC_bench_pdf_export.md §5, D2). ⭐ `columns` + `rows` ARE the wire format: the
    # view-model is already the self-describing structure a MonitorRecord carries (§15.2), so the
    # round-trip is a copy. ---
    def toJson(self):
        return {"type": "table", "title": self.title, "caption": self.caption,
                "columns": self.columns, "rows": self.rows, "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        view = cls(title=entry.get("title"), columns=entry.get("columns"), rows=entry.get("rows"),
                   caption=entry.get("caption"))
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
