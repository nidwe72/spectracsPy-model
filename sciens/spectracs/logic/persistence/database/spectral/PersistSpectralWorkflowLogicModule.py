from typing import List, Optional

from sqlalchemy.orm import selectinload

from sciens.spectracs.model.databaseEntity.DbBase import save_session
# Importing SpectralWorkflow registers the whole graph (its module is the registration hub).
from sciens.spectracs.model.spectral.SpectralWorkflow import SpectralWorkflow
from sciens.spectracs.model.spectral.SpectralWorkflowMetadata import SpectralWorkflowMetadata


class PersistSpectralWorkflowLogicModule:
    # Persists / lists / loads / updates / deletes the SpectralWorkflow graph (SPEC_workflow_persistence.md
    # §2/§4/§6). Always on a SHORT-LIVED save_session (autoflush off) — never the shared singleton (§2.2).

    def save(self, workflow):
        self.__syncJsonColumns(workflow)
        session = save_session()
        try:
            session.add(workflow)     # cascade persists the reachable graph
            session.commit()
        finally:
            session.close()

    def listForUser(self, userId) -> List[SpectralWorkflow]:
        # Newest first. Eager-load metadata + the evaluation results (for the list columns) — NOT the spectra.
        session = save_session()
        try:
            workflows = session.query(SpectralWorkflow).filter(
                SpectralWorkflow.userId == userId).order_by(
                SpectralWorkflow.timestampIso.desc()).options(
                selectinload(SpectralWorkflow.metadataFields),
                selectinload(SpectralWorkflow.phases)).all()
            for workflow in workflows:
                self.__touchForList(workflow)
            return workflows
        finally:
            session.close()

    def findById(self, workflowId) -> Optional[SpectralWorkflow]:
        session = save_session()
        try:
            workflow = session.query(SpectralWorkflow).filter(SpectralWorkflow.id == workflowId).first()
            self.__touchFull(workflow)      # load the whole graph before detaching
            return workflow
        finally:
            session.close()

    def updateMetadata(self, workflowId, valuesByName, userId=None):
        session = save_session()
        try:
            workflow = session.query(SpectralWorkflow).filter(SpectralWorkflow.id == workflowId).first()
            if workflow is None or (userId is not None and workflow.userId != userId):
                return
            for field in workflow.getMetadataFields():
                if field.name in valuesByName:
                    field.value = valuesByName[field.name]
            session.commit()
        finally:
            session.close()

    def delete(self, workflowId, userId=None):
        session = save_session()
        try:
            workflow = session.query(SpectralWorkflow).filter(SpectralWorkflow.id == workflowId).first()
            if workflow is None or (userId is not None and workflow.userId != userId):
                return
            session.delete(workflow)        # cascade="all, delete-orphan" removes the whole graph
            session.commit()
        finally:
            session.close()

    # --- helpers ---

    def __syncJsonColumns(self, workflow):
        for phase in workflow.getPhases().values():
            for step in phase.getSteps().values():
                container = step.getContainer()
                if container is not None:
                    for spectrum in container.getSpectra().values():
                        spectrum.syncToColumn()
                evaluationResult = step.getEvaluationResult()
                if evaluationResult is not None:
                    evaluationResult.syncToColumn()

    def __touchForList(self, workflow):
        list(workflow.getMetadataFields())
        for phase in workflow.getPhases().values():
            for step in phase.getSteps().values():
                if step.getEvaluationResult() is not None:
                    _ = step.getEvaluationResult().resultJson

    def __touchFull(self, workflow):
        if workflow is None:
            return
        list(workflow.getMetadataFields())
        for phase in workflow.getPhases().values():
            for step in phase.getSteps().values():
                container = step.getContainer()
                if container is not None:
                    for spectrum in container.getSpectra().values():
                        _ = spectrum.valuesJson
                if step.getEvaluationResult() is not None:
                    _ = step.getEvaluationResult().resultJson
