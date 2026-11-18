from datetime import date


class ResumeRepository:
    def __init__(self, db):
        self.db = db

    def get_by_seeker(self, seeker_id: int):
        rows = self.db.query(
            "SELECT r.resume_id, r.skills, r.experience_years, r.experience, r.updated_at, "
            "       js.education "
            "FROM job_seekers js LEFT JOIN resumes r ON r.seeker_id = js.user_id "
            "WHERE js.user_id = ?",
            (seeker_id,),
        )
        if not rows:
            return None
        row = rows[0]
        # түйіндеме әлі жоқ болса, тек білім ақпараты қайтады
        return row if row["resume_id"] is not None else {**row, "skills": None}

    def save(self, seeker_id: int, skills: str, experience_years: int,
             experience, education) -> None:
        """Түйіндемені құру/жаңарту және job_seekers деректерін синхрондау (бір транзакция)."""
        today = date.today().isoformat()
        with self.db.transaction() as tx:
            exists = tx.query("SELECT 1 AS x FROM resumes WHERE seeker_id = ?", (seeker_id,))
            if exists:
                tx.execute(
                    "UPDATE resumes SET skills = ?, experience_years = ?, experience = ?, "
                    "updated_at = ? WHERE seeker_id = ?",
                    (skills, experience_years, experience, today, seeker_id),
                )
            else:
                tx.execute(
                    "INSERT INTO resumes (seeker_id, skills, experience_years, experience, updated_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (seeker_id, skills, experience_years, experience, today),
                )
            tx.execute(
                "UPDATE job_seekers SET education = ?, skills = ? WHERE user_id = ?",
                (education, skills, seeker_id),
            )

    def save_match(self, resume_id: int, vacancy_id: int, score: float, model_version: str) -> None:
        """match_results кестесіне балл жазады (бар болса жаңартады)."""
        with self.db.transaction() as tx:
            exists = tx.query(
                "SELECT 1 AS x FROM match_results WHERE resume_id = ? AND vacancy_id = ?",
                (resume_id, vacancy_id),
            )
            if exists:
                tx.execute(
                    "UPDATE match_results SET score = ?, model_version = ? "
                    "WHERE resume_id = ? AND vacancy_id = ?",
                    (score, model_version, resume_id, vacancy_id),
                )
            else:
                tx.execute(
                    "INSERT INTO match_results (resume_id, vacancy_id, score, model_version) "
                    "VALUES (?, ?, ?, ?)",
                    (resume_id, vacancy_id, score, model_version),
                )
