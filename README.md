# AI-PAWS

AI-Powered Academic Writing Support

### Running the App

1. Position yourself into the `backend` directory.
2. Add a `.env` file in the `backend` directory based on the `.env.template` file.
3. Run the following command: `docker compose up`.
4. Access the backend at the ```localhost:8080``` address in the web browser.


# Endpoints

- Endpoints are separated into many subgroups. For each subgroup, brief summary, body examples, and return values are present below.
- It should be noted that all of the return values have the same wrapper, which looks like the one provided below, with the status code also being present. In the "return value" sections, the "data" object structure will be provided.
- Only the endpoints that should be used in the app are presented here.
- All of the timestamps in the request bodies and the output should be UTC. The conversion to the local time should be done on the FE.
```json
{
    "message": "Some message",
    "data": {
        "Some object structure..": "..."
    }
}
```

## /assignments
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST    | `/`            | Creation of a new assignment           | TA screen for creating assignments                            |
| GET    | `/`            | Retrieval of all assignments           | TA screen for retrieving all assignments before downloading a zip of all submissions for a specific assignment                            |
| GET    | `/active`       | Retrieval of currently active assignments for submission      | Student screen when taking a look at active assignments                    |
| GET   | `/previous`            | Retrieval of previously submitted assignments            | Student screen when taking a look at previously submitted assignments                          |
| POST   | `/{assignment_id}/chapters/{chapter_id}/interactive`            | Upload of the currently-written research paper and retrieval of the received feedback            | Student screen when uploading a research paper as an assignment, after the upload, view of all of the received feedback                          |
| POST   | `/{assignment_id}/chapters/{chapter_id}/evaluative`            | Upload of the currently-written research paper            | Student screen when uploading a research paper as an assignment; No feedback received immediately after the upload, TA has to confirm/edit it first.
| GET   | `/{assignment_id}/submissions/files`            | Retrieval of pdfs submitted by students for a specific assignment            | TA will have an option to download the zip file with all of the submitted files when the evaluative assignment has finished. The zip file will contain a folder per TA, with each containing TAs' students' pdf files of research papers.      
### Body Examples
#### `POST /`

```json
{
  "name": "string",
  "start_date": "2025-06-18T00:00:00.000Z",
  "end_date": "2025-07-18T23:59:59.000Z",
  "submission_mode_id": 0,
  "chapter_id": 0,
  "group_ids": [1, 2]
}
```
#### `POST /{assignment_id}/chapters/{chapter_id}/interactive`
```
A pdf file upload is expected
```
#### `POST /{assignment_id}/chapters/{chapter_id}/evaluative`
```
A pdf file upload is expected
```
### Return Value Examples
#### `POST /`
```json
{
  "id": 1,
  "name": "Problem Interactive 2025",
  "start_date": "2025-07-01T00:00:00Z",
  "end_date": "2025-07-15T23:59:00Z",
  "submission_mode_id": 2,
  "submission_mode_name": "Interactive mode",
  "chapter_id": 1,
  "chapter_name": "Problem"
}
```
#### `GET /active`
- "status" can be "COMPLETED", "PENDING", "FAILED" 
```json
[{
  "id": 1,
  "name": "Final Research Essay",
  "start_date": "2025-06-01T09:00:00Z",
  "end_date": "2025-06-15T23:59:00Z",
  "submission_mode": "Evaluative mode",
  "chapter_id": 1,
  "chapter_name": "Problem",
  "submission": {
    "id": 101,
    "submitted_at": "2025-06-15T18:45:00Z",
    "text": "This is the submitted essay text...",
    "achieved_points_percentage": 32,
    "submission_mode": "Evaluative mode",
    "status": "COMPLETED",
    "file_bytes": "base-64-string",
    "rule_feedbacks": [
      {
        "feedback_id": 1,
        "is_valid": true,
        "rule_name": "Thesis Statement Clarity",
        "rule_description": "Evaluate how clear and focused the thesis is.",
        "feedback_text": "The thesis is clear but could be more specific.",
        "additional_feedback_text": "Consider rewording to make the scope narrower.",
        "fulfillment_value": 0.8,
        "initially_fulfilled": true,
      },
      {
        "feedback_id": 2,
        "is_valid": true,
        "rule_name": "Evidence and Examples",
        "rule_description": "Check whether the essay uses strong evidence.",
        "feedback_text": "Good examples used throughout.",
        "additional_feedback_text": "",
        "fulfillment_value": 1.0,
        "initially_fulfilled": true,
      }
    ]
  }
},
{
    ...
}
]
```
#### `GET /previous`
- "status" can be "COMPLETED", "PENDING", "FAILED" 
```json
[{
  "id": 1,
  "name": "Final Research Essay",
  "start_date": "2025-06-01T09:00:00Z",
  "end_date": "2025-06-15T23:59:00Z",
  "submission_mode": "Evaluative mode",
  "chapter_id": 1,
  "chapter_name": "Problem",
  "submission": {
    "id": 101,
    "submitted_at": "2025-06-15T18:45:00Z",
    "text": "This is the submitted essay text...",
    "achieved_points_percentage": 32,
    "submission_mode": "Evaluative mode",
    "status": "COMPLETED",
    "file_bytes": "base-64-string",
    "rule_feedbacks": [
      {
        "feedback_id": 1,
        "is_valid": true,
        "rule_name": "Thesis Statement Clarity",
        "rule_description": "Evaluate how clear and focused the thesis is.",
        "feedback_text": "The thesis is clear but could be more specific.",
        "additional_feedback_text": "Consider rewording to make the scope narrower.",
        "fulfillment_value": 0.8,
        "initially_fulfilled": true,
      },
      {
        "feedback_id": 2,
        "is_valid": true,
        "rule_name": "Evidence and Examples",
        "rule_description": "Check whether the essay uses strong evidence.",
        "feedback_text": "Good examples used throughout.",
        "additional_feedback_text": "",
        "fulfillment_value": 1.0,
        "initially_fulfilled": true,
      }
    ]
  }
},
{
    ...
}
]
```

#### `POST /{assignment_id}/chapters/{chapter_id}/interactive`
```json
{
  "submission_id": 1
}
```

#### `POST /{assignment_id}/chapters/{chapter_id}/evaluative`
```json
{
  "submission_id": 2
}
```

#### `GET /{assignment_id}/chapters/files`
```
A zip file with students' submitted pdf files.
```

## /auth
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST    | `/login`            | Login into the system           | An overall screen for logging into the application                            |

### Call Example: `POST /login`
```javascript
const formData = new URLSearchParams();
formData.append("username", "user@example.com");
formData.append("password", "your_password");

fetch("http://localhost:8080/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body: formData,
})
  .then(response => response.json())
  .then(data => {
    console.log("Token:", data.access_token);
  })
  .catch(error => {
    console.error("Login error:", error);
  });
```
### Return Value Examples
#### `POST /login`
```json
{
  "access_token": "<your-jwt-token>",
  "token_type": "bearer"
}
```

## /feedbacks
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST    | `/{feedback_id}/additional`            | Request for the additional feedback explanation in interactive mode            | Student screen when going over the received feedback in interactive mode and pressing the "request additional explanation"-like button                            |
| PUT    | `/{feedback_id}/invalid`       | Invalidation of the LLM received feedback      | Student screen when going over the received feedback in interactive mode and pressing the "invalidate feedback"-like button                    |
### Return Value Examples
#### `POST /{feedback_id}/additional`
```json
{
  "id": 42,
  "feedback_text": "The system accurately detected the edge case in user input.",
  "initially_fulfilled": true,
  "rule_name": "InputEdgeValidation",
  "rule_description": "Checks whether edge cases in user inputs are handled properly.",
  "additional_feedback_text": "Consider enhancing the regex for better email validation coverage.",
  "is_valid": true
}
```
#### `PUT /{feedback_id}/invalidate`
```
data part is None, only the message gets returned.
```
## /groups
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST    | `/`            | Creation of a new group           | TA screen for creating student groups for a specific semester                            |
| GET    | `/`            | Retrieval of active groups           | Used for the TA assignment creation, and for the "student groups" select on the course creation screen (V2)                            |
 
### Body Examples
#### `POST /`
```json
{
    "name": "G_1_2025",
    "short_name": "G1-2025",
    "valid_from": "2025-01-01T00:00:00",
    "valid_until": "2025-12-31T23:59:59",
}
```
- `short_name` is optional.
### Return Value Examples
#### `POST /`
```json
{
  "id": 7
}
```
- `409 Conflict`, code `GROUP_NAME_ALREADY_EXISTS`, if the name is taken (see the Endpoints V2 error-format note below for the shape of this error).
#### `GET /`
```json
[
    {
      "id": 1,
      "name": "G_1_2025",
      "short_name": "G1-2025",
      "valid_from": "2025-01-01T00:00:00",
      "valid_until": "2025-12-31T23:59:59"
    },
    {
      "id": 3,
      "name": "G_1_2024-6",
      "short_name": null,
      "valid_from": "2024-01-01T00:00:00",
      "valid_until": "2026-12-31T23:59:59"
    }
  ]
```
#### `PUT /{group_id}` and `DELETE /{group_id}`
- `204 No Content` on success.
- `404 Not Found`, code `GROUP_NOT_FOUND`, if the group doesn't exist.
- `PUT` also returns `409 Conflict`, code `GROUP_NAME_ALREADY_EXISTS`, if renaming to an already-used name.

## /roles
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| GET    | `/`            | Retrieval of the present roles in the system            | Role IDs are needed when registering new TAs via TA screen                           |
### Return Value Examples
#### `GET /`
```json
[
  {
    "id": 1,
    "name": "Student"
  },
  {
    "id": 2,
    "name": "TA" 
  }
]
```
## /submission-modes
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| GET    | `/`            | Retrieval of the present submission modes in the system            | Used for the TA assignment creation                            |
### Return Value Examples
#### `GET /`
```json
 [
    {
      "id": 1,
      "name": "Interactive mode",
      "description": "Mode in which students receive information about the quality of their submitted chapters."
    },
    {
      "id": 2,
      "name": "Evaluative mode",
      "description": "Mode in which students receive grades (and reasons behind them) for their submitted chapters."
    }
  ]
```
## /chapters
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| GET    | `/`            | Retrieval of the present chapters in the system            | Used for the TA assignment creation                            |
### Return Value Examples
#### `GET /`
```json
[
    {
      "id": 1,
      "name": "Problem"
    },
    {
      "id": 2,
      "name": "Teorijske osnove"
    },
    {
      "id": 3,
      "name": "Rešenje"
    },
    {
      "id": 4,
      "name": "Rezultati"
    }
  ]
```
## /users
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST    | `/registration`            | Registration of a new user (TA only)            | TA screen, where the TA is able to register a new TA if needed. Should incorporate GET /roles endpoint                           |
| GET    | `/me`       | Retrieval of the personal user info      | Home page for Students (maybe even TAs) should have personal info showage                    |
| PUT    | `/password`            | Password update            | Student screen if password change is wanted. Maybe same for the TA.                            |
| POST    | `/batch`       | Batch creation of students      | TA screen with the csv file upload button.                    |
| GET    | `/my-students/submissions/evaluative`            | TA Retrieval of evaluative submissions of his assigned students            | For each TA's student, all of the evaluative-assignment submissions are present.                        |
| PUT    | `/submission/{submission_id}/grade`       | TA grading of a submission      | After the submission has been sent to the app's evaluative mode (performed by LLM), TA has to go over the given grades and feedback and finalise them (by either editing or leaving them as they are). Afterwards, if needed, TA can edit the feedback/grades again.                    |
| POST   | `/initial-knowledge`       | TA submission of pretest results      | Students will have a pretest, which will be graded by the TAs. Afterwards, the results (which are going to be written in a csv file) should be uploaded via this endpoint by a TA, so that the initial student knowledge is present in the database.                    |

### Body Examples
#### `POST /registration`
```json
{
    "email": "example@email.com",
    "password": "Example123!",
    "name": "Name",
    "surname": "Surname",
    "role_id": 2,
}
```

#### `PUT /password`
```json
{
  "password": "NewPassword123!",
  "confirmed_password": "NewPassword123!"
}
```

#### `POST /batch`
```
A csv file is expected, with the following header columns: 
- Ime,
- Prezime,
- Email, 
- Grupa,
- Indeks,
- Asistent.

```

#### ```PUT /submission/{submission_id}/grade```
```json
{
  "evaluation_grades": [
    {
      "feedback_id": 102,
      "final_grade": 2,
      "fulfillment_id": 53,
      "final_feedback": "All good"
    },
    {
      ...
    }
  ]
}
```

#### `POST /batch`
```
A csv file is expected, with the following header columns: 
- Indeks,
- Other fields should be the names of the rules that are being evaluated.
```

### Return Value Examples
#### `POST /registration`
```json
{
    "email": "example@email.com",
    "is_active": true,
    "name": "Name",
    "surname": "Surname",
    "role": "TA",
    "student_index": null
}
```

#### `GET /me`
```json
{
    "email": "example@email.com",
    "is_active": true,
    "name": "Name",
    "surname": "Surname",
    "role": "Student",
    "student_index": "SV-1-2025"
}
```

#### `PUT /password`
- Probably not needed
```json
{
    "email": "example@email.com",
    "is_active": true,
    "name": "Name",
    "surname": "Surname",
    "role": "Student",
    "student_index": "SV-1-2025"
}
```

#### `POST /batch`
```
data part is None, only the message gets returned.
```

#### `GET /my-students/submissions/evaluative`
```json
{
  "users_with_submissions": [
    {
      "user_id": 101,
      "user_index": "SV-1-2025",
      "name": "Name",
      "surname": "Surname",
      "submissions": [
        {
          "submission_id": 501,
          "status": "COMPLETED",
          "submitted_at": "2025-07-20T14:30:00",
          "assignment_name": "Literature Review",
          "assignment_start_date": "2025-07-01T08:00:00",
          "assignment_end_date": "2025-07-15T23:59:00",
          "achieved_points_percentage": 87.5,
          "rules": [
            {
              "rule_id": 201,
              "name": "Clarity",
              "description": "Writing should be clear and precise.",
              "feedback": {
                "feedback_id": 301,
                "feedback_text": "Some sentences could be rephrased for clarity.",
                "final_feedback_text": "Improved clarity after revision."
              },
              "fulfillment": {
                "fulfillment_id": 401,
                "initial_fulfillment_value": 0,
                "final_fulfillment_value": 1
              }
            },
            {
              "rule_id": 202,
              "name": "Structure",
              "description": "Proper organisation of paragraphs.",
              "feedback": {
                "feedback_id": 302,
                "feedback_text": "Paragraphs are well-structured overall.",
                "final_feedback_text": "No further comments."
              },
              "fulfillment": {
                "fulfillment_id": 402,
                "initial_fulfillment_value": 2,
                "final_fulfillment_value": 2
              }
            }
          ]
        }
      ]
    },
    {
      ...
    },
  ]
}
```

#### ```PUT /submission/{submission_id}/grade```
```
data part is None, only the message gets returned.
```

#### `POST /initial-knowledge`
```
data part is None, only the message gets returned.
```

# Endpoints V2

- These endpoints replace the initial course-creation cut. Success responses still use the same `{ "message": ..., "data": ... }` wrapper as above, and all timestamps are UTC.
- Rule groups are now independent, reusable entities managed entirely through `/rule-groups` — creating or updating a course only *links* to existing rule groups by id (with a per-assignment `percentage_of_points_in_assignment`); it never creates, edits, or deletes a rule group or its rules.
- **Errors** on these endpoints do *not* use the `{ "message", "data" }` wrapper. They return the raw body shown in each section below, e.g.:
```json
{
  "code": "COURSE_NOT_FOUND",
  "message": "Course not found."
}
```
  `400` is always `VALIDATION_ERROR` (invalid/missing request data, or a request that references a deleted/nonexistent related record), `404` is a `*_NOT_FOUND` code, `409` is a `*_ALREADY_EXISTS` code (duplicate name).
- `PUT` and `DELETE` endpoints below return `204 No Content` (no body) on success.
- **Deletes are soft deletes** (an `is_active` flag under the hood). A deleted course/rule group/language: disappears from its `GET` list and `GET /{id}` (404s), frees up its name for reuse, and can no longer be newly *referenced* (linking a deleted rule group into a course, or a deleted language as a course's feedback/submission language, is rejected with `400 VALIDATION_ERROR`). It is **not** retroactively removed from courses that already reference it — those keep displaying it as before.

## /courses
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST   | `/`            | Creation of a new course and its (new) assignments. All `assignments` must be new (no `id`); all `assignments[].rule_groups` must reference existing rule groups by `id` — this endpoint never creates/edits rule groups | Course creation screen |
| PUT    | `/{course_id}`            | Update of a course. `assignments` with `id` are updated, without `id` are created, and existing ones not sent are deleted. `rule_groups` are always references to existing rule groups by `id` | Course edit screen |
| DELETE | `/{course_id}`            | Soft-delete of a course           | Course list "delete" action                            |
| GET    | `/`            | Retrieval of all (active) courses, unscoped           | Admin-style overview of every course in the system                            |
| GET    | `/instructor`            | Retrieval of all courses the logged-in instructor created or was added to           | Instructor's "My courses" screen                            |
| GET    | `/student`            | Retrieval of all courses for the logged-in student's group           | Student's "My courses" screen                            |
| GET    | `/{course_id}`            | Retrieval of a single course by id           | Course edit screen, populating the form when an instructor opens an existing course                            |
| GET    | `/check-name?name=&exclude_id=`            | Check whether a course name is already in use. `exclude_id` is optional and excludes the course being edited from the check           | Called on blur of the "Course name" field when creating/editing a course                            |
| GET    | `/{course_id}/students/mine`            | Retrieval of the logged-in instructor's own assigned students for this course           | Instructor's "my students" view for a course                            |
| GET    | `/{course_id}/students/unassigned`            | Retrieval of every student across **all** of this course's groups that has no instructor yet — a course can have multiple groups, and an instructor doesn't care which group a student is in, just whether they're picked | Instructor's "pick your students" screen, course-wide            |
| POST   | `/{course_id}/students/assign`            | Self-assigns the given students (from any of the course's groups) to the logged-in instructor           | Confirming a course-wide selection            |
| POST   | `/{course_id}/students/unassign`            | Un-assigns the given students (a batch — send a list of 1 to unassign just one) from whichever instructor currently has them, for this course           | "Undo"/reassign, course-wide            |

### Body Examples
#### `POST /`
```json
{
  "name": "Web Programming",
  "start_date": "2026-02-16T00:00:00.000Z",
  "end_date": "2026-06-30T23:59:59.000Z",
  "max_amount_of_points": 100,
  "feedback_language_id": 1,
  "submission_language_ids": [1, 2],
  "instructor_ids": [1, 4],
  "assignments": [
    {
      "name": "HTML & CSS Fundamentals",
      "start_date": "2026-03-02T00:00:00.000Z",
      "end_date": "2026-03-22T23:59:59.000Z",
      "submission_mode_id": 3,
      "percentage_of_points_in_course": 20,
      "rule_groups": [
        { "id": 3, "percentage_of_points_in_assignment": 60 }
      ]
    }
  ]
}
```
- **Student groups are no longer set here.** `POST`/`PUT /courses` don't accept a `student_group_ids` field anymore — a course's groups are (for now) only visible via `GET`, not settable through course create/update. A new group ↔ course flow is coming later.
#### `PUT /{course_id}`
- Same shape as `POST /`, except assignments may carry an `id` (update) or omit it (create); any existing assignment not present in the payload is deleted.

### Return Value Examples
#### `POST /`
```json
{
  "id": 17
}
```
- `409 Conflict`, code `COURSE_NAME_ALREADY_EXISTS`, if the name is taken.
- `400 Bad Request`, code `VALIDATION_ERROR`, if the body is invalid, or references a rule group / language id that doesn't exist (or has been deleted).

#### `PUT /{course_id}`
- `204 No Content` on success.
- `404 Not Found`, code `COURSE_NOT_FOUND`.
- `409 Conflict`, code `COURSE_NAME_ALREADY_EXISTS`.
- `400 Bad Request`, code `VALIDATION_ERROR` (same cases as `POST /`).

#### `DELETE /{course_id}`
- `204 No Content` on success.
- `404 Not Found`, code `COURSE_NOT_FOUND`, if it doesn't exist or was already deleted.

#### `GET /`
```json
[
  {
    "id": 1,
    "name": "Web Programming",
    "start_date": "2026-02-16T00:00:00Z",
    "end_date": "2026-06-30T23:59:59Z",
    "max_amount_of_points": 100,
    "feedback_language": {
      "id": 1,
      "name": "Serbian",
      "short_name": "SR"
    },
    "submission_languages": [
      {
        "id": 1,
        "name": "Serbian",
        "short_name": "SR"
      }
    ],
    "student_groups": [
      {
        "id": 1,
        "name": "Business Informatics 2026 - Group A",
        "short_name": "BI 2026-A"
      }
    ],
    "instructors": [
      {
        "id": 4,
        "name": "Ulrich",
        "surname": "Pantic"
      }
    ],
    "assignments": [
      {
        "id": 1,
        "name": "HTML & CSS Fundamentals",
        "start_date": "2026-03-02T00:00:00Z",
        "end_date": "2026-03-22T23:59:59Z",
        "submission_mode_id": 3,
        "submission_mode_name": "Evaluative mode",
        "percentage_of_points_in_course": 20,
        "rule_groups": [
          {
            "id": 3,
            "name": "HTML & CSS",
            "percentage_of_points_in_assignment": 60,
            "rules": [
              {
                "id": 1,
                "name": "Semantic Elements",
                "user_description": "Use semantic tags like main.",
                "include_in_prompt": true
              }
            ]
          }
        ]
      }
    ],
    "audit": {
      "created_at": "2026-08-19T10:42:15Z",
      "created_by": { "id": 4, "name": "Ulrich", "surname": "Pantic" },
      "updated_at": "2026-08-20T14:17:03Z",
      "updated_by": { "id": 7, "name": "Ana", "surname": "Petrovic" }
    }
  },
  {
    ...
  }
]
```
#### `GET /instructor`
- Same shape (and same objects) as `GET /`, just filtered to the courses the logged-in instructor created or was added to as an instructor.
#### `GET /student`
- Same shape (and same objects) as `GET /`, just filtered to the courses whose groups the logged-in student belongs to. Returns an empty array (with `data: []`) if the student isn't in a group.
#### `GET /{course_id}`
- Same shape as a single object from `GET /`.
- `404 Not Found`, code `COURSE_NOT_FOUND`, if the id doesn't exist or was deleted.
#### `GET /check-name`
```json
{
  "name_available": true
}
```
- `name_available: true` means the name is free to use (this includes names freed up by a deleted course).
#### `GET /{course_id}/students/mine`
```json
[
  {
    "id": 57,
    "name": "Petar",
    "surname": "Petrovic",
    "email": "petar@example.com",
    "index": "SV-1-2026",
    "faculty": "FTN",
    "is_active": true
  },
  {
    ...
  }
]
```
#### `GET /{course_id}/students/unassigned`
- Same shape as `GET /{course_id}/students/mine` above, but the unassigned pool — aggregated across every group linked to this course.
- `404 Not Found`, code `COURSE_NOT_FOUND`.
#### `POST /{course_id}/students/assign`
```json
{
  "student_ids": [79, 81]
}
```
- Students can come from **any** of the course's groups in the same call — no need to know which group a student belongs to.
- `204 No Content` on success.
- `400 Bad Request`, code `VALIDATION_ERROR`, if a given student isn't in any group linked to this course.
- `409 Conflict`, code `STUDENT_ALREADY_ASSIGNED`, if one or more are already taken by another instructor (including a genuine race between two instructors — the loser gets this error).
#### `POST /{course_id}/students/unassign`
```json
{
  "student_ids": [79]
}
```
- Same body shape as `assign` — a batch. Send a single-item list to unassign just one student.
- `204 No Content` on success.
- `404 Not Found`, code `ASSIGNMENT_NOT_FOUND`, if any given student currently has no instructor assigned for this course — all-or-nothing, same as the group-scoped version.

## /rule-groups
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST   | `/`            | Creation of a new, standalone rule group and its rules           | Rule group creation screen, or "create a new rule group" flow while building a course |
| PUT    | `/{rule_group_id}`            | Update of a rule group. Rules with `id` are updated, without `id` are created, existing ones not sent are deleted | Rule group edit screen |
| DELETE | `/{rule_group_id}`            | Soft-delete of a rule group           | Rule group library "delete" action                            |
| GET    | `/`            | Retrieval of all (active) rule groups           | Library of all rule groups, for picking existing ones when building a course            |
| GET    | `/instructor`            | Retrieval of the rule groups created by the logged-in instructor, plus rule groups used in any course they created or were added to (mirrors `GET /courses/instructor`)           | A "my rule groups" view/filter            |
| GET    | `/{rule_group_id}`            | Retrieval of a single rule group           | Rule group edit screen            |
| GET    | `/check-name?name=&exclude_id=`            | Check whether a rule group name is already in use. `exclude_id` is optional and excludes the rule group being edited from the check           | Called on blur of the "Rule group name" field                            |

### Body Examples
#### `POST /`
```json
{
  "name": "JavaScript Coding Style",
  "rules": [
    {
      "name": "Use Const",
      "user_description": "Always prefer const",
      "include_in_prompt": true
    }
  ]
}
```
#### `PUT /{rule_group_id}`
```json
{
  "name": "JavaScript Coding Standards",
  "rules": [
    {
      "id": 11,
      "name": "Use Const",
      "user_description": "Prefer const whenever possible",
      "include_in_prompt": true
    },
    {
      "name": "Use Strict Equality",
      "user_description": "Prefer === over ==",
      "include_in_prompt": true
    }
  ]
}
```

### Return Value Examples
#### `POST /`
```json
{
  "id": 17
}
```
- `409 Conflict`, code `RULE_GROUP_NAME_ALREADY_EXISTS`, if the name is taken.
- `400 Bad Request`, code `VALIDATION_ERROR`, if the body is invalid.

#### `PUT /{rule_group_id}`
- `204 No Content` on success.
- `404 Not Found`, code `RULE_GROUP_NOT_FOUND`.
- `409 Conflict`, code `RULE_GROUP_NAME_ALREADY_EXISTS`.

#### `DELETE /{rule_group_id}`
- `204 No Content` on success.
- `404 Not Found`, code `RULE_GROUP_NOT_FOUND`, if it doesn't exist or was already deleted.
- Deleting a rule group does not affect courses/assignments that already link it — it just stops appearing in `GET /` and can't be linked into *new* courses (`POST`/`PUT /courses` will 400 if you try).

#### `GET /`
```json
[
  {
    "id": 3,
    "name": "HTML & CSS",
    "number_of_courses": 1,
    "courses": [
      {
        "id": 1,
        "name": "Web Programming",
        "audit": {
          "created_at": "2026-08-19T10:42:15Z",
          "created_by": { "id": 4, "name": "Ulrich", "surname": "Pantic" },
          "updated_at": "2026-08-20T14:17:03Z",
          "updated_by": { "id": 7, "name": "Ana", "surname": "Petrovic" }
        }
      }
    ],
    "rules": [
      {
        "id": 1,
        "name": "Semantic Elements",
        "user_description": "Use semantic tags like main.",
        "include_in_prompt": true
      }
    ],
    "audit": {
      "created_at": "2026-08-19T10:42:15Z",
      "created_by": { "id": 12, "name": "Ulrich", "surname": "Pantic" },
      "updated_at": "2026-08-20T14:17:03Z",
      "updated_by": { "id": 7, "name": "Ana", "surname": "Petrovic" }
    }
  },
  {
    ...
  }
]
```
- Note: `number_of_courses` (`= courses.length`) is kept alongside the new `courses` array — the array is the actual list of courses that link this rule group (via one of their assignments), each with its own `id`/`name`/`audit` (the *course's* audit, not the rule group's). Empty array (and `number_of_courses: 0`) if it isn't linked to any course yet.
- Note: `percentage_of_points_in_assignment` is not part of the rule group anymore (a rule group can be linked to several assignments, each with its own percentage) — it only appears nested inside a course's `assignments[].rule_groups[]` (see `GET /courses/{course_id}`).
#### `GET /instructor`
- Same shape (and same objects) as `GET /`, filtered to rule groups the logged-in instructor created **or** that are used in a course they created or were added to as an instructor — same "created or added to" logic as `GET /courses/instructor`.
#### `GET /{rule_group_id}`
- Same shape as a single object from `GET /`.
- `404 Not Found`, code `RULE_GROUP_NOT_FOUND`, if the id doesn't exist or was deleted.
#### `GET /check-name`
```json
{
  "name_available": false
}
```

## /groups
- "Student groups" are the same `Group` entity documented in the `## /groups` section above (v1) — there's no separate `/student_groups` endpoint.
- A group is now always tied to a course at creation time, and is created with an already-picked list of students (see `GET /students/search` below for how to find them). Editing a group later can add/remove students, but a student can only ever belong to **one** group system-wide — trying to add someone who's already in a different group is rejected.
- Instructor self-assignment (picking which students are "theirs") is **course-scoped, not group-scoped** — a course can have multiple groups, and an instructor doesn't care which group a student came from. See `GET /courses/{course_id}/students/unassigned`, `POST /courses/{course_id}/students/assign`, and `POST /courses/{course_id}/students/unassign` in the `## /courses` section above.
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST   | `/`            | Creation of a new student group tied to a course, with a pre-selected student list           | Final step of the "create student group" flow, after searching/filtering students            |
| PUT    | `/{group_id}`            | Update of a student group. `student_ids`, if sent, fully replaces the group's roster (add/remove); omit it to leave the roster untouched           | Student group edit screen            |
| DELETE | `/{group_id}`            | Soft-delete of a student group           | Student group list "delete" action            |
| GET    | `/`            | Retrieval of active student groups (now includes `short_name`)           | Used for the "student groups" select on the course creation screen                            |

### Body Examples
#### `POST /`
```json
{
    "name": "G_1_2025",
    "short_name": "G1-2025",
    "valid_from": "2025-01-01T00:00:00",
    "valid_until": "2025-12-31T23:59:59",
    "course_id": 1,
    "student_ids": [57, 58, 59]
}
```
- `short_name` is optional. `course_id` is required and immutable after creation. `student_ids` defaults to `[]` (an empty group can be filled in later via `PUT`).
#### `PUT /{group_id}`
- Same shape as `POST /` minus `course_id`, but every field is optional — only send what should change. `student_ids`, if present, is the group's *complete* new roster (not a delta).

### Return Value Examples
#### `POST /`
```json
{
  "id": 7
}
```
- `409 Conflict`, code `GROUP_NAME_ALREADY_EXISTS`, if the name is taken.
- `400 Bad Request`, code `VALIDATION_ERROR`, if `course_id` doesn't exist, or any `student_ids` entry doesn't exist / isn't a `Student` / already belongs to a different group.
#### `PUT /{group_id}`
- `204 No Content` on success.
- `404 Not Found`, code `GROUP_NOT_FOUND`.
- `409 Conflict`, code `GROUP_NAME_ALREADY_EXISTS`, if renaming to an already-used name.
- `400 Bad Request`, code `VALIDATION_ERROR` (same `student_ids` cases as `POST /`).
#### `DELETE /{group_id}`
- `204 No Content` on success.
- `404 Not Found`, code `GROUP_NOT_FOUND`, if it doesn't exist or was already deleted.
#### `GET /`
```json
[
  {
    "id": 1,
    "name": "Business Informatics 2026 - Group A",
    "short_name": "BI 2026-A",
    "valid_from": "2025-01-01T00:00:00",
    "valid_until": "2025-12-31T23:59:59"
  },
  {
    ...
  }
]
```

## /languages
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| DELETE | `/{language_id}`            | Soft-delete of a language           | Language admin "delete" action                            |
| GET    | `/`            | Retrieval of the present (active) languages in the system           | Used for the feedback/submission language selects on the course creation screen                            |

### Return Value Examples
#### `DELETE /{language_id}`
- `204 No Content` on success.
- `404 Not Found`, code `LANGUAGE_NOT_FOUND`, if it doesn't exist or was already deleted.
- Deleting a language does not affect courses that already reference it as their feedback/submission language — it just stops appearing in `GET /` and can't be referenced by *new*/updated courses (`POST`/`PUT /courses` will 400 if you try).
#### `GET /`
```json
[
  {
    "id": 1,
    "name": "Serbian",
    "short_name": "SR"
  },
  {
    "id": 2,
    "name": "English",
    "short_name": "EN"
  }
]
```

## /instructors
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| GET    | `/`            | Retrieval of all active users with the Instructor role           | Used to populate the instructor picker on the course creation screen                            |

### Return Value Examples
#### `GET /`
```json
[
  {
    "id": 4,
    "name": "Ulrich",
    "surname": "Pantic"
  },
  {
    ...
  }
]
```

## /students
- Registration is now a standalone step, separate from group creation — a registered student has no group and no assigned instructor until later steps (`POST /groups/` and `POST /courses/{course_id}/students/assign`).
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST   | `/batch`            | Bulk registration of students from a CSV export of the "Excel" roster           | Student registration screen, CSV upload            |
| GET    | `/search?email=&name=&surname=&faculty=&index=&page=&page_size=`            | Paginated, filterable search over registered students           | "Find my students" screen when building a group — filter by faculty/index/etc. before adding to a group            |

### Body Examples
#### `POST /batch`
```
A CSV file is expected, with the following header columns:
- Email,
- Ime,
- Prezime,
- Fakultet,
- Indeks.
```
- All fields are currently assumed to arrive as a CSV export. If the source data actually comes through as JSON instead, this endpoint's body/parsing will need a small follow-up change.

### Return Value Examples
#### `POST /batch`
```
data part is None, only the message gets returned (e.g. "Successfully registered 3 students.").
```
- `400 Bad Request`, code `VALIDATION_ERROR`, if the file isn't a CSV, fails to parse, or is missing a required column.
#### `GET /search`
```json
{
  "items": [
    {
      "id": 58,
      "name": "Ana",
      "surname": "Anic",
      "email": "ana@example.com",
      "index": "SV-2-2026",
      "faculty": "FTN",
      "is_active": true
    },
    {
      ...
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 25
}
```
- All filters are optional and match as case-insensitive substrings. `page_size` is capped at 100 (default 25) to avoid pulling the whole student table at once — use `total` to drive pagination on the FE.
