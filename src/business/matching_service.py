class MatchingService:
    """Сәйкестендіру модулі: түйіндеме дағдыларын вакансия талаптарымен салыстырады."""

    MODEL_VERSION = "v1.0"

    @staticmethod
    def _phrases(text) -> set:
        return {p.strip().lower() for p in (text or "").replace(";", ",").split(",") if p.strip()}

    def score(self, skills, requirements) -> float:
        """Талаптардың қаншасы дағдыларда бар екенін пайызбен (0–100) қайтарады."""
        need = self._phrases(requirements)
        if not need:
            return 0.0
        have = self._phrases(skills)
        return round(100.0 * len(need & have) / len(need), 2)
