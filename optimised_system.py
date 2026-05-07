import sqlite3
from typing import List, Dict, Optional

DB_NAME = "submission_review.db"


class Submission:
    def __init__(self, id: int, title: str, content: str, status: str):
        self.id = id
        self.title = title
        self.content = content
        self.status = status

class Reviewer:
    def __init__(self, id: int, name: str, email: str, current_workload: int, max_workload: int, conflict_subject: str):
        self.id = id
        self.name = name
        self.email = email
        self.current_workload = current_workload
        self.max_workload = max_workload
        self.conflict_subject = conflict_subject


class SubmissionRepository:
    @staticmethod
    def save(title: str, content: str) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO submissions (title, content, status) VALUES (?, ?, ?)",
                       (title, content, 'submitted'))
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return submission_id

class ReviewerRepository:
    @staticmethod
    def get_available_reviewers(submission_title: str = "") -> List[Reviewer]:
        """
        Single method that filters by both conflict and workload in one pass.
        In baseline this was two separate loops (filterConflicts, checkWorkload).
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, current_workload, max_workload, conflict_subject FROM reviewers")
        rows = cursor.fetchall()
        conn.close()
        
        reviewers = []
        for row in rows:
            rev = Reviewer(row[0], row[1], row[2], row[3], row[4], row[5])
            if rev.current_workload >= rev.max_workload:
                continue
            if rev.conflict_subject and rev.conflict_subject.lower() in submission_title.lower():
                continue
            reviewers.append(rev)
        return reviewers

    @staticmethod
    def save_score(submission_id: int, reviewer_id: int, score: int):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO reviews (submission_id, reviewer_id, score) VALUES (?, ?, ?)",
                       (submission_id, reviewer_id, score))
        conn.commit()
        conn.close()

class DecisionEngine:
    @staticmethod
    def evaluate(scores: List[int]) -> str:

        if not scores:
            return "revision" 
        
        avg = sum(scores) / len(scores)
        consensus = (max(scores) - min(scores)) <= 2
        

        if avg >= 8.0 and consensus:
            return "accepted"
    
        if avg < 5.0:
            return "rejected"
    
        return "revision"


class EvaluationCoordinator:
    def __init__(self, submission_id: int, reviewers: List[Reviewer], repo: ReviewerRepository):
        self.submission_id = submission_id
        self.reviewers = reviewers
        self.repo = repo
        self.scores = []
    
    def run_evaluation(self) -> str:
        for reviewer in self.reviewers:
            score = (reviewer.id * 7) % 10 + 1
            self.scores.append(score)
            self.repo.save_score(self.submission_id, reviewer.id, score)
        decision = DecisionEngine.evaluate(self.scores)
        return decision


class Validator:
    @staticmethod
    def validate(data: Dict) -> bool:
        return bool(data.get('title') and data.get('content'))


class NotificationService:
    @staticmethod
    def notify_acceptance(researcher_email: str):
        print(f"[Optimised] Acceptance sent to {researcher_email}")
    @staticmethod
    def notify_rejection(researcher_email: str):
        print(f"[Optimised] Rejection sent to {researcher_email}")
    @staticmethod
    def notify_revision(researcher_email: str):
        print(f"[Optimised] Revision requested sent to {researcher_email}")


class SubmissionController:
    def submit(self, data: Dict) -> Dict:
        
        if not Validator.validate(data):
            return {"error": "Invalid format"}
        
       
        submission_id = SubmissionRepository.save(data['title'], data['content'])
        
        reviewers = ReviewerRepository.get_available_reviewers(data.get('title', ''))
        
        coordinator = EvaluationCoordinator(submission_id, reviewers, ReviewerRepository())
        decision = coordinator.run_evaluation()
        
        researcher_email = data.get('email', 'researcher@example.com')
        notifier = NotificationService()
        if decision == "accepted":
            notifier.notify_acceptance(researcher_email)
        elif decision == "rejected":
            notifier.notify_rejection(researcher_email)
        else:
            notifier.notify_revision(researcher_email)
        
        return {"status": decision, "submission_id": submission_id}


class UI:
    @staticmethod
    def submit(data: Dict):
        controller = SubmissionController()
        return controller.submit(data)


if __name__ == "__main__":
    
    test_data = {
        "title": "AI in SE",
        "content": "Full paper...",
        "email": "researcher@example.com"
    }
    result = UI.submit(test_data)
    print("Optimised Result:", result)