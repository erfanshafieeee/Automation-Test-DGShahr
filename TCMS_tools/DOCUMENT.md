# 🚀 End-to-End Guide: Connecting Your Tests to **Kiwi TCMS** via **tcms\_api**

> 📘 A practical, structured handbook for integrating your codebase with Kiwi TCMS using the `tcms_api` client. You’ll find prerequisites, setup, usage patterns, security/debug tips, and a **complete API reference** (everything you provided is included verbatim—nothing omitted).
> 🐍 Example language: **Python**.

---

## 📋 Table of Contents

* [🌐 What is Kiwi TCMS?](#-what-is-kiwi-tcms)
* [🐍 What is `tcms_api`?](#-what-is-tcms_api)
* [⚙️ Prerequisites & Installation](#️-prerequisites--installation)
* [🔐 Connection & Authentication](#-connection--authentication)
* [🛠️ Common Usage Patterns](#️-common-usage-patterns)
* [🧰 Security & Debugging Tips](#-security--debugging-tips)
* [📚 Complete API Reference (by Entity)](#-complete-api-reference-by-entity)

  * 📎 Attachment
  * 🔐 Auth
  * 🐞 Bug
  * 🧱 Build
  * 🗂️ Category
  * 🏷️ Classification
  * 🧩 Component
  * 🌳 Environment
  * 🥝 KiwiTCMS
  * ✍️ Markdown
  * 🗺️ PlanType
  * ⬆️ Priority
  * 📦 Product
  * 🏷️ Tag
  * 🧪 TestCase
  * 🔄 TestCaseStatus
  * ▶️ TestExecution
  * 🔁 TestExecutionStatus
  * 🗒️ TestPlan
  * 🏃 TestRun
  * 📈 Testing
  * 👤 User
  * 🔖 Version
  * 🧰 system.\*
* [🧾 Appendix: Quick Triage Checklist](#-appendix-quick-triage-checklist)

---

## 🌐 What is Kiwi TCMS?

**Kiwi TCMS** is an open-source test management system for organizing test plans, test cases, runs, and execution results. It helps with quality tracking, team collaboration, reporting, and easy integrations.

## 🐍 What is `tcms_api`?

`tcms_api` is a client library (commonly XML-RPC/JSON-RPC based) that lets you operate Kiwi TCMS from **Python**: CRUD on core objects, file attachments, tags, comments, bug reporting, test execution updates, and more.

---

## ⚙️ Prerequisites & Installation

```bash
pip install tcms-api
```

> ℹ️ You’ll need the Kiwi TCMS server URL and valid credentials (username/password or token—depending on server configuration).

---

## 🔐 Connection & Authentication

A simple bootstrap pattern:

```python
from tcms_api import TCMS

# Your server endpoint (adjust to your deployment)
client = TCMS(url="https://tcms.example.com/xml-rpc/")

# Login (returns session_id)
session_id = client.Auth.login("user123", "password123")

# ... use client.* namespaces ...

# Logout when done
client.Auth.logout()
```

> 💡 Note: Namespaced classes are typically accessible via `client` (e.g., `client.TestPlan.create`). If your library import differs, follow your local pattern.

---

## 🛠️ Common Usage Patterns

* 🔍 **filter** → retrieve serialized lists by field lookups
* ✏️ **create/update/remove** → standard CRUD flows
* 🏷️ **add/remove (tag/attachment/property/comment)** → common side operations
* 📜 **history / properties / list\_attachments** → fetch historical, metadata, and file info
* 🧰 **system.\*** → discover available methods, signatures, and inline help

Example (search and update):

```python
# Find running TestRuns and mark them completed
runs = client.TestRun.filter({"status": "running"})
for r in runs:
    client.TestRun.update(r["id"], {"status": "completed"})
```

---

## 🧰 Security & Debugging Tips

* ⛔ **PermissionDenied**: ensure the acting user has required roles/groups/permissions in Kiwi.
* 🔎 **DoesNotExist**: verify IDs/filters; prefer `filter` first to discover valid objects.
* ⚠️ **ValidationError/ValueError**: confirm schema and types—use `system.methodSignature` for guidance.
* ✉️ **Emails/Attachments**: ensure valid email formats and correct Base64 encoding.

---

## 📚 Complete API Reference (by Entity)

> **Note:** Everything you provided is included here as-is, organized and slightly polished for readability. Python-style examples use an instance named `client`.

### 📎 Attachment

#### `Attachment.remove_attachment(attachment_id: int)`

* **Description:** Removes the given attachment file.
* **Raises:** Exception if the attachment doesn’t exist or removal fails.
* **Usage:**

  ```python
  client.Attachment.remove_attachment(1)
  ```

---

### 🔐 Auth

#### `Auth.login(username: str, password: str) -> str`

* **Description:** Logs in and returns a session ID.
* **Raises:** PermissionDenied if username or password is incorrect.
* **Usage:**

  ```python
  sid = client.Auth.login("user123", "password123")
  ```

#### `Auth.logout()`

* **Description:** Deletes session information (logout).
* **Usage:**

  ```python
  client.Auth.logout()
  ```

---

### 🐞 Bug

#### `Bug.add_tag(bug_id: int, tag: str)`

* **Raises:** PermissionDenied, Bug.DoesNotExist, Tag.DoesNotExist
* **Usage:** `client.Bug.add_tag(1001, "Critical")`

#### `Bug.details(url: str) -> dict`

* **Description:** Returns details about a bug at the given URL.
* **Usage:** `details = client.Bug.details("http://.../bug/1001")`

#### `Bug.filter(query: dict) -> list`

* **Usage:** `bugs = client.Bug.filter({"status": "open"})`

#### `Bug.remove(query: dict)`

* **Raises:** PermissionDenied
* **Usage:** `client.Bug.remove({"status": "resolved"})`

#### `Bug.remove_tag(bug_id: int, tag: str)`

* **Raises:** PermissionDenied, Bug.DoesNotExist
* **Usage:** `client.Bug.remove_tag(1001, "Critical")`

#### `Bug.report(execution_id: int, tracker_id: int) -> str`

* **Description:** Returns a URL to open the bug tracker with prefilled fields referencing a TestExecution.
* **Usage:** `url = client.Bug.report(1, 2)`

---

### 🧱 Build

#### `Build.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `build = client.Build.create({"name":"v1.0","version":"1.0.0"})`

#### `Build.filter(query: dict) -> list`

* **Usage:** `client.Build.filter({"version":"1.0.0"})`

#### `Build.update(build_id: int, values: dict) -> dict`

* **Raises:** Build.DoesNotExist, PermissionDenied, ValueError
* **Usage:** `client.Build.update(101, {"version":"1.1.0","status":"active"})`

---

### 🗂️ Category

#### `Category.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `client.Category.create({"name":"Test Category","description":"..."})`

#### `Category.filter(query: dict) -> list`

* **Usage:** `client.Category.filter({"name":"Test Category"})`

---

### 🏷️ Classification

#### `Classification.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `client.Classification.create({"name":"High Priority","description":"..."})`

#### `Classification.filter(query: dict) -> list`

* **Usage:** `client.Classification.filter({"name":"High Priority"})`

---

### 🧩 Component

#### `Component.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `client.Component.create({"name":"Component A","owner":1})`

#### `Component.filter(query: dict) -> list`

* **Usage:** `client.Component.filter({"name":"Component A"})`

#### `Component.update(component_id: int, values: dict) -> dict`

* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.Component.update(101, {"name":"Updated Component"})`

---

### 🌳 Environment

#### `Environment.add_property(environment_id: int, name: str, value: str) -> dict`

* **Raises:** PermissionDenied
* **Usage:** `client.Environment.add_property(1, "OS", "Linux")`

#### `Environment.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `client.Environment.create({"name":"Production Environment","location":"USA"})`

#### `Environment.filter(query: dict) -> list`

* **Usage:** `client.Environment.filter({"location":"USA"})`

#### `Environment.properties(query: dict) -> list`

* **Raises:** PermissionDenied
* **Usage:** `client.Environment.properties({"environment_id":1})`

---

### 🥝 KiwiTCMS

#### `KiwiTCMS.version() -> str`

* **Description:** Returns current Kiwi TCMS version.
* **Usage:** `version = client.KiwiTCMS.version()`

---

### ✍️ Markdown

#### `Markdown.render(text: str) -> str`

* **Description:** Renders Markdown to HTML.
* **Usage:** `html = client.Markdown.render("# Hello World")`

---

### 🗺️ PlanType

#### `PlanType.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `client.PlanType.create({"name":"Manual Test Plan","description":"..."})`

#### `PlanType.filter(query: dict) -> list`

* **Usage:** `client.PlanType.filter({"name":"Automated Test Plan"})`

---

### ⬆️ Priority

#### `Priority.filter(query: dict) -> list`

* **Usage:** `client.Priority.filter({"level":"high"})`

---

### 📦 Product

#### `Product.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:** `client.Product.create({"name":"Test Product","description":"..."})`

#### `Product.filter(query: dict) -> list`

* **Usage:** `client.Product.filter({"name":"Test Product"})`

---

### 🏷️ Tag

#### `Tag.filter(query: dict) -> list`

* **Usage:** `client.Tag.filter({"name":"Bug"})`

---

### 🧪 TestCase

#### `TestCase.add_attachment(case_id: int, filename: str, b64content: str)`

* **Usage:** `client.TestCase.add_attachment(101, "test_log.txt", "base64...")`

#### `TestCase.add_comment(case_id: int, comment: str) -> dict`

* **Raises:** PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.add_comment(101, "This is a comment.")`

#### `TestCase.add_component(case_id: int, component: str) -> dict`

* **Raises:** PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.add_component(101, "TestComponent")`

#### `TestCase.add_notification_cc(case_id: int, cc_list: list[str])`

* **Raises:** TypeError/ValidationError, PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.add_notification_cc(101, ["a@x.com", "b@x.com"])`

#### `TestCase.add_property(case_id: int, name: str, value: str) -> dict`

* **Raises:** PermissionDenied
* **Usage:** `client.TestCase.add_property(101, "Test Property", "Some value")`

#### `TestCase.add_tag(case_id: int, tag: str)`

* **Raises:** PermissionDenied, TestCase.DoesNotExist, Tag.DoesNotExist
* **Usage:** `client.TestCase.add_tag(101, "Critical")`

#### `TestCase.comments(case_id: int) -> list`

* **Raises:** PermissionDenied, TestCase.DoesNotExist
* **Usage:** `comments = client.TestCase.comments(101)`

#### `TestCase.create(values: dict) -> dict`

* **Raises:** ValueError, PermissionDenied
* **Usage:**

  ```python
  case = client.TestCase.create({
      "category": 135,
      "product": 61,
      "summary": "Test Case Summary",
      "priority": 1
  })
  ```

#### `TestCase.filter(query: dict) -> list`

* **Usage:** `client.TestCase.filter({"priority": 1})`

#### `TestCase.get_notification_cc(case_id: int) -> list[str]`

* **Raises:** TestCase.DoesNotExist
* **Usage:** `cc = client.TestCase.get_notification_cc(101)`

#### `TestCase.history(case_id: int, query: dict) -> list`

* **Usage:** `hist = client.TestCase.history(101, {"action": "update"})`

#### `TestCase.list_attachments(case_id: int) -> list`

* **Raises:** TestCase.DoesNotExist
* **Usage:** `atts = client.TestCase.list_attachments(101)`

#### `TestCase.properties(query: dict) -> list`

* **Raises:** PermissionDenied
* **Usage:** `props = client.TestCase.properties({"case_id": 101})`

#### `TestCase.remove(query: dict) -> (int, dict)`

* **Raises:** PermissionDenied
* **Usage:** `deleted = client.TestCase.remove({"status": "inactive"})`

#### `TestCase.remove_comment(case_id: int, comment_id: int | None)`

* **Raises:** PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.remove_comment(101, 5)`

#### `TestCase.remove_component(case_id: int, component_id: int)`

* **Raises:** PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.remove_component(101, 10)`

#### `TestCase.remove_notification_cc(case_id: int, cc_list: list[str])`

* **Raises:** TypeError/ValidationError, PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.remove_notification_cc(101, ["a@x.com"])`

#### `TestCase.remove_property(query: dict)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestCase.remove_property({"case_id": 101, "name": "Test Property"})`

#### `TestCase.remove_tag(case_id: int, tag: str)`

* **Raises:** PermissionDenied, TestCase.DoesNotExist
* **Usage:** `client.TestCase.remove_tag(101, "Critical")`

#### `TestCase.sortkeys(query: dict) -> dict[case_id, sortkey]`

* **Usage:** `order = client.TestCase.sortkeys({"plan": 3})`

#### `TestCase.update(case_id: int, values: dict) -> dict`

* **Raises:** TestCase.DoesNotExist, PermissionDenied, ValueError
* **Usage:** `client.TestCase.update(101, {"summary": "Updated test case summary"})`

---

### 🔄 TestCaseStatus

#### `TestCaseStatus.filter(query: dict) -> list`

* **Usage:** `client.TestCaseStatus.filter({"status": "completed"})`

---

### ▶️ TestExecution

#### `TestExecution.add_comment(execution_id: int, comment: str) -> dict`

* **Raises:** PermissionDenied
* **Usage:** `client.TestExecution.add_comment(201, "Test execution successful.")`

#### `TestExecution.add_link(values: dict, update_tracker: bool=False) -> dict`

* **Raises:** RuntimeError, ValueError
* **Usage:** `client.TestExecution.add_link({"url": "http://example.com/test-link"}, True)`

#### `TestExecution.filter(query: dict) -> list`

* **Usage:** `client.TestExecution.filter({"status": "in_progress"})`

#### `TestExecution.get_comments(execution_id: int) -> list`

* **Raises:** PermissionDenied
* **Usage:** `client.TestExecution.get_comments(201)`

#### `TestExecution.get_links(query: dict) -> list`

* **Usage:** `client.TestExecution.get_links({"execution_id": 201})`

#### `TestExecution.history(execution_id: int) -> list`

* **Raises:** PermissionDenied
* **Usage:** `client.TestExecution.history(201)`

#### `TestExecution.properties(query: dict) -> list`

* **Usage:** `client.TestExecution.properties({"execution_id": 201})`

#### `TestExecution.remove(query: dict) -> (int, dict)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestExecution.remove({"status": "failed"})`

#### `TestExecution.remove_comment(execution_id: int, comment_id: int | None)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestExecution.remove_comment(201, 3)`

#### `TestExecution.remove_link(query: dict)`

* **Usage:** `client.TestExecution.remove_link({"execution_id": 201, "url": "http://example.com/test-link"})`

#### `TestExecution.update(execution_id: int, values: dict) -> dict`

* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.TestExecution.update(201, {"status": "completed"})`

---

### 🔁 TestExecutionStatus

#### `TestExecutionStatus.filter(query: dict) -> list`

* **Usage:** `client.TestExecutionStatus.filter({"status": "completed"})`

---

### 🗒️ TestPlan

#### `TestPlan.add_attachment(plan_id: int, filename: str, b64content: str)`

* **Usage:** `client.TestPlan.add_attachment(301, "test_plan_log.txt", "base64...")`

#### `TestPlan.add_case(plan_id: int, case_id: int) -> dict`

* **Raises:** PermissionDenied
* **Usage:** `client.TestPlan.add_case(301, 401)`

#### `TestPlan.add_tag(plan_id: int, tag_name: str)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestPlan.add_tag(301, "Smoke Test")`

#### `TestPlan.create(values: dict) -> dict`

* **Raises:** PermissionDenied, ValueError
* **Usage:**

  ```python
  plan = client.TestPlan.create({
      "product": 61,
      "product_version": 93,
      "name": "Test Plan 1",
      "type": 1,
      "parent": 150,
      "text": "Test plan for TCMS",
  })
  ```

#### `TestPlan.filter(query: dict) -> list`

* **Usage:** `client.TestPlan.filter({"name": "Test Plan 1"})`

#### `TestPlan.list_attachments(plan_id: int) -> list`

* **Raises:** TestPlan.DoesNotExist
* **Usage:** `client.TestPlan.list_attachments(301)`

#### `TestPlan.remove_case(plan_id: int, case_id: int)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestPlan.remove_case(301, 401)`

#### `TestPlan.remove_tag(plan_id: int, tag_name: str)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestPlan.remove_tag(301, "Smoke Test")`

#### `TestPlan.tree(plan_id: int) -> list`

* **Raises:** TestPlan.DoesNotExist
* **Usage:** `tree = client.TestPlan.tree(301)`

#### `TestPlan.update(plan_id: int, values: dict) -> dict`

* **Raises:** TestPlan.DoesNotExist, PermissionDenied, ValueError
* **Usage:** `client.TestPlan.update(301, {"name": "Updated Test Plan"})`

#### `TestPlan.update_case_order(plan_id: int, case_id: int, sortkey: int)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestPlan.update_case_order(301, 401, 10)`

---

### 🏃 TestRun

#### `TestRun.add_attachment(run_id: int, filename: str, b64content: str)`

* **Usage:** `client.TestRun.add_attachment(501, "test_run_log.txt", "base64...")`

#### `TestRun.add_case(run_id: int, case_id: int) -> list`

* **Raises:** PermissionDenied, RuntimeError (if TestCase status isn’t **CONFIRMED**)
* **Usage:** `client.TestRun.add_case(501, 601)`

#### `TestRun.add_cc(run_id: int, username: str)`

* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.TestRun.add_cc(501, "testuser@example.com")`

#### `TestRun.add_tag(run_id: int, tag: str)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestRun.add_tag(501, "Regression")`

#### `TestRun.create(values: dict) -> dict`

* **Raises:** PermissionDenied, ValueError
* **Usage:**

  ```python
  run = client.TestRun.create({
      "build": 384,
      "manager": 137,
      "plan": 137,
      "summary": "Testing XML-RPC for TCMS"
  })
  ```

#### `TestRun.filter(query: dict) -> list`

* **Usage:** `client.TestRun.filter({"status": "running"})`

#### `TestRun.get_cases(run_id: int) -> list`

* **Description:** Returns attached TestCases, each augmented with `execution_id` and `status`.
* **Usage:** `cases = client.TestRun.get_cases(501)`

#### `TestRun.properties(query: dict) -> list`

* **Raises:** PermissionDenied
* **Usage:** `client.TestRun.properties({"run_id": 501})`

#### `TestRun.remove(query: dict) -> (int, dict)`

* **Raises:** PermissionDenied
* **Usage:** `client.TestRun.remove({"status": "failed"})`

#### `TestRun.remove_case(run_id: int, case_id: int)` *(Deprecated; prefer `TestExecution.remove()` instead)*

* **Usage:** `client.TestRun.remove_case(501, 601)`

#### `TestRun.remove_cc(run_id: int, username: str)`

* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.TestRun.remove_cc(501, "testuser@example.com")`

#### `TestRun.remove_tag(run_id: int, tag_name: str)`

* **Raises:** PermissionDenied, TestRun.DoesNotExist
* **Usage:** `client.TestRun.remove_tag(501, "Smoke Test")`

#### `TestRun.update(run_id: int, values: dict) -> dict`

* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.TestRun.update(501, {"status": "completed"})`

---

### 📈 Testing

#### `Testing.breakdown(query: dict) -> dict`

* **Description:** Returns statistics for selected TestCases.
* **Usage:** `stats = client.Testing.breakdown({"status": "completed"})`

#### `Testing.execution_trends(...)`

* **Description:** Analyzes execution trends (parameters/return shape not specified in your source).
* **Usage:** `trends = client.Testing.execution_trends(query)`

#### `Testing.individual_test_case_health(...)`

* **Description:** Analyzes health of individual test cases (details not specified).
* **Usage:** `health = client.Testing.individual_test_case_health(query)`

#### `Testing.status_matrix(query: dict) -> dict`

* **Description:** Returns dataset for visualizing status matrix across plans/cases/executions.
* **Usage:** `matrix = client.Testing.status_matrix({"status": "active"})`

#### `Testing.test_case_health(...)`

* **Description:** Returns health status analysis for test cases (details not specified).
* **Usage:** `health = client.Testing.test_case_health(query)`

---

### 👤 User

#### `User.add_attachment(filename: str, b64content: str) -> dict`

* **Description:** Attaches a file to the currently logged-in user.
* **Usage:** `client.User.add_attachment("user_log.txt", "base64...")`

#### `User.filter(query: dict) -> list`

* **Description:** Returns serialized user object (without password).
* **Usage:** `client.User.filter({"email": "user@example.com"})`

#### `User.join_group(username: str, groupname: str)`

* **Raises:** PermissionDenied
* **Usage:** `client.User.join_group("user123", "admins")`

#### `User.update(user_id: int, values: dict) -> dict`

* **Description:** Updates user fields (including password).
* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.User.update(101, {"email": "newuser@example.com"})`

---

### 🔖 Version

#### `Version.create(values: dict) -> dict`

* **Raises:** PermissionDenied, ValueError
* **Usage:** `client.Version.create({"value": "v2.0", "product": 272})`

#### `Version.filter(query: dict) -> list`

* **Usage:** `client.Version.filter({"product": 272})`

---

### 🧰 system.\*

#### `system.listMethods() -> list[str]`

* **Usage:** `methods = client.system.listMethods()`

#### `system.methodHelp(method_name: str) -> str`

* **Usage:** `helptext = client.system.methodHelp("TestRun.add_case")`

#### `system.methodSignature(method_name: str) -> list`

* **Usage:** `sig = client.system.methodSignature("TestRun.add_case")`

#### `system.multicall(methods: list[list]) -> list`

* **Usage:**

  ```python
  results = client.system.multicall([
      ["TestRun.add_case", [501, 601]],
      ["TestExecution.update", [201, {"status": "completed"}]],
  ])
  ```

---

## 🧾 Appendix: Quick Triage Checklist

* 🔐 **401 / PermissionDenied** → check user roles/groups/permissions in Kiwi.
* 🧭 **DoesNotExist** → verify IDs/filters; run a `filter` first to discover valid objects.
* 🧪 **ValueError / ValidationError** → confirm schema/types; inspect with `system.methodSignature`.
* 📎 **Emails / Attachments** → validate email formats; ensure correct Base64 encoding.

---