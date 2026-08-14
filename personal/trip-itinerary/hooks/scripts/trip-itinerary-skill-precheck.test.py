#!/usr/bin/env python3
"""Regression suite for trip-itinerary-skill-precheck.sh.

Run:  python3 hooks/scripts/trip-itinerary-skill-precheck.test.py

WHY THIS EXISTS. trip-itinerary-skill-gate.sh (see its own test suite) catches a gated
subagent that skipped the `Skill` tool call its spawn prompt demanded — but
only at SubagentStop, after the subagent has already spent an entire lane of
work producing output in the wrong shape. That risk first surfaced in the
sibling `bps` plugin, where headless runs on 2026-07-28 and after showed a
`doc-reader` spawn read `/bps:doc-map` as ordinary prose, never called
`Skill`, and produced ~28 file reads' worth of output in the wrong shape
before `trip-itinerary-skill-gate.sh` bounced it back. trip-itinerary-skill-precheck.sh is the
PreToolUse counterpart: it refuses every tool call except `Skill` until the
right `Skill` call has actually happened, so the wasted work never happens
in the first place. This file proves that gate fires on the failure it
exists for, never deadlocks on the `Skill` call it demands, and stays silent
everywhere it must not touch.

Each test builds a synthetic subagent transcript tree — the hook derives the
subagent's own transcript path from `transcript_path` + `session_id` +
`agent_id` rather than being handed it directly, so the fixture must lay out
`<tmp>/<session_id>/subagents/agent-<agent_id>.jsonl` alongside
`<tmp>/<session_id>.jsonl` for that derivation to land correctly. It then
feeds a synthetic PreToolUse payload to the hook and inspects its stdout:
empty stdout means "allowed", a JSON object with
`hookSpecificOutput.permissionDecisionReason` means "denied".
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = str(Path(__file__).with_name("trip-itinerary-skill-precheck.sh"))

SESSION_ID = "b63888c6-fb02-4c71-b156-4db34c7e9ade"
AGENT_ID = "a9b1c6985282c2740"


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


def tool_result(content):
    """A user-role message carrying a single tool_result block. `content`
    may be a plain string or a list of {"type": "text", "text": ...} blocks,
    matching the two shapes a real transcript uses."""
    return {
        "type": "user",
        "message": {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "toolu_x", "content": content}
            ],
        },
    }


def build_subagent_transcript(tmpdir, lines, session_id=SESSION_ID, agent_id=AGENT_ID):
    """Lay out <tmp>/<session_id>/subagents/agent-<agent_id>.jsonl, plus a
    stub parent transcript at <tmp>/<session_id>.jsonl, and return the
    (transcript_path, session_id, agent_id) triple the hook needs to derive
    the subagent transcript path itself."""
    tmp = Path(tmpdir)
    parent_transcript = tmp / (session_id + ".jsonl")
    parent_transcript.write_text("")  # parent transcript content is irrelevant
    subdir = tmp / session_id / "subagents"
    subdir.mkdir(parents=True, exist_ok=True)
    sub_path = subdir / ("agent-%s.jsonl" % agent_id)
    with open(sub_path, "w") as f:
        for line in lines:
            if isinstance(line, str):
                f.write(line + "\n")
            else:
                f.write(json.dumps(line) + "\n")
    return str(parent_transcript), session_id, agent_id


def fire(agent_type="trip-itinerary:trip-scout", tool_name="Read", transcript_path=None,
         session_id=None, agent_id=None, raw=None):
    """Run the hook; return 'allowed' or the parsed
    permissionDecisionReason string."""
    if raw is None:
        payload = {
            "session_id": session_id,
            "transcript_path": transcript_path,
            "cwd": "/nonexistent-cwd",
            "prompt_id": "p1",
            "permission_mode": "default",
            "agent_id": agent_id,
            "agent_type": agent_type,
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": {},
            "tool_use_id": "toolu_1",
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
    return out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")


CASES = []


def case(name, fn):
    CASES.append((name, fn))


# --- 1. expected skill already loaded -> allow ------------------------------
def t_expected_loaded(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: expected skill already loaded"),
        assistant_skill("trip-itinerary:trip-scout"),
        assistant_text("Here is the result."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="WebSearch",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("expected skill already loaded -> allow", t_expected_loaded)


# --- 2. gated agent, no Skill call at all, tool_name Read -> deny -----------
def t_no_skill_call(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: no skill call at all"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got != "allowed" and not got.startswith("ERROR"), "expected deny, got: %r" % got
    assert "trip-itinerary:trip-scout" in got
    assert "Skill" in got


case("gated agent, no Skill call, tool_name Read -> deny", t_no_skill_call)


# --- 3. gated agent, different skill loaded -> deny naming both ------------
def t_wrong_skill(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquestion: what changed?"),
        assistant_skill("trip-itinerary:other-skill"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got != "allowed" and not got.startswith("ERROR"), "expected deny, got: %r" % got
    assert "trip-itinerary:trip-scout" in got, "reason must name the expected skill: %r" % got
    assert "trip-itinerary:other-skill" in got, "reason must name the actual skill: %r" % got


case("gated agent, different skill loaded -> deny naming both", t_wrong_skill)


# --- 4. tool_name is Skill, no prior Skill call -> allow (deadlock guard) --
def t_skill_call_itself_allowed(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: deadlock guard"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Skill",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow (deadlock guard), got: %r" % got


case("tool_name Skill itself, no prior Skill call -> allow (deadlock guard)",
     t_skill_call_itself_allowed)


# --- 5. agent_type core:runner with an otherwise-failing transcript -------
def t_ungated_agent(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nfiles: x.md"),
    ])
    got = fire(agent_type="core:runner", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("agent_type core:runner with failing transcript -> allow", t_ungated_agent)


# --- 6. first user message is prose, no slash command -> allow -------------
def t_prose_no_slash(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("Please do this and tell me what you find."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("prose spawn prompt, no slash command -> allow", t_prose_no_slash)


# --- 7. subagent transcript file does not exist -> allow -------------------
def t_missing_transcript_file(tmpdir):
    tmp = Path(tmpdir)
    tp = str(tmp / (SESSION_ID + ".jsonl"))
    tp_file = Path(tp)
    tp_file.write_text("")
    # deliberately do NOT create <tmp>/<session_id>/subagents/agent-<id>.jsonl
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=SESSION_ID, agent_id=AGENT_ID)
    assert got == "allowed", "expected allow, got: %r" % got


case("subagent transcript file does not exist -> allow", t_missing_transcript_file)


# --- 8. agent_id missing from payload -> allow ------------------------------
def t_missing_agent_id(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: agent_id missing"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=None)
    assert got == "allowed", "expected allow, got: %r" % got


case("agent_id missing from payload -> allow", t_missing_agent_id)


# --- 9. session_id missing from payload -> allow ----------------------------
def t_missing_session_id(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: session_id missing"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=None, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("session_id missing from payload -> allow", t_missing_session_id)


# --- 10. transcript_path missing from payload -> allow ----------------------
def t_missing_transcript_path(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: transcript_path missing"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=None, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("transcript_path missing from payload -> allow", t_missing_transcript_path)


# --- 11. unparseable payload on stdin -> allow ------------------------------
def t_garbage_payload(tmpdir):
    got = fire(raw="not json at all {{{")
    assert got == "allowed", "expected allow, got: %r" % got


case("unparseable payload on stdin -> allow", t_garbage_payload)


# --- 12. one tool_result carries the marker -> still deny -------------------
def t_one_marker_hit_still_denies(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: one marker hit"),
        assistant_text("I will call Read now."),
        tool_result("[trip-itinerary-skill-gate] Your spawn prompt opened with `/trip-itinerary:trip-scout`..."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got != "allowed" and not got.startswith("ERROR"), "expected deny, got: %r" % got
    assert "trip-itinerary:trip-scout" in got


case("one tool_result marker hit -> still deny", t_one_marker_hit_still_denies)


# --- 13. two tool_results carry the marker -> allow (loop guard) -----------
def t_two_marker_hits_allow(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: two marker hits"),
        assistant_text("Attempt 1."),
        tool_result("[trip-itinerary-skill-gate] denial number one"),
        assistant_text("Attempt 2, still no Skill call."),
        tool_result([{"type": "text", "text": "[trip-itinerary-skill-gate] denial number two"}]),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow (loop guard tripped), got: %r" % got


case("two tool_result marker hits -> allow (loop guard)", t_two_marker_hits_allow)


# --- 14. marker only inside assistant text blocks, twice, no tool_result ---
# Regression guard for the over-count trap: the model often quotes a denial
# reason back in its own next text block. If the hook counted text blocks
# too, this transcript (which has the marker twice, purely in text, and no
# real tool_result) would trip the loop guard and allow through — wrongly.
# It must still deny.
def t_marker_only_in_text_blocks_still_denies(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: marker only in text blocks"),
        assistant_text("[trip-itinerary-skill-gate] I was told this once."),
        assistant_text("[trip-itinerary-skill-gate] I was told this again, quoting myself."),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got != "allowed" and not got.startswith("ERROR"), (
        "regression: marker in text blocks must NOT count toward the loop "
        "guard, got: %r" % got
    )
    assert "trip-itinerary:trip-scout" in got


case("marker twice in text blocks only, no tool_result -> still denies (overcount regression guard)",
     t_marker_only_in_text_blocks_still_denies)


# --- 15. first user message content is a bare string, not block list -------
def t_bare_string_content(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        {"type": "user", "message": {"role": "user", "content": "/trip-itinerary:trip-scout\n\nfiles: [a, b]"}},
        assistant_skill("trip-itinerary:trip-scout"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Edit",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow (string content handled), got: %r" % got


case("bare string content on first user message -> handled", t_bare_string_content)


# --- 16. leading blank line before the slash command is still line 1 -------
def t_leading_blank_line(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("\n/trip-itinerary:trip-scout\n\nquery: leading blank line"),
        assistant_skill("trip-itinerary:trip-scout"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Grep",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("leading blank line before slash command -> still recognized", t_leading_blank_line)


# --- 17. regression guard: qualified slash command, no Skill call -> deny
def t_qualified_slash_no_skill_call(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nfiles: regex-regression.md"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Write",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got != "allowed" and not got.startswith("ERROR"), "expected deny, got: %r" % got
    assert "trip-itinerary:trip-scout" in got
    assert "Skill" in got


case("qualified slash command trip-itinerary:trip-scout, no Skill call -> deny (regex regression guard)",
     t_qualified_slash_no_skill_call)


# --- 18. second gated agent type variant --------------------------------------
def t_second_agent_expected_loaded(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: second agent variant"),
        assistant_skill("trip-itinerary:trip-scout"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="WebFetch",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got == "allowed", "expected allow, got: %r" % got


case("trip-itinerary:trip-scout expected skill loaded -> allow", t_second_agent_expected_loaded)


def t_second_agent_no_skill_call(tmpdir):
    tp, sid, aid = build_subagent_transcript(tmpdir, [
        user_msg("/trip-itinerary:trip-scout\n\nquery: second agent variant"),
    ])
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="WebFetch",
               transcript_path=tp, session_id=sid, agent_id=aid)
    assert got != "allowed" and not got.startswith("ERROR"), "expected deny, got: %r" % got
    assert "trip-itinerary:trip-scout" in got
    assert "Skill" in got


case("trip-itinerary:trip-scout no Skill call at all -> deny", t_second_agent_no_skill_call)


# --- 19. unparseable/message-less lines alongside a valid Skill call -------
def t_noisy_but_valid(tmpdir):
    tmp = Path(tmpdir)
    parent_transcript = tmp / (SESSION_ID + ".jsonl")
    parent_transcript.write_text("")
    subdir = tmp / SESSION_ID / "subagents"
    subdir.mkdir(parents=True, exist_ok=True)
    sub_path = subdir / ("agent-%s.jsonl" % AGENT_ID)
    with open(sub_path, "w") as f:
        f.write("this is not json at all {{{\n")
        f.write(json.dumps(queue_op()) + "\n")
        f.write(json.dumps(user_msg("/trip-itinerary:trip-scout\n\nquery: noisy transcript")) + "\n")
        f.write("also not json ][\n")
        f.write(json.dumps({"type": "summary", "text": "..."}) + "\n")
        f.write(json.dumps(assistant_skill("trip-itinerary:trip-scout")) + "\n")
    got = fire(agent_type="trip-itinerary:trip-scout", tool_name="Read",
               transcript_path=str(parent_transcript), session_id=SESSION_ID, agent_id=AGENT_ID)
    assert got == "allowed", "expected allow, got: %r" % got


case("unparseable/message-less lines alongside valid Skill call -> allow", t_noisy_but_valid)


def main():
    fails = 0
    for name, fn in CASES:
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                fn(tmpdir)
            except AssertionError as e:
                fails += 1
                print("FAIL %-70s %s" % (name, e))
            except Exception as e:
                fails += 1
                print("FAIL %-70s unexpected %s: %s" % (name, type(e).__name__, e))
            else:
                print("PASS %-70s" % name)

    print("\n%d/%d correct" % (len(CASES) - fails, len(CASES)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
