class ResumeRepository:
    def __init__(self, db):
        self.db = db

    def get_by_seeker(self, seeker_id: int):
        rows = self.db.query(
            "SELECT resume_id, skills FROM resumes WHERE seeker_id = ?",
            (seeker_id,),
        )
        return rows[0] if rows else None

    def save_match(self, resume_id: int, vacancy_id: int, score: float, model_version: str) -> None:
        """match_results кестесіне балл жазады (бар болса жаңартады)."""
        self.db.execute(
            "IF EXISTS (SELECT 1 FROM match_results WHERE resume_id = ? AND vacancy_id = ?) "
            "    UPDATE match_results SET score = ?, model_version = ? "
            "    WHERE resume_id = ? AND vacancy_id = ? "
            "ELSE "
            "    INSERT INTO match_results (resume_id, vacancy_id, score, model_version) "
            "    VALUES (?, ?, ?, ?)",
            (resume_id, vacancy_id, score, model_version, resume_id, vacancy_id,
             resume_id, vacancy_id, score, model_version),
        )
