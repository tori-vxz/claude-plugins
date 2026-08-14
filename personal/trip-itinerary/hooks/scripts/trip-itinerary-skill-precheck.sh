#!/usr/bin/env bash
# PreToolUse hook — the pre-emptive counterpart to trip-itinerary-skill-gate.sh. That
# SubagentStop hook closes the same defect this one does, but only at the
# moment the subagent finishes: a spawn prompt whose line 1 names a skill
# (e.g. `/trip-itinerary:<skill>`) tells the subagent which skill it must run,
# but naming it is not loading it, and a subagent that skips the `Skill`
# call can burn an entire lane of work. The defect first surfaced in the
# sibling `bps` plugin, where headless runs on 2026-07-28 and after showed a
# `doc-reader` spawn read its opening `/bps:doc-map` as ordinary prose, never
# called `Skill`, and produced ~28 file reads' worth of output in the wrong
# shape before `trip-itinerary-skill-gate.sh` bounced it back. The bounce is real work
# saved only relative to shipping the wrong shape onward — the ~28 reads
# already happened. The same failure mode reaches every gated subagent in
# trip-itinerary: a spawn that reads its opening slash command as prose could run
# some other tool straight from the prompt fields, in the wrong shape, before
# anything catches it. This hook stops that spend before it starts: it runs
# ahead of every tool call a gated subagent makes and refuses anything but
# `Skill` until the right one has actually been called. Denial is free; the
# reads it prevents are not.
#
# WHAT IT BLOCKS: a gated subagent (`trip-itinerary:trip-scout`) whose spawn prompt
# opened with a recognizable slash command, calling any tool other than
# `Skill` before its transcript shows a `Skill` call for the skill that
# command named.
#
# WHAT IT NEVER GATES: the `Skill` call itself. Refusing the very tool call
# a subagent needs to make in order to satisfy the gate would deadlock the
# subagent — every `tool_name == "Skill"` request is let through before any
# other check runs, full stop, regardless of agent type or transcript state.
#
# THE SUBAGENT'S OWN TRANSCRIPT: `transcript_path` in a PreToolUse payload is
# the PARENT session's transcript, not this subagent's — reading it would show
# none of the subagent's own tool calls. The subagent's transcript instead
# lives at a path this hook must construct itself:
#   <dirname(transcript_path)>/<session_id>/subagents/agent-<agent_id>.jsonl
# If `transcript_path`, `session_id`, or `agent_id` is missing, or the
# resulting file can't be opened, that is not evidence of anything — it fails
# open the same as every other unreadable-state case below.
#
# THE LOOP GUARD: a denial's reason lands in the subagent's own transcript as
# a `tool_result` block, and the model often quotes that reason back in its
# own next `text` block — so counting *any* transcript line containing the
# marker double-counts every denial. This hook counts only `tool_result`
# blocks that carry the literal marker `[trip-itinerary-skill-gate]`, never `text`
# blocks, and once that count reaches 2 it allows the call through
# unconditionally and leaves the rest to `trip-itinerary-skill-gate.sh`. Two denials
# have made the point already; forcing a third would wedge the subagent in a
# loop, which is worse than the defect this hook exists to catch.
#
# WHAT ELSE IT DELIBERATELY DOES NOT CHECK: a spawn prompt with no leading
# slash command (nothing to gate against — out of scope by design, same as
# trip-itinerary-skill-gate.sh), and any agent outside the gated set (passes
# through untouched, even on a failing transcript).
#
# SAFETY: fails open, not closed. An unreadable payload, a missing or
# unreadable subagent transcript, an unrecognized agent type, the absence of
# a slash command, or the loop guard tripping — all of these allow the tool
# call silently. A gate that fails closed on a missing file wedges the whole
# pipeline for a subagent that did nothing wrong.
#
# The payload arrives via $PAYLOAD rather than stdin so the heredoc below can
# stay single-quoted and the Python body can contain apostrophes freely.
#
# Contract (PreToolUse): print
# {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":
# "deny","permissionDecisionReason":"..."}} on stdout with exit 0 to refuse
# the tool call and hand the subagent `permissionDecisionReason` as its next
# instruction; exit 0 printing nothing lets the tool call proceed.

payload=$(cat)

PAYLOAD="$payload" python3 <<'PYEOF'
import sys, json, re, os

GATED_AGENTS = {"trip-itinerary:trip-scout"}
MARKER = "[trip-itinerary-skill-gate]"


def allow():
    sys.exit(0)


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


try:
    payload = json.loads(os.environ.get("PAYLOAD") or "")
except Exception:
    allow()

if not isinstance(payload, dict):
    allow()

# --- never gate the Skill call itself, or this deadlocks the subagent ----
tool_name = payload.get("tool_name") or ""
if tool_name == "Skill":
    allow()

# --- agent scope -----------------------------------------------------------
agent_type = payload.get("agent_type") or ""
if agent_type not in GATED_AGENTS:
    allow()

# --- the subagent's OWN transcript, not the parent session's ---------------
transcript_path = payload.get("transcript_path") or ""
session_id = payload.get("session_id") or ""
agent_id = payload.get("agent_id") or ""
if not transcript_path or not session_id or not agent_id:
    allow()

tpath = os.path.join(
    os.path.dirname(transcript_path), session_id, "subagents",
    "agent-%s.jsonl" % agent_id,
)
try:
    raw_lines = open(tpath).readlines()
except Exception:
    allow()


def text_of(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(
            b.get("text", "") for b in c
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


# Keep only lines that parse and carry a `message` object. Real transcripts
# also carry queue-operation and summary lines among these; they are silently
# dropped here, same as any line that fails to parse.
records = []
for line in raw_lines:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if isinstance(d.get("message"), dict):
        records.append(d)

# --- find the first user message, and a leading slash command on it ------
first_user_text = None
for d in records:
    msg = d["message"]
    if d.get("type") == "user" and msg.get("role") == "user":
        first_user_text = text_of(msg)
        break

if first_user_text is None:
    allow()

# "Line 1" means the first line carrying anything of substance — a purely
# blank line ahead of the command is not itself content to reject on.
first_line = ""
for line in first_user_text.split("\n"):
    if line.strip():
        first_line = line.strip()
        break

m = re.match(r"^/((?:trip-itinerary:)?[a-z0-9-]+)$", first_line)
if not m:
    # No leading slash command. Deliberate: a subagent never told to run a
    # skill is out of scope for this gate.
    allow()

expected = m.group(1)
if not expected.startswith("trip-itinerary:"):
    expected = "trip-itinerary:" + expected

# --- walk every assistant tool_use block named Skill, anywhere -----------
loaded = []
for d in records:
    msg = d["message"]
    if d.get("type") != "assistant" or msg.get("role") != "assistant":
        continue
    content = msg.get("content")
    if not isinstance(content, list):
        continue
    for b in content:
        if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill":
            inp = b.get("input")
            if isinstance(inp, dict):
                skill = inp.get("skill")
                if skill:
                    loaded.append(skill)

if expected in loaded:
    allow()

# --- loop guard: count marker occurrences in tool_result blocks only -----
# A denial lands in the subagent's transcript as a tool_result block, but the
# model frequently quotes the reason back in its own next text block too —
# counting text blocks here would double-count a single denial and could trip
# the guard on the very first one. Only tool_result content counts.
marker_hits = 0
for d in records:
    msg = d["message"]
    content = msg.get("content")
    if not isinstance(content, list):
        continue
    for b in content:
        if not isinstance(b, dict) or b.get("type") != "tool_result":
            continue
        c = b.get("content")
        if isinstance(c, str):
            if MARKER in c:
                marker_hits += 1
        elif isinstance(c, list):
            joined = "".join(
                blk.get("text", "") for blk in c
                if isinstance(blk, dict) and blk.get("type") == "text"
            )
            if MARKER in joined:
                marker_hits += 1

if marker_hits >= 2:
    # Two denials have already made the point. A third would just loop the
    # subagent; leave it to trip-itinerary-skill-gate.sh at stop time instead.
    allow()

if not loaded:
    reason = (
        "%s Your spawn prompt opened with `/%s` — that names the skill you "
        "must run, it does not load it. You have not called the `Skill` "
        "tool yet. Call the `Skill` tool with `%s` now, before any other "
        "tool, then redo the work under the body it returns."
        % (MARKER, expected, expected)
    )
else:
    actual = ", ".join(sorted(set(loaded)))
    reason = (
        "%s Your spawn prompt opened with `/%s` — that names the skill you "
        "must run, it does not load it. Your transcript shows `Skill` "
        "called with `%s` instead. Call the `Skill` tool with `%s` now, "
        "before any other tool, then redo the work under the body it "
        "returns." % (MARKER, expected, actual, expected)
    )

deny(reason)
PYEOF
exit 0
