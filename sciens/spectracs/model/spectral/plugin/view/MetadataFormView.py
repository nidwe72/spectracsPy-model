class MetadataFormView:
    # Transient render descriptor for the METADATA phase's editable form (SPEC_simplified_plugin_navigation.md
    # §4.7-E). Like CaptureView it is interactive, so it does NOT flow through the passive visitor — the host's
    # metadata form path consumes it. It carries the ordered metadata field specs (MetadataField-shaped:
    # name / label / type / order); the host builds the inputs and reads them back to SpectralWorkflowMetadata
    # rows on save.
    #
    # NOT persisted: only the entered VALUES persist (as SpectralWorkflowMetadata rows). This view is rebuilt
    # from the plugin's fields (new run) or from those rows (viewing a saved run). Holds no MetadataField import
    # (it only needs the field-shaped objects), so the model layer keeps no dependency on the plugin_sdk base.

    def __init__(self, fields=None):
        self.fields = list(fields) if fields else []

    def getFields(self):
        return self.fields
