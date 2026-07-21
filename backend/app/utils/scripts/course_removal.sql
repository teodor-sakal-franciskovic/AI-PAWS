-- ============================================
-- 1) Remove ALL courses and everything related
-- ============================================

DELETE FROM academic_writing_schema.fulfillment;
DELETE FROM academic_writing_schema.historical_profile;
DELETE FROM academic_writing_schema.rule_feedback_submission;
DELETE FROM academic_writing_schema.submission;
DELETE FROM academic_writing_schema.rule;
DELETE FROM academic_writing_schema.assignment_rule_group;
DELETE FROM academic_writing_schema.rule_group;
DELETE FROM academic_writing_schema.assignment;
DELETE FROM academic_writing_schema.course_submission_language;
DELETE FROM academic_writing_schema.course_group;
DELETE FROM academic_writing_schema.course_instructor;
DELETE FROM academic_writing_schema.course;


-- ============================================
-- 2) Remove a single course by ID
--    Replace :course_id with the actual ID
-- ============================================

CREATE TEMP TABLE _assignment_ids AS
    SELECT id FROM academic_writing_schema.assignment
    WHERE course_id = :course_id;

CREATE TEMP TABLE _rg_ids AS
    SELECT arg.rule_group_id AS id
    FROM academic_writing_schema.assignment_rule_group arg
    WHERE arg.assignment_id IN (SELECT id FROM _assignment_ids);

CREATE TEMP TABLE _submission_ids AS
    SELECT id FROM academic_writing_schema.submission
    WHERE assignment_id IN (SELECT id FROM _assignment_ids);

DELETE FROM academic_writing_schema.fulfillment
WHERE submission_id IN (SELECT id FROM _submission_ids);

DELETE FROM academic_writing_schema.historical_profile
WHERE submission_id IN (SELECT id FROM _submission_ids);

DELETE FROM academic_writing_schema.rule_feedback_submission
WHERE submission_id IN (SELECT id FROM _submission_ids);

DELETE FROM academic_writing_schema.submission
WHERE id IN (SELECT id FROM _submission_ids);

DELETE FROM academic_writing_schema.rule
WHERE rule_group_id IN (SELECT id FROM _rg_ids);

DELETE FROM academic_writing_schema.assignment_rule_group
WHERE assignment_id IN (SELECT id FROM _assignment_ids);

DELETE FROM academic_writing_schema.rule_group
WHERE id IN (SELECT id FROM _rg_ids);

DELETE FROM academic_writing_schema.assignment
WHERE id IN (SELECT id FROM _assignment_ids);

DELETE FROM academic_writing_schema.course_submission_language
WHERE course_id = :course_id;

DELETE FROM academic_writing_schema.course_group
WHERE course_id = :course_id;

DELETE FROM academic_writing_schema.course_instructor WHERE course_id = :course_id;  -- uncomment after migration

DELETE FROM academic_writing_schema.course
WHERE id = :course_id;

DROP TABLE _submission_ids;
DROP TABLE _rg_ids;
DROP TABLE _assignment_ids;