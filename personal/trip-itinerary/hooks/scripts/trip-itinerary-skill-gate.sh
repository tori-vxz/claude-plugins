#!/usr/bin/env bash
# SubagentStop hook — closes one specific defect in trip's subagent
# dispatch: a spawn prompt whose line 1 names a skill (e.g. `/trip-itinerary:<skill>`)
# tells the subagent which skill it must run, but naming it is not loading
# it. The defect first surfaced in the sibling `bps` plugin: on 2026-07-28 a
# headless run showed a `doc-reader` spawn read its opening `/bps:doc-map` as
# ordinary prose, never called the `Skill` tool, and produced output from the
# prompt fields alone. It happened to come out the right shape. Nothing
# checked it, and a wrong shape would have passed identically. Every gated
# subagent in trip is exposed to the same failure: it could just as
# easily read its opening slash command as prose and run some other tool
# straight from the prompt fields, never calling `Skill` at all. This hook is
# that check.
#
# WHAT IT BLOCKS: a gated subagent (`trip-itinerary:trip-scout`) whose spawn prompt
# opened with a recognizable slash command, but whose transcript shows either
# no `Skill` tool call at all, or a `Skill` call for some other skill.
# In both cases the block reason names the skill the prompt asked for, says
# what (if anything) was loaded instead, and tells the subagent to call
# `Skill` with the right name and redo the work under the body it returns.
#
# WHAT IT DELIBERATELY DOES NOT CHECK:
#   * A spawn prompt with no leading slash command at all. That is out of
#     scope by design — a subagent that was never told to run a skill has
#     nothing to be gated against. The lead skill that spawns these
#     subagents is what guarantees every spawn it makes carries one; this
#     hook does not re-litigate that.
#   * Whether the skill, once loaded, was followed correctly. Only that it
#     was loaded. Judging the output is somebody else's job.
#   * Any agent outside {`trip-itinerary:trip-scout`}. `core:runner`, `main`, and
#     everything else pass through untouched even on a failing transcript —
#     this gate exists for trip's own gated agent types.
#
# SAFETY:
#   * One-bounce: `stop_hook_active` true means we already sent this subagent
#     back once this turn. A second failure is structural, not a one-off
#     miss, and forcing a third attempt would just loop — so it surfaces
#     instead.
#   * Fails open, not closed: an unreadable payload, an unreadable transcript,
#     an unrecognized agent type, or the absence of a slash command all
#     allow the stop silently. A gate that fails closed on a missing file
#     wedges the whole pipeline for a subagent that did nothing wrong.
#
# The payload arrives via $PAYLOAD rather than stdin so the heredoc below can
# stay single-quoted and the Python body can contain apostrophes freely.
#
# Contract (SubagentStop): print {"decision":"block","reason":"..."} on
# stdout with exit 0 to send the subagent back with `reason` as its next
# instruction; exit 0 printing nothing lets it stop.

payload=$(cat)

PAYLOAD="$payload" python3 <<'PYEOF'
import sys, json, re, os

GATED_AGENTS = {"trip-itinerary:trip-scout"}


def allow():
    sys.exit(0)


try:
    payload = json.loads(os.environ.get("PAYLOAD") or "")
except Exception:
    allow()

if not isinstance(payload, dict):
    allow()

# --- one-bounce guard ---------------------------------------------------
if payload.get("stop_hook_active"):
    allow()

# --- agent scope ---------------------------------------------------------
# The matcher in hooks.json is the fast path; this is what actually
# decides, and it stays even if the matcher is ever loosened or dropped.
agent_type = payload.get("agent_type") or ""
if agent_type not in GATED_AGENTS:
    allow()

# --- the subagent's OWN transcript, not the main session's ---------------
tpath = payload.get("agent_transcript_path") or ""
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

if not loaded:
    reason = (
        "Your spawn prompt opened with `/%s` — that names the skill you must "
        "run, it does not load it. Your transcript has no `Skill` tool call at "
        "all. Call the `Skill` tool with `%s` now, then redo the work under "
        "the body it returns." % (expected, expected)
    )
else:
    actual = ", ".join(sorted(set(loaded)))
    reason = (
        "Your spawn prompt opened with `/%s` — that names the skill you must "
        "run, it does not load it. Your transcript shows `Skill` called with "
        "`%s` instead. Call the `Skill` tool with `%s` now, then redo the "
        "work under the body it returns." % (expected, actual, expected)
    )

print(json.dumps({"decision": "block", "reason": reason}))
sys.exit(0)
PYEOF
exit 0
