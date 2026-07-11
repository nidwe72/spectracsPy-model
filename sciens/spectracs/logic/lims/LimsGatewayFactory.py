from sciens.spectracs.logic.lims.LimsError import LimsError
from sciens.spectracs.logic.lims.LimsGateway import LimsGateway
from sciens.spectracs.logic.lims.dto.LimsTarget import LimsTarget


class LimsGatewayFactory:
    """Resolves a plugin's `LimsTarget` to a concrete `LimsGateway` adapter. The plugin picks the LIMS;
    the factory picks the adapter and hands it the config key so it can load its own `.env` block.
    See SPEC_lims_integration.md §4.

    Built-in backends: "mock" (offline/tests) and "senaite" (M1). Extra backends can be added at runtime
    via `register(backend, factory)` where `factory` is `callable(configKey) -> LimsGateway`.
    """

    _registry = {}          # backend -> callable(configKey) -> LimsGateway

    @classmethod
    def register(cls, backend: str, factory) -> None:
        cls._registry[backend] = factory

    @classmethod
    def create(cls, target: LimsTarget) -> LimsGateway:
        backend = target.backend
        if backend in cls._registry:
            return cls._registry[backend](target.configKey)
        builtin = cls._builtin(backend)
        if builtin is None:
            raise LimsError("unknown LIMS backend %r" % backend)
        return builtin(target.configKey)

    @classmethod
    def _builtin(cls, backend: str):
        if backend == "mock":
            from sciens.spectracs.logic.lims.MockLimsGateway import MockLimsGateway
            return lambda configKey: MockLimsGateway(configKey)
        if backend == "senaite":
            try:
                from sciens.spectracs.logic.lims.adapters.senaite.SenaiteLimsGateway import \
                    SenaiteLimsGateway
            except ImportError:
                raise LimsError("SENAITE adapter not available yet (arrives in L2)")
            return lambda configKey: SenaiteLimsGateway(configKey)
        return None
