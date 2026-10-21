"""Indexable fixture representing a small deployment-readiness module."""


class DeploymentReport:
    """Aggregate named checks and expose a human-readable readiness summary."""

    def __init__(self, checks: dict[str, bool]) -> None:
        self.checks = checks

    def readiness(self) -> bool:
        """Return true only when every deployment check passes."""
        return bool(self.checks) and all(self.checks.values())


def calculate_deployment_readiness(checks: dict[str, bool]) -> str:
    """Return a concise status suitable for a CI summary."""
    report = DeploymentReport(checks)
    return "ready" if report.readiness() else "blocked"
