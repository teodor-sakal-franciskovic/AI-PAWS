from typing import List
from ..models.role import Role
from ..models.user import User
from ..schemas.user import (
    UserResponse,
    EvaluativeUsersSubmissionResponse,
    EvaluativeUserSubmissionSchema,
)


def create_user_response(user: User, role: Role):
    return UserResponse(
        email=user.email,
        name=user.name,
        surname=user.surname,
        is_active=user.is_active,
        role=role.name,
        index=user.index,
    )


def group_submission_data(sql_user_submissions) -> EvaluativeUsersSubmissionResponse:
    users_map = {}  # user_id -> {"user": {...}, "submissions_map": {submission_id: {...}}}

    for row in sql_user_submissions:
        (
            user_id,
            user_index,
            user_name,
            user_surname,
            submission_id,
            submitted_at,
            achieved_points_percentage,
            assignment_name,
            assignment_start_date,
            assignment_end_date,
            rule_id,
            rule_name,
            rule_description,
            feedback_id,
            feedback_text,
            final_feedback_text,
            fulfillment_id,
            initial_fulfillment_value,
            final_fulfillment_value,
        ) = row

        if user_id not in users_map:
            users_map[user_id] = {
                "user": {
                    "user_id": user_id,
                    "user_index": user_index,
                    "name": user_name,
                    "surname": user_surname,
                    "submissions": [],
                },
                "submissions_map": {},
            }

        user_entry = users_map[user_id]
        submissions_map = user_entry["submissions_map"]

        if submission_id not in submissions_map:
            submission_obj = {
                "submission_id": submission_id,
                "submitted_at": submitted_at,
                "achieved_points_percentage": achieved_points_percentage,
                "assignment_name": assignment_name,
                "assignment_start_date": assignment_start_date,
                "assignment_end_date": assignment_end_date,
                "rules": [],
            }
            user_entry["user"]["submissions"].append(submission_obj)
            submissions_map[submission_id] = submission_obj

        submissions_map[submission_id]["rules"].append(
            {
                "rule_id": rule_id,
                "name": rule_name,
                "description": rule_description,
                "feedback": {
                    "feedback_id": feedback_id,
                    "feedback_text": feedback_text,
                    "final_feedback_text": final_feedback_text,
                },
                "fulfillment": None
                if fulfillment_id is None
                else {
                    "fulfillment_id": fulfillment_id,
                    "initial_fulfillment_value": initial_fulfillment_value,
                    "final_fulfillment_value": final_fulfillment_value,
                },
            }
        )

    user_list_dicts = [entry["user"] for entry in users_map.values()]
    user_models: List[EvaluativeUserSubmissionSchema] = [
        EvaluativeUserSubmissionSchema(**u) for u in user_list_dicts
    ]
    return EvaluativeUsersSubmissionResponse(users_with_submissions=user_models)
