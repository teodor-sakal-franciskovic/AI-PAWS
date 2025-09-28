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
  "submission": {
    "id": 101,
    "submitted_at": "2025-06-15T18:45:00Z",
    "text": "This is the submitted essay text...",
    "achieved_points_percentage": 32,
    "submission_mode": "Evaluative mode",
    "status": "COMPLETED",
    "rule_feedbacks": [
      {
        "feedback_id": 1,
        "rule_name": "Thesis Statement Clarity",
        "rule_description": "Evaluate how clear and focused the thesis is.",
        "feedback_text": "The thesis is clear but could be more specific.",
        "additional_feedback_text": "Consider rewording to make the scope narrower.",
        "fulfillment_value": 0.8
      },
      {
        "feedback_id": 2,
        "rule_name": "Evidence and Examples",
        "rule_description": "Check whether the essay uses strong evidence.",
        "feedback_text": "Good examples used throughout.",
        "additional_feedback_text": "",
        "fulfillment_value": 1.0
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
  "submission": {
    "id": 101,
    "submitted_at": "2025-06-15T18:45:00Z",
    "text": "This is the submitted essay text...",
    "achieved_points_percentage": 32,
    "submission_mode": "Evaluative mode",
    "status": "COMPLETED",
    "rule_feedbacks": [
      {
        "feedback_id": 1,
        "rule_name": "Thesis Statement Clarity",
        "rule_description": "Evaluate how clear and focused the thesis is.",
        "feedback_text": "The thesis is clear but could be more specific.",
        "additional_feedback_text": "Consider rewording to make the scope narrower.",
        "fulfillment_value": 0.8
      },
      {
        "feedback_id": 2,
        "rule_name": "Evidence and Examples",
        "rule_description": "Check whether the essay uses strong evidence.",
        "feedback_text": "Good examples used throughout.",
        "additional_feedback_text": "",
        "fulfillment_value": 1.0
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
  "additional_text": "Consider enhancing the regex for better email validation coverage.",
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
| GET    | `/`            | Retrieval of active groups           | Used for the TA assignment creation                            |
 
### Body Examples
#### `POST /`
```json
{
    "name": "G_1_2025",
    "valid_from": "2025-01-01T00:00:00",
    "valid_until": "2025-12-31T23:59:59",
}
```
### Return Value Examples
#### `POST /`
```
data part is None, only the message gets returned.
```
#### `GET /`
```json
[
    {
      "id": 1,
      "name": "G_1_2025",
      "valid_from": "2025-01-01T00:00:00",
      "valid_until": "2025-12-31T23:59:59"
    },
    {
      "id": 3,
      "name": "G_1_2024-6",
      "valid_from": "2024-01-01T00:00:00",
      "valid_until": "2026-12-31T23:59:59"
    }
  ]
```

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
