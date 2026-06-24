# Wizan Data Retention Policy

## Purpose

This policy defines how user data is stored, retained, and deleted within the Wizan platform.

## User Accounts

* User accounts are retained until the user requests account deletion.
* Deleted accounts are soft-deleted by setting:

  * is_deleted = True
  * is_active = False

## Uploaded Documents

* Uploaded study documents are retained while the user account remains active.
* Documents remain associated with the user account for learning history and AI retrieval.

## Chat Feedback

* Chat feedback records are retained for system improvement and quality monitoring.
* Feedback data contains:

  * Question
  * Answer
  * Rating
  * Timestamp

## Voice Logs

* Audio files are never stored.
* Only transcribed text and metadata are retained.

## Audit Logs

* Audit logs are retained for security and auditing purposes.
* Logs record important actions such as:

  * Document uploads
  * Study chat requests
  * Voice planning requests

## Data Access

* Users may request account deactivation.
* Administrative access to stored data is restricted to authorized personnel only.

## Security

* All stored data is protected through authentication and authorization mechanisms implemented by the platform.
