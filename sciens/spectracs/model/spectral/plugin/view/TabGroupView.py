from sciens.spectracs.model.spectral.plugin.view.ReportableView import ReportableView


class TabGroupView(ReportableView):
    # SPEC_simplified_plugin_navigation.md §7b/§7c (T1) — an EXPLICIT container view-model: a labelled group of
    # child view-models the plugin wants shown as SUB-TABS. The Qt renderer draws a QTabWidget (one sub-tab per
    # child, each rendered by a fresh QtWorkflowRenderer); the matplotlib report renderer stacks the children
    # under their tab headings (paper has no tabs). Grouping is plugin-DECLARED — no implicit "N consecutive
    # captures auto-group" heuristic, no `title` field on the child views.
    #
    # `tabs` is an ordered list of (label, childView) pairs. Children may be any view-model and serialize through
    # the ViewModelFactory, so a group round-trips faithfully (nested captures/plots included). Only descriptors
    # persist — a child SpectrumCaptureView carries no pixels (the host fills `.image` after dispatch, traversing
    # into the group), exactly as at top level.

    def __init__(self, tabs=None):
        self.tabs = list(tabs) if tabs else []   # [(label, childView), ...]

    def addTab(self, label, view):
        # ⭐ `view` may be a SINGLE view-model or a LIST of them (SPEC_settled_measurement.md §27.9): a tab
        # whose content is a summary — a heading plus a column of metric rows — is several view-models, and
        # forcing it into one would mean inventing a "summary view" that the metric grid already renders.
        self.tabs.append((label, view))
        return self

    def children(self):
        flattened = []
        for _label, view in self.tabs:
            flattened.extend(view if isinstance(view, list) else [view])
        return flattened

    # --- serialization (recurse children through the ViewModelFactory; imported lazily to avoid the factory ↔
    # view-model import cycle) ---
    def toJson(self):
        return {"type": "tabgroup",
                "tabs": [{"label": label,
                          "views": [item.toJson() for item in (view if isinstance(view, list) else [view])
                                    if hasattr(item, "toJson")]}
                         for label, view in self.tabs],
                "isShownInReport": self.isShownInReport}

    @classmethod
    def fromJson(cls, entry):
        from sciens.spectracs.model.spectral.plugin.view.ViewModelFactory import ViewModelFactory
        view = cls()
        for tab in entry.get("tabs", []):
            if "views" in tab:           # multi-view tab (a summary column)
                children = [ViewModelFactory.fromJson(item or {}) for item in tab.get("views") or []]
                children = [child for child in children if child is not None]
                if children:
                    view.addTab(tab.get("label"), children if len(children) > 1 else children[0])
                continue
            child = ViewModelFactory.fromJson(tab.get("view") or {})   # legacy single-view form
            if child is not None:
                view.addTab(tab.get("label"), child)
        view.isShownInReport = entry.get("isShownInReport", False)
        return view
