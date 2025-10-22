import pandas as pd
from typing import Dict, List, Any
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


def build_students_data(
    df: pd.DataFrame, rule_descriptions: Dict[str, str], index_column: str = "Indeks"
) -> List[Dict[str, Any]]:
    """
    Build a structured list of student evaluation data by combining rule values
    from a DataFrame with rule descriptions from the database.

    Args:
        df (pd.DataFrame): DataFrame containing student evaluations.
                           First column (or the one named `index_column`)
                           should identify each student.
        rule_descriptions (Dict[str, str]): Mapping of rule_name -> description.
        index_column (str, optional): Name of the column representing student index.
                                      Defaults to "index".

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing one student,
                              with all rule evaluations and descriptions.
    """
    students_data: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        student_index = row["Indeks"]
        rules = []

        for col in df.columns:
            if col == index_column:
                continue

            rule_name = col
            rule_value = row[col]
            rule_description = rule_descriptions.get(rule_name, "No description found")

            rules.append(
                {
                    "rule_name": rule_name,
                    "rule_description": rule_description,
                    "value": int(rule_value) if pd.notna(rule_value) else None,
                }
            )

        students_data.append({"student_index": student_index, "rules": rules})

    return students_data
