import functools

import pytest
from axe_core_python.sync_playwright import Axe
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module", autouse=True)
def live_app(app, live_server):
    pass


def snapshot_to_dict(snapshot: str):
    snapshot_counts = {}
    for line in snapshot.split("\n"):
        key, count = line.split(" : ")
        snapshot_counts[key] = int(count)
    return snapshot_counts


def compare_violations(new_snapshot, old_snapshot, new_results):
    new_counts = snapshot_to_dict(new_snapshot)
    old_counts = snapshot_to_dict(old_snapshot)
    seen_keys = set()
    keys_diff = {"added": set(), "removed": set(), "increased": set(), "decreased": set()}
    for key in old_counts:
        if key not in new_counts:
            keys_diff["removed"].add(key)
        elif new_counts[key] < old_counts[key]:
            keys_diff["decreased"].add(key)
        elif new_counts[key] > old_counts[key]:
            keys_diff["increased"].add(key)
        seen_keys.add(key)
    for key in new_counts:
        if key not in seen_keys:
            keys_diff["added"].add(key)
    good_msg = "That's good news! 🎉 Run `pytest --snapshot-update` to update the snapshots.\n"
    bad_msg = "That's bad news! 😱 Either fix the issue or run `pytest --snapshot-update` to update the snapshots.\n"
    message = "\n"
    if len(keys_diff["added"]) > 0:
        message += f"New violations found: {','.join(keys_diff['added'])}\n{bad_msg}"
        for violation in keys_diff["added"]:
            violation_id = violation.split(" (")[0]
            message += new_results.generate_report(violation_id=violation_id)
    if len(keys_diff["removed"]) > 0:
        message += f"Old violations no longer found: {','.join(keys_diff['removed'])}.\n{good_msg}"
    if len(keys_diff["increased"]) > 0:
        message += (
            f"Additional instances of existing violations were found: {','.join(keys_diff['increased'])}\n{bad_msg}"
        )
        for violation in keys_diff["increased"]:
            violation_id = violation.split(" (")[0]
            message += new_results.generate_report(violation_id=violation_id)
    if len(keys_diff["decreased"]) > 0:
        message += f"Fewer instances of existing violations were found: {','.join(keys_diff['decreased'])}.\n{good_msg}"
    return message


@pytest.fixture
def axe_pytest_snapshot(snapshot):
    def run_assert(page: Page):
        results = Axe().run(page)
        snapshot.assert_match(
            results.generate_snapshot(), message_generator=functools.partial(compare_violations, new_results=results)
        )

    return run_assert


def test_index(page: Page, axe_pytest_snapshot):
    page.goto(url_for("quizzes.index", _external=True))
    axe_pytest_snapshot(page)


def test_quiz(page: Page, snapshot, fake_quiz, axe_pytest_snapshot):
    page.goto(url_for("quizzes.quiz", quiz_id=fake_quiz.id, _external=True))
    axe_pytest_snapshot(page)


def test_quiz_submit(page: Page, snapshot, fake_quiz, axe_pytest_snapshot):
    page.goto(url_for("quizzes.quiz", quiz_id=fake_quiz.id, _external=True))
    page.get_by_label("Your name:").click()
    page.get_by_label("Your name:").fill("Pamela")
    page.get_by_label("Ada Lovelace").check()
    page.get_by_label("pip").check()
    page.get_by_role("button", name="Submit your score!").click()
    expect(page.locator("#score")).to_contain_text("You scored 25% on the quiz.")
    axe_pytest_snapshot(page)
