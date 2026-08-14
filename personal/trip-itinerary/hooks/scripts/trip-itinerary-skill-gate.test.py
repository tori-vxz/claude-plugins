#!/usr/bin/env python3
"""Regression suite for trip-itinerary-skill-gate.sh.

Run:  python3 hooks/scripts/trip-itinerary-skill-gate.test.py

WHY THIS EXISTS. The defect this hook closes first surfaced in the sibling
`bps` plugin: on 2026-07-28 a headless run showed a `doc-reader` spawn read
its opening `/bps:doc-map` as ordinary prose and never called the `Skill`
tool — it produced output from the spawn prompt's fields alone. The shape
happened to come out right, so nothing caught it, and a wrong shape would
have passed identically. The same failure mode reaches trip's own
gated subagents: a spawn could just as easily read its opening slash
command as prose and never call `Skill` either. This hook is the check; this
file is what proves the check actually fires on the failure it exists for,
and stays silent on everything it must not touch.

Each test builds a synthetic subagent transcript (`.jsonl`) in a temp
directory, then feeds a synthetic SubagentStop payload to the hook and
inspects its stdout: empty stdout means "allowed", a JSON object with a
`reason` means "blocked".
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = str(Path(__file__).with_name("trip-itinerary-skill-gate.sh"))


def transcript(tmpdir, lines):
    """Write `lines` (already-JSON-encodable dicts or raw strings) as a
    newline-delimited transcript file and return its path."""
    path = Path(tmpdir) / "transcript.jsonl"
    with open(path, "w") as f:
        for line in lines:
            if isinstance(line, str):
                f.write(line + "\n")
            else:
                f.write(json.dumps(line) + "\n")
    return str(path)


def user_msg(content):
    return {"type": "user", "message": {"role": "user", "content": content}}


def assistant_text(text):
    return {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": text}]},
    }


def assistant_skill(skill_name):
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": skill_name}}
            ],
        },
    }


def queue_op():
    """A line with no `message` object — must be ignored, not error."""
    return {"type": "queue-operation", "op": "flush"}


def fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=None,
          stop_hook_active=False, raw=None):
    """Run the hook; return 'allowed' or the parsed block reason string."""
    if raw is None:
        payload = {
            "agent_type": agent_type,
            "agent_transcript_path": agent_transcript_path,
            "stop_hook_active": stop_hook_active,
            "transcript_path": "/nonexistent-main-transcript",
            "last_assistant_message": "",
        }
        raw = json.dumps(payload)
    p = subprocess.run(["bash", HOOK], input=raw, capture_output=True, text=True)
    if p.returncode != 0:
        return "ERROR:%d:%s" % (p.returncode, p.stderr[-300:])
    if not p.stdout.strip():
        return "allowed"
    try:
        out = json.loads(p.stdout)
    except Exception:
        return "ERROR:bad-json:%s" % p.stdout[:300]
    return out.get("reason", "")


CASES = []


def case(name, fn):
    CASES.append((name, fn))


# --- 1. expected skill loaded -> silent -------------------------------------
def t_expected_loaded(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: expected skill actually loaded"),
        assistant_skill("trip-itinerary:trip-scout"),
        assistant_text("Here is the result."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got == "allowed", "expected allow, got: %r" % got


case("expected skill loaded -> silent", t_expected_loaded)


# --- 2. a different skill loaded -> blocks, names both ----------------------
def t_wrong_skill(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquestion: what changed?"),
        assistant_skill("trip-itinerary:other-skill"),
        assistant_text("Answered the question."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got != "allowed" and not got.startswith("ERROR"), "expected block, got: %r" % got
    assert "trip-itinerary:trip-scout" in got, "reason must name the expected skill: %r" % got
    assert "trip-itinerary:other-skill" in got, "reason must name the actual skill: %r" % got


case("different skill loaded -> blocks naming both", t_wrong_skill)


# --- 3. no Skill call at all -> blocks --------------------------------------
def t_no_skill_call(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: worked out by hand"),
        assistant_text("Here is the result, worked out by hand."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got != "allowed" and not got.startswith("ERROR"), "expected block, got: %r" % got
    assert "trip-itinerary:trip-scout" in got
    assert "Skill" in got


case("no Skill call at all -> blocks", t_no_skill_call)


# --- 4. prose spawn prompt, no slash command -> silent ----------------------
def t_prose_no_slash(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("Please do this and tell me what you find."),
        assistant_text("Here is the result."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got == "allowed", "expected allow, got: %r" % got


case("prose spawn prompt, no slash command -> silent", t_prose_no_slash)


# --- 5. stop_hook_active true caps the retry at one -------------------------
def t_stop_hook_active(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nfiles: x.md"),
        assistant_text("Answered it without loading anything."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath, stop_hook_active=True)
    assert got == "allowed", "expected allow (one-bounce cap), got: %r" % got


case("stop_hook_active true with failing transcript -> silent", t_stop_hook_active)


# --- 6. agent_type outside the gated set -> silent --------------------------
def t_ungated_agent(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nfiles: x.md"),
        assistant_text("Answered it without loading anything."),
    ])
    got = fire(agent_type="core:runner", agent_transcript_path=tpath)
    assert got == "allowed", "expected allow, got: %r" % got


case("agent_type core:runner with failing transcript -> silent", t_ungated_agent)


# --- 7. agent_transcript_path missing -> silent -----------------------------
def t_missing_transcript(tmpdir):
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path="/nonexistent/path.jsonl")
    assert got == "allowed", "expected allow, got: %r" % got


case("agent_transcript_path nonexistent -> silent", t_missing_transcript)


# --- 8. unparseable / message-less lines alongside a valid Skill call ------
def t_noisy_but_valid(tmpdir):
    path = Path(tmpdir) / "transcript.jsonl"
    with open(path, "w") as f:
        f.write("this is not json at all {{{\n")
        f.write(json.dumps(queue_op()) + "\n")
        f.write(json.dumps(user_msg("/trip-itinerary:trip-scout\n\nquery: noisy transcript")) + "\n")
        f.write("also not json ][\n")
        f.write(json.dumps({"type": "summary", "text": "..."}) + "\n")
        f.write(json.dumps(assistant_skill("trip-itinerary:trip-scout")) + "\n")
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=str(path))
    assert got == "allowed", "expected allow, got: %r" % got


case("unparseable/message-less lines alongside valid Skill call -> silent", t_noisy_but_valid)


# --- 9. first user message content is a bare string, not block list --------
def t_bare_string_content(tmpdir):
    # content is a plain string, matching what payloads carry when the
    # subagent's first message has no block structure at all.
    tpath = transcript(tmpdir, [
        {"type": "user", "message": {"role": "user", "content": "/trip-itinerary:trip-scout\n\nfiles: [a, b]"}},
        assistant_skill("trip-itinerary:trip-scout"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got == "allowed", "expected allow (string content handled), got: %r" % got


case("bare string content on first user message -> handled", t_bare_string_content)


# --- extra: bare string content that still fails should still block --------
def t_bare_string_content_wrong(tmpdir):
    tpath = transcript(tmpdir, [
        {"type": "user", "message": {"role": "user", "content": "/trip-itinerary:trip-scout\n\nfiles: [a, b]"}},
        assistant_skill("trip-itinerary:other-skill"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got != "allowed" and not got.startswith("ERROR"), "expected block, got: %r" % got
    assert "trip-itinerary:trip-scout" in got and "trip-itinerary:other-skill" in got


case("bare string content, wrong skill -> blocks", t_bare_string_content_wrong)


# --- extra: leading blank line before the slash command is still line 1 ----
def t_leading_blank_line(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("\n/trip-itinerary:trip-scout\n\nquery: leading blank line"),
        assistant_skill("trip-itinerary:trip-scout"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got == "allowed", "expected allow, got: %r" % got


case("leading blank line before slash command -> still recognized", t_leading_blank_line)


# --- extra: agent_transcript_path key absent entirely -> silent ------------
def t_missing_transcript_key(tmpdir):
    payload = {
        "agent_type": "trip-itinerary:trip-scout",
        "stop_hook_active": False,
        "transcript_path": "/nonexistent-main-transcript",
    }
    got = fire(raw=json.dumps(payload))
    assert got == "allowed", "expected allow, got: %r" % got


case("agent_transcript_path key absent entirely -> silent", t_missing_transcript_key)


# --- extra: unparseable payload on stdin -> silent --------------------------
def t_garbage_payload(tmpdir):
    got = fire(raw="not json at all {{{")
    assert got == "allowed", "expected allow, got: %r" % got


case("unparseable payload -> silent", t_garbage_payload)


# --- extra: second gated agent type, expected skill loaded -> silent -------
def t_second_agent_expected_loaded(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: second gated agent type"),
        assistant_skill("trip-itinerary:trip-scout"),
        assistant_text("Here is the result."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got == "allowed", "expected allow, got: %r" % got


case("second gated agent type, expected skill loaded -> silent", t_second_agent_expected_loaded)


# --- extra: second gated agent type, no Skill call at all -> blocks ---------
def t_second_agent_no_skill_call(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: second gated agent type"),
        assistant_text("Found the result by hand, without loading anything."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got != "allowed" and not got.startswith("ERROR"), "expected block, got: %r" % got
    assert "trip-itinerary:trip-scout" in got
    assert "Skill" in got


case("second gated agent type, no Skill call at all -> blocks", t_second_agent_no_skill_call)


# --- 13. regression guard: qualified slash command, no Skill call -> blocks
# This is the specific case that would have caught the old bare
# `^/([a-z0-9-]+)$` regex silently failing open on a namespaced slash
# command like `/trip-itinerary:trip-scout` (the colon isn't in that character class, so
# the match fails, the script falls into its "no slash command" allow
# branch, and the gate protects nothing). Under the fixed regex this must
# block.
def t_qualified_slash_no_skill_call(tmpdir):
    tpath = transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: regex regression guard"),
        assistant_text("Here is the result, worked out by hand."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", agent_transcript_path=tpath)
    assert got != "allowed" and not got.startswith("ERROR"), "expected block, got: %r" % got
    assert "trip-itinerary:trip-scout" in got
    assert "Skill" in got


case("qualified slash command trip-itinerary:trip-scout, no Skill call -> blocks (regex regression guard)",
     t_qualified_slash_no_skill_call)


def main():
    fails = 0
    for name, fn in CASES:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                fn(tmpdir)
            except AssertionError as e:
                fails += 1
                print("FAIL %-60s %s" % (name, e))
            except Exception as e:
                fails += 1
                print("FAIL %-60s unexpected %s: %s" % (name, type(e).__name__, e))
            else:
                print("PASS %-60s" % name)

    print("\n%d/%d correct" % (len(CASES) - fails, len(CASES)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
