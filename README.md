# AI-PAWS

AI-Powered Academic Writing Support

### Running the App

1. Position yourself into the `backend` directory.
2. Add a `.env` file in the `backend` directory based on the `.env.template` file.
3. Run the following command: `docker compose up`.
4. Access the backend at the ```localhost:8080``` address in the web browser.

- Alembic migrations (`alembic upgrade head`) run automatically on container startup, after the database reports healthy — no manual migration step needed.


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
| POST   | `/{assignment_id}/submissions/evaluative`            | Student upload of a paper (PDF) for an evaluative assignment. The AI grades it in the background against the assignment's rule groups            | Student screen when submitting a paper for an evaluative assignment; the student gets no feedback right away — the instructor reviews/finalises the AI's grades first (`/courses/{course_id}/submissions/{submission_id}/evaluation`).
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
#### `POST /{assignment_id}/submissions/evaluative`
```
multipart/form-data with a single "file" field containing the PDF
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

#### `POST /{assignment_id}/submissions/evaluative`
```json
{
  "id": 2
}
```
- `201 Created`. The submission is stored as `PENDING` and the response returns right away; the AI grades it in the background. It then becomes `COMPLETED` (ready for the instructor to grade), or `FAILED` if the AI call or processing failed.
- Only students can submit, and only to evaluative assignments of courses they're enrolled in (i.e. they're in a group on that course). Submitting again is allowed; the grading page uses the latest completed submission.
- The rules graded are those of the assignment's rule groups. Rules with `include_in_prompt: false` aren't sent to the AI — their row is still created, with no AI grade, for the instructor to grade.
- Errors use the V2 error format (see **Endpoints V2** below):
  - `404 Not Found`, code `ASSIGNMENT_NOT_FOUND`, if the assignment doesn't exist, isn't evaluative, or its course was deleted.
  - `403 Forbidden`, code `ASSIGNMENT_ACCESS_DENIED`, if the student isn't enrolled in the assignment's course.
  - `409 Conflict`, code `ASSIGNMENT_HAS_NO_RULES`, if the assignment has no rule groups/rules to grade against.
  - `400 Bad Request`, code `VALIDATION_ERROR`, if the file isn't a PDF or can't be read.
  - `401 Unauthorized`, code `UNAUTHORIZED`, if not logged in or not a student.

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
| GET    | `/`            | Retrieval of all non-deleted groups, regardless of their `valid_from`/`valid_until` dates           | Used for the TA assignment creation, and for the "student groups" select on the course creation screen (V2)                            |
 
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
      "valid_until": "2025-12-31T23:59:59",
      "course_id": 17,
      "course_name": "Web Programming"
    },
    {
      "id": 3,
      "name": "G_1_2024-6",
      "short_name": null,
      "valid_from": "2024-01-01T00:00:00",
      "valid_until": "2026-12-31T23:59:59",
      "course_id": null,
      "course_name": null
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
  `400` is always `VALIDATION_ERROR` (invalid/missing request data, or a request that references a deleted/nonexistent related record), `403` is a `*_ACCESS_DENIED` code (logged in, but no access to that resource), `404` is a `*_NOT_FOUND` code, `409` is a `*_ALREADY_EXISTS` code (duplicate name) or a state conflict described in the endpoint's section.
- Across **all** endpoints (V1 included), a missing/invalid token, or a logged-in user without the required role, returns `401` with `{"code": "UNAUTHORIZED", "message": ...}`, and an unexpected server error returns `500` with `{"code": "INTERNAL_SERVER_ERROR", "message": ...}`.
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
| GET    | `/{course_id}/students/available-for-group?excluded_ids=57,61`            | Retrieval of every registered, active student **not already in a group on this course**, minus any `excluded_ids` sent (comma-separated). Returns the full matching list, unpaginated | The "add students" picker when creating or editing a student group |
| PUT    | `/{course_id}/students/mine`            | Sets the logged-in instructor's complete list of students for this course (from any of the course's groups). Students added to the list are assigned, students removed from it are unassigned           | Confirming the instructor's course-wide selection            |
| GET    | `/{course_id}/students/mine/submissions/evaluative`            | Retrieval of the logged-in instructor's assigned students on this course, each with their completed evaluative submissions for this course and a points summary. Students with no completed evaluative submissions are included too           | Grading page, after the instructor picks a course (from `GET /instructor`)            |
| GET    | `/{course_id}/submissions/{submission_id}/evaluation`            | Everything needed to view and grade one evaluative submission: course, student, assignment, the submitted file, the AI's suggested grades and the instructor's final grades per rule (grouped by rule group), points, and what the instructor is allowed to do           | Submission evaluation page (create/edit/view)            |
| POST   | `/{course_id}/submissions/{submission_id}/evaluation/final`            | First grading of a submission: the instructor's final grade and feedback for every rule           | "Save" on the evaluation page when `grading_status` is `NOT_GRADED` and `permissions.can_grade` is `true`            |
| PUT    | `/{course_id}/submissions/{submission_id}/evaluation/final`            | Replaces an existing final evaluation. Every rule must be sent again, changed or not           | "Save" on the evaluation page when `grading_status` is `GRADED` and `permissions.can_edit_grade` is `true`            |

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
#### `PUT /{course_id}`
- Same shape as `POST /`, except assignments may carry an `id` (update) or omit it (create); any existing assignment not present in the payload is deleted.
#### `POST /{course_id}/submissions/{submission_id}/evaluation/final` and `PUT /{course_id}/submissions/{submission_id}/evaluation/final`
```json
{
  "rule_evaluations": [
    {
      "rule_id": 201,
      "final_feedback_text": "Siri problem je dobro predstavljen, ali kontekst treba dodatno razraditi.",
      "final_fulfillment_value": 1
    },
    {
      "rule_id": 202,
      "final_feedback_text": "Osnovni koncepti su jasno definisani i pravilno upotrebljeni.",
      "final_fulfillment_value": 2
    }
  ]
}
```
- `rule_evaluations` must contain **every** rule of the submission (the rules listed in `GET .../evaluation`) exactly once — on `PUT` too, including unchanged ones.
- `final_fulfillment_value` is `0`, `1` or `2` (see `fulfillment_scale` in `GET .../evaluation`).

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
#### `GET /{course_id}/students/mine/submissions/evaluative`
```json
{
  "students_with_submissions": [
    {
      "student_id": 101,
      "student_index": "SV_13_2022",
      "name": "Mihajlo",
      "surname": "Orlovic",
      "summary": {
        "completed_submissions_count": 2,
        "ungraded_submissions_count": 1,
        "achieved_points": 19.34,
        "max_points": 45
      },
      "submissions": [
        {
          "submission_id": 501,
          "submission_status": "COMPLETED",
          "grading_status": "GRADED",
          "submitted_at": "2026-03-30T12:27:00",
          "assignment": {
            "id": 201,
            "name": "Poglavlje Problem 2026 (Evaluativni)",
            "start_date": "2026-03-23T00:00:00",
            "end_date": "2026-04-06T23:59:00",
            "max_points": 22.5
          },
          "result": {
            "fulfillment_ratio": 0.8596,
            "achieved_points": 19.34
          }
        },
        {
          "submission_id": 502,
          "submission_status": "COMPLETED",
          "grading_status": "NOT_GRADED",
          "submitted_at": "2026-04-18T09:40:00",
          "assignment": {
            "id": 202,
            "name": "Poglavlje Resenje 2026 (Evaluativni)",
            "start_date": "2026-04-08T00:00:00",
            "end_date": "2026-05-04T23:59:00",
            "max_points": 22.5
          },
          "result": null
        }
      ]
    },
    {
      "student_id": 102,
      "student_index": "SV_21_2022",
      "name": "Katalin",
      "surname": "Nagy",
      "summary": {
        "completed_submissions_count": 0,
        "ungraded_submissions_count": 0,
        "achieved_points": 0,
        "max_points": 0
      },
      "submissions": []
    }
  ]
}
```
- Only students assigned to the logged-in instructor on this course are returned (see `PUT /{course_id}/students/mine`), ordered by surname and name.
- Only `COMPLETED` submissions are returned (the only ones an instructor can grade), for assignments of this course whose submission mode is evaluative. Submissions are ordered by assignment start date.
- If a student has more than one completed submission for the same assignment, only the latest one is returned and counted in `summary`. Older ones (and newer `PENDING`/`FAILED` uploads) are left out.
- `grading_status` is `GRADED` once the instructor has graded the submission (`POST /{course_id}/submissions/{submission_id}/evaluation/final`), otherwise `NOT_GRADED`. `result` is `null` until it's graded.
- `assignment.max_points` = the course's `max_amount_of_points` × the assignment's `percentage_of_points_in_course` / 100. It's `null` if either value isn't set.
- `result.fulfillment_ratio` is the submission's grade (0–1, weighted by rule group — see `GET /{course_id}/submissions/{submission_id}/evaluation` below), and `result.achieved_points` = `fulfillment_ratio` × `max_points`, rounded to 2 decimals.
- `summary.max_points` adds up `max_points` over all of the student's completed submissions, graded or not; `summary.achieved_points` adds up `achieved_points` over the graded ones only.
- Access: the instructor must have created the course or been added to it as an instructor.
- `404 Not Found`, code `COURSE_NOT_FOUND`, if the course doesn't exist or was deleted.
- `403 Forbidden`, code `COURSE_ACCESS_DENIED`, if the logged-in instructor has no access to the course.
- `401 Unauthorized` if the request isn't authenticated, or the logged-in user isn't an instructor.
- A valid course with no assigned students returns `200` with `"students_with_submissions": []`.
#### `GET /{course_id}/submissions/{submission_id}/evaluation`
```json
{
  "course": { "id": 1, "name": "Probni naziv kursa" },
  "student": {
    "student_id": 101,
    "student_index": "SV_13_2022",
    "name": "Mihajlo",
    "surname": "Orlovic"
  },
  "assignment": {
    "id": 201,
    "name": "Poglavlje Problem 2026 (Evaluativni)",
    "start_date": "2026-03-23T00:00:00",
    "end_date": "2026-04-06T23:59:00",
    "max_points": 22.5
  },
  "submission": {
    "id": 501,
    "status": "COMPLETED",
    "submitted_at": "2026-03-30T12:27:00",
    "file": {
      "name": "poglavlje-problem.pdf",
      "mime_type": "application/pdf",
      "download_url": "/submissions/501/file"
    }
  },
  "evaluation": {
    "grading_status": "GRADED",
    "ai_suggested_result": { "fulfillment_ratio": 0.75, "achieved_points": 16.88 },
    "final_result": { "fulfillment_ratio": 0.85, "achieved_points": 19.13 },
    "graded_at": "2026-04-19T10:35:00",
    "graded_by": { "instructor_id": 7, "name": "Teodor", "surname": "Sakal Franciskovic" }
  },
  "fulfillment_scale": [
    { "value": 0, "code": "NOT_FULFILLED" },
    { "value": 1, "code": "PARTIALLY_FULFILLED" },
    { "value": 2, "code": "FULFILLED" }
  ],
  "rule_groups": [
    {
      "id": 31,
      "name": "Sadrzaj i relevantnost",
      "position": 1,
      "percentage_of_points_in_assignment": 60,
      "summary": {
        "rules_count": 2,
        "finalized_rules_count": 2,
        "max_points": 13.5,
        "ai_suggested_achieved_points": 10.13,
        "final_achieved_points": 10.13
      },
      "rules": [
        {
          "id": 201,
          "position": 1,
          "name": "Siri problem",
          "description": "Siri problem koji rad obradjuje treba da bude jasno predstavljen.",
          "evaluation": {
            "ai_suggestion": {
              "feedback_text": "Siri problem je delimicno predstavljen.",
              "fulfillment_value": 1
            },
            "final": {
              "feedback_text": "Siri problem je dobro predstavljen, ali kontekst treba razraditi.",
              "fulfillment_value": 1
            }
          }
        },
        {
          ...
        }
      ]
    },
    {
      ...
    }
  ],
  "permissions": {
    "can_view": true,
    "can_grade": false,
    "can_edit_grade": true
  }
}
```
- **Access:** only the instructor the student is assigned to on this course (see `PUT /{course_id}/students/mine`), who must also have created or been added to the course, can view or grade the evaluation. Everyone else gets `403`.
- **Which rules:** the rules the AI evaluated for this submission, even if the rule group was edited later. Rule groups are sorted alphabetically by name, and rules alphabetically by name inside each rule group, using the language-neutral Unicode order: upper/lower case and accents are ignored (so `Č` sorts with `C` and `Á` with `A`), and other scripts (Greek, Cyrillic, …) come after Latin. `position` is that order, starting at 1 (for rules, restarting in each rule group). A rule's `description` is its instructor-written description.
- **Grades per rule:** `ai_suggestion` is the AI's grade and explanation. `final` is the instructor's, and is `null` until the submission is graded.
- **Points:** `assignment.max_points` = the course's `max_amount_of_points` × the assignment's `percentage_of_points_in_course` / 100 (`null` if either isn't set). Each rule group's `summary.max_points` is its share of that, based on `percentage_of_points_in_assignment`.
- **How the score is computed:** each rule group's score is the sum of its rules' grades divided by 2 × its number of graded rules, and the groups are combined using their `percentage_of_points_in_assignment`. Example: group A (60%) fully met and group B (40%) half met gives 0.6 × 1 + 0.4 × 0.5 = 0.8. If any rule group has no percentage set, all rule groups count equally; percentages that don't add up to 100 are scaled so a fully met submission always gets 1. `ai_suggested_result` applies this to the AI's grades and `final_result` to the instructor's (`null` until graded). `achieved_points` = `fulfillment_ratio` × `max_points`, rounded to 2 decimals.
- **`graded_at` / `graded_by`:** the last time the final evaluation was saved, and by whom (`null` for submissions graded before this was tracked).
- **`submission.file`:** `null` if no file was stored. `name` is the original upload's file name; older submissions get a generated one (`{student_index}-{assignment-name}.pdf`). Download it with `GET /submissions/{submission_id}/file` (needs the login token).
- **`permissions`:** `can_grade` is `true` for a `COMPLETED`, not yet graded submission (→ `POST .../evaluation/final`); `can_edit_grade` is `true` for a graded one (→ `PUT .../evaluation/final`). Submissions that aren't `COMPLETED` can be viewed but not graded.
- `404 Not Found`, code `COURSE_NOT_FOUND`, if the course doesn't exist or was deleted.
- `404 Not Found`, code `SUBMISSION_NOT_FOUND`, if the submission doesn't exist, isn't in this course, or isn't on an evaluative assignment.
- `403 Forbidden`, code `SUBMISSION_EVALUATION_ACCESS_DENIED`, see **Access** above.
#### `POST /{course_id}/submissions/{submission_id}/evaluation/final` and `PUT /{course_id}/submissions/{submission_id}/evaluation/final`
```json
{
  "grading_status": "GRADED",
  "ai_suggested_result": { "fulfillment_ratio": 0.75, "achieved_points": 16.88 },
  "final_result": { "fulfillment_ratio": 0.85, "achieved_points": 19.13 },
  "graded_at": "2026-04-19T10:35:00",
  "graded_by": { "instructor_id": 7, "name": "Teodor", "surname": "Sakal Franciskovic" }
}
```
- Returns the updated `evaluation` object (same shape as in `GET .../evaluation`). `POST` returns `201 Created`, `PUT` returns `200 OK`.
- `PUT` fully replaces the existing final evaluation, and both set `graded_by`/`graded_at` to the current instructor and time.
- After a `POST`, the student's knowledge profile is updated in the background through the AI, using the final grades (this used to happen inside the old `PUT /users/submission/{submission_id}/grade`). It doesn't delay the response. `PUT` doesn't trigger it again.
- Saving is all-or-nothing: if anything fails validation, nothing is saved.
- `400 Bad Request`, code `VALIDATION_ERROR`, if the body is invalid (e.g. a value outside 0–2), or `rule_evaluations` doesn't contain every rule of the submission exactly once. In the second case, `data` lists the problem rule ids:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "rule_evaluations must contain every rule of this submission exactly once.",
  "data": { "duplicate_rule_ids": [], "unknown_rule_ids": [999], "missing_rule_ids": [204] }
}
```
- `404 Not Found`, code `COURSE_NOT_FOUND` / `SUBMISSION_NOT_FOUND`, same as `GET .../evaluation`.
- `403 Forbidden`, code `SUBMISSION_EVALUATION_ACCESS_DENIED`, same as `GET .../evaluation`.
- `409 Conflict`, code `SUBMISSION_NOT_READY_FOR_GRADING`, if the submission isn't `COMPLETED`.
- `POST` only: `409 Conflict`, code `EVALUATION_ALREADY_GRADED`, if the submission is already graded (use `PUT`).
- `PUT` only: `404 Not Found`, code `FINAL_EVALUATION_NOT_FOUND`, if the submission hasn't been graded yet (use `POST`).
#### `GET /{course_id}/students/unassigned`
- Same shape as `GET /{course_id}/students/mine` above, but the unassigned pool — aggregated across every group linked to this course.
- `404 Not Found`, code `COURSE_NOT_FOUND`.
#### `GET /{course_id}/students/available-for-group`
- Same item shape as `GET /{course_id}/students/mine` above (`id`, `name`, `surname`, `email`, `index`, `faculty`, `is_active`).
- `excluded_ids` is an optional single query param holding a comma-separated list of ids (`?excluded_ids=57,61`)
- `404 Not Found`, code `COURSE_NOT_FOUND`.
#### `PUT /{course_id}/students/mine`
```json
{
  "student_ids": [79, 81]
}
```
- `student_ids` is the logged-in instructor's **complete** new list of students for this course, not a delta. Students in the list who aren't yet yours get assigned to you; students currently yours who are missing from the list get unassigned. Send `[]` to unassign all of your students.
- Only your own assignments are affected — you can't unassign another instructor's students by leaving them out.
- Students can come from **any** of the course's groups — no need to know which group a student belongs to.
- All-or-nothing: if anything fails validation, nothing changes.
- `204 No Content` on success.
- `404 Not Found`, code `COURSE_NOT_FOUND`.
- `400 Bad Request`, code `VALIDATION_ERROR`, if `student_ids` has duplicates, or a newly added student isn't in any group linked to this course.
- `409 Conflict`, code `STUDENT_ALREADY_ASSIGNED`, if one or more newly added students are already assigned to another instructor (including a genuine race between two instructors — the loser gets this error). The conflicting students are listed in `data`:
```json
{
  "code": "STUDENT_ALREADY_ASSIGNED",
  "message": "One or more students are already assigned to another instructor for this course.",
  "data": { "student_ids": [81] }
}
```

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
- A group is tied to exactly one course at a time. The course it's tied to **can be changed later** via `PUT /{group_id}`.
- Membership rule: a student can belong to groups on **different** courses at the same time (e.g. one group for "Web Programming", another for "Databases"), but can only be in **one** group per course. 
- Instructor self-assignment (picking which students are "theirs") is **course-scoped, not group-scoped** — a course can have multiple groups, and an instructor doesn't care which group a student came from. See `GET /courses/{course_id}/students/unassigned`, `GET /courses/{course_id}/students/mine`, and `PUT /courses/{course_id}/students/mine` in the `## /courses` section above.
- Authorization: any authenticated `Instructor` can create/view/edit a group on any active course — there's no per-course ownership check (matches every other course-linked endpoint in this API, e.g. the course-scoped assign/unassign above). Admin-level restrictions (limiting group management to specific instructors) are a known open item, not yet designed.
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST   | `/`            | Creation of a new student group tied to a course, with a pre-selected student list           | Final step of the "create student group" flow, after searching/filtering students            |
| GET    | `/{group_id}`            | Full detail of one student group: its course, its current roster, and audit info           | Student group view/edit screen, loading an existing group            |
| PUT    | `/{group_id}`            | Update of a student group. `course_id`, if sent, re-links the group to a different course. `student_ids`, if sent, fully replaces the group's roster (add/remove); omit either to leave it untouched           | Student group edit screen            |
| DELETE | `/{group_id}`            | Soft-delete of a student group           | Student group list "delete" action            |
| GET    | `/`            | Retrieval of all non-deleted student groups, regardless of their `valid_from`/`valid_until` dates (includes `short_name`)           | Used for the "student groups" select on the course creation screen                            |

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
- `short_name` is optional. `course_id` is required. `student_ids` defaults to `[]` (an empty group can be filled in later via `PUT`).
#### `PUT /{group_id}`
```json
{
    "name": "Business Informatics 2026 - Group A",
    "short_name": "BI 2026-A",
    "valid_from": "2026-02-16T00:00:00",
    "valid_until": "2026-06-30T23:59:59",
    "course_id": 22,
    "student_ids": [57, 61, 73]
}
```
- Every field is optional — only send what should change.
- `course_id`, if omitted, leaves the group on its current course. If sent, the group is re-linked to that course, and **every current member is re-validated against the new course** (rejected with `409` if any of them is already in a different group there).
- `student_ids`, if omitted, leaves the roster untouched (even if `course_id` changes — existing members just move over to the new course with the group). If sent, it's the group's *complete* new roster, not a delta of adds/removes.

### Return Value Examples
#### `POST /`
```json
{
  "id": 7
}
```
- `409 Conflict`, code `GROUP_NAME_ALREADY_EXISTS`, if the name is taken.
- `400 Bad Request`, code `VALIDATION_ERROR`, if `course_id` doesn't exist/isn't active, `student_ids` has duplicates, or any entry doesn't exist / isn't a `Student`.
- `409 Conflict`, code `STUDENT_ALREADY_IN_COURSE_GROUP`, if any `student_ids` entry already belongs to a *different* group on this course:
```json
{
  "code": "STUDENT_ALREADY_IN_COURSE_GROUP",
  "message": "One or more students already belong to another group in this course.",
  "data": { "student_ids": [61, 73] }
}
```
#### `GET /{group_id}`
```json
{
  "id": 7,
  "name": "Business Informatics 2026 - Group A",
  "short_name": "BI 2026-A",
  "valid_from": "2026-02-16T00:00:00",
  "valid_until": "2026-06-30T23:59:59",
  "course_id": 17,
  "course_name": "Web Programming",
  "students": [
    {
      "id": 57,
      "name": "Petar",
      "surname": "Petrovic",
      "email": "petar@example.com",
      "index": "SV-1-2026",
      "faculty": "FTN",
      "is_active": true
    }
  ],
  "audit": {
    "created_at": "2026-08-23T16:24:35.009585",
    "created_by": { "id": 1, "name": "Teodor", "surname": "Sakal Franciskovic" },
    "updated_at": "2026-08-24T09:20:44.844673",
    "updated_by": { "id": 1, "name": "Teodor", "surname": "Sakal Franciskovic" }
  }
}
```
- `404 Not Found`, code `GROUP_NOT_FOUND`.
#### `PUT /{group_id}`
- `204 No Content` on success.
- `404 Not Found`, code `GROUP_NOT_FOUND`.
- `409 Conflict`, code `GROUP_NAME_ALREADY_EXISTS`, if renaming to an already-used name.
- `400 Bad Request`, code `VALIDATION_ERROR` (same `student_ids`/`course_id` validation as `POST /`).
- `409 Conflict`, code `STUDENT_ALREADY_IN_COURSE_GROUP` (same shape as `POST /`) — either from a `student_ids` conflict, or because changing `course_id` puts an existing member in conflict with a group they're already in on the new course.
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
    "valid_until": "2025-12-31T23:59:59",
    "course_id": 17,
    "course_name": "Web Programming"
  },
  {
    ...
  }
]
```
- `course_id`/`course_name` are the group's course (same fields as `GET /{group_id}`). Both are `null` if the group isn't linked to a course, or its course was deleted.

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
- Registration is now a standalone step, separate from group creation — a registered student has no group and no assigned instructor until later steps (`POST /groups/` and `PUT /courses/{course_id}/students/mine`).
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| POST   | `/batch`            | Bulk registration of students from a JSON list (built from manual entry, CSV/Excel import, or a clipboard paste — the FE normalizes all of those to the same JSON shape before sending)           | Student registration screen            |
| GET    | `/search?email=&name=&surname=&faculty=&index=`            | Filterable search over registered students. Returns the full matching list, unpaginated (by design — the FE table handles filtering/sorting/pagination client-side)           | "Find my students" screen when building a group — filter by faculty/index/etc. before adding to a group            |

### Body Examples
#### `POST /batch`
```json
{
  "students": [
    {
      "name": "Ana",
      "surname": "Nadj",
      "email": "ana@gmail.com",
      "faculty": "FTN",
      "index": "00100"
    },
    {
      "name": "Pera",
      "surname": "Kis",
      "email": "pera@gmail.com",
      "faculty": "FTN",
      "index": "00101"
    }
  ]
}
```
- All 5 fields are required per student.
- `students` must contain between 1 and 500 entries.
- `faculty` is a free-text field.
- Processing is atomic: if any student in the batch fails validation, nothing in the batch is registered.
- Credential emails are sent as a background task after the response is returned — the request doesn't wait on SMTP, so the FE isn't blocked by slow/failed email delivery. A failed send is logged server-side but doesn't affect the registration result the FE already received.

### Return Value Examples
#### `POST /batch`
```json
{
  "message": "Successfully registered 2 students.",
  "data": {
    "registered_count": 2
  }
}
```
- `400 Bad Request`, code `STUDENT_BATCH_EMPTY`, if `students` is an empty array.
- `400 Bad Request`, code `STUDENT_BATCH_LIMIT_EXCEEDED`, if `students` has more than 500 entries.
- `400 Bad Request`, code `VALIDATION_ERROR`, if the request body doesn't match the expected JSON shape (missing/wrong-typed fields) — the app-wide generic validation response.
- `400 Bad Request`, code `STUDENT_BATCH_VALIDATION_FAILED`, if one or more students fail business validation. All errors found are returned together:
```json
{
  "code": "STUDENT_BATCH_VALIDATION_FAILED",
  "message": "Student batch contains validation errors.",
  "data": {
    "errors": [
      {
        "row_number": 2,
        "field": "email",
        "code": "STUDENT_EMAIL_ALREADY_EXISTS",
        "message": "A student with this email already exists."
      },
      {
        "row_number": 3,
        "field": "index",
        "code": "STUDENT_INDEX_ALREADY_EXISTS",
        "message": "A student with this index already exists."
      }
    ]
  }
}
```
  - `row_number` is 1-indexed into the `students` array from the request, for the FE to map an error back to a row.
  - Possible per-row `code`s: `STUDENT_EMAIL_INVALID`, `STUDENT_EMAIL_DUPLICATED_IN_BATCH`, `STUDENT_INDEX_DUPLICATED_IN_BATCH`, `STUDENT_EMAIL_ALREADY_EXISTS`, `STUDENT_INDEX_ALREADY_EXISTS`.
#### `GET /search`
```json
[
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
]
```
- All filters are optional and match as case-insensitive substrings.
- No pagination or server-side limit: the full matching list is returned in one response (expected to be at most a few thousand rows), for the FE table (e.g. Tabulator) to filter/sort/paginate client-side — same convention as `GET /courses/{course_id}/students/available-for-group` above.

## /submissions
### Brief Summary
| Method | Path                      | Description                                   | FE Usage                                 |
|--------|---------------------------|-----------------------------------------------|----------------------------------------------|
| GET    | `/{submission_id}/file`            | Download of the PDF the student submitted           | The file link on the submission evaluation page (`submission.file.download_url` in `GET /courses/{course_id}/submissions/{submission_id}/evaluation`)            |

### Return Value Examples
#### `GET /{submission_id}/file`
```
The PDF file itself (Content-Type: application/pdf), with Content-Disposition: attachment and the file name. Not wrapped in the { "message", "data" } object.
```
- Needs the login token like every other endpoint, so the FE has to download it with an authenticated request (e.g. `fetch` → blob) instead of a plain link. The file name to show is `submission.file.name` from the evaluation endpoint.
- Same access rule as the evaluation page: only the instructor the student is assigned to on that course.
- `404 Not Found`, code `SUBMISSION_NOT_FOUND`, if the submission doesn't exist or its course was deleted.
- `404 Not Found`, code `SUBMISSION_FILE_NOT_FOUND`, if the submission has no stored file.
- `403 Forbidden`, code `SUBMISSION_ACCESS_DENIED`, if the student isn't assigned to the logged-in instructor on that course.
