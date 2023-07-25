import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module", autouse=True)
def live_app(app, live_server):
    pass


def test_index(page: Page, fake_quiz, axe_pytest_snapshot):
    page.goto(url_for("quizzes.index", _external=True))
    axe_pytest_snapshot(page)


def test_quiz(page: Page, fake_quiz, axe_pytest_snapshot):
    page.goto(url_for("quizzes.quiz", quiz_id=fake_quiz.id, _external=True))
    expect(page.locator("#scores")).not_to_contain_text("Loading...")
    axe_pytest_snapshot(page)


def test_quiz_submit(page: Page, fake_quiz, axe_pytest_snapshot):
    page.goto(url_for("quizzes.quiz", quiz_id=fake_quiz.id, _external=True))
    page.get_by_label("Your name:").click()
    page.get_by_label("Your name:").fill("Pamela")
    page.get_by_label("Ada Lovelace").check()
    page.get_by_label("pip").check()
    page.get_by_role("button", name="Submit your score!").click()
    expect(page.locator("#score")).to_contain_text("You scored 25% on the quiz.")
    axe_pytest_snapshot(page)
