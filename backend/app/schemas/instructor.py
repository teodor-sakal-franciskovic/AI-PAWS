from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    enrollments_count: int
    active_course_count: int
    ungraded_submissions_count: int
    longest_waiting_days: int


class DashboardCourseResponse(BaseModel):
    id: int
    name: str
    student_count: int
    students_without_submissions_count: int
    completed_submissions_count: int
    graded_submissions_count: int
    ungraded_submissions_count: int
    longest_waiting_days: int


class InstructorDashboardResponse(BaseModel):
    summary: DashboardSummaryResponse
    courses: list[DashboardCourseResponse] = []
