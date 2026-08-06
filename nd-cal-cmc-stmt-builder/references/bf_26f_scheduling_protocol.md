# Firm 26(f) Scheduling Protocol and Calendar Workflows

## Overview

This document outlines the firm's protocol for computing and scheduling key deadlines in federal litigation, with emphasis on the Rule 26(f) conference baseline and class certification motion timing for Northern District of California cases.

## Rule 26(f) Conference Baseline

### Initial Disclosures Deadline

Federal Rule of Civil Procedure 26(a)(1)(C) requires parties to make initial disclosures:

**14 calendar days after the parties' Rule 26(f) conference**, calculated under Federal Rule of Civil Procedure 6(a) (which adds 3 days if the deadline falls on a weekend or federal holiday).

### Procedure: Finding the 26(f) Date

1. **Obtain matter number** from user or case caption
2. **Access matter's calendar** (integrated calendar tool or external calendar system)
3. **Search for "26F" event** or "Rule 26(f) conference" in the calendar for that matter
4. **Extract the 26(f) date** (format: YYYY-MM-DD)
5. **Compute initial-disclosures deadline** using `scripts/frcp6_date.py`:
   ```
   python3 scripts/frcp6_date.py <26f_date> "14 days"
   ```
6. **Use the adjusted_date value** from JSON output in Topic 7 of the CMS

### Fallback Behavior

If the calendar lookup fails (matter not found, no 26(f) event, or calendar tool unavailable):
- Leave Topic 7 and Topic 15 initial-disclosures row as bracketed placeholder: "[INITIAL DISCLOSURES DEADLINE: 14 days after Rule 26(f) conference]"
- Add a note in the final response: "Calendar lookup did not produce a 26(f) date; Topic 7 initial-disclosures deadline left as placeholder for user confirmation."

---

## Class Certification Motion Scheduling

### Timing Framework

For putative class actions with a confirmed Case Management Conference (CMC) hearing date:

1. **Motion filing window:** 8–10 months after CMC hearing
2. **Standard practice:** File at 9-month mark (midpoint)
3. **Opposition deadline:** 45–60 days after motion filing (subject to judge-specific notice period)
4. **Reply deadline:** 30–45 days after opposition filing
5. **Hearing notice period:** 35 calendar days per Civil L.R. 7-2(a), or judge-specific override

### Date Computation Examples

**Example Case: CMC hearing on 2026-11-15**

1. **Plaintiff's Motion for Class Certification date:**
   ```
   python3 scripts/frcp6_date.py 2026-11-15 "9 months"
   ```
   Result: `2027-08-15` (or next business day per FRCP 6(a))

2. **Opposition deadline (45 days after motion):**
   ```
   python3 scripts/frcp6_date.py 2027-08-15 "45 days"
   ```
   Result: `2027-09-29`

3. **Reply deadline (30 days after opposition):**
   ```
   python3 scripts/frcp6_date.py 2027-09-29 "30 days"
   ```
   Result: `2027-10-29`

4. **Hearing date (35 days after reply filing, per Civil L.R. 7-2(a)):**
   ```
   python3 scripts/frcp6_date.py 2027-10-29 "35 days"
   ```
   Result: `2027-12-03`

---

## Judge-Specific Notice Period Overrides

Some N.D. Cal. judges have standing orders specifying non-standard notice periods for hearings. Verify the assigned judge's standing order for:

- Motion response deadlines (may be 20, 30, or 45 days instead of standard)
- Hearing notice period (may be 10, 21, or 35 days instead of Civil L.R. 7-2(a)'s standard 35)
- Hearing date preferences (some judges prefer specific weekdays or times)

**Common deviations:**
- Judge [NAME]: Requires 21-day notice for hearings (not 35 days)
- Judge [NAME]: Requires 45-day opposition window (not 30 days)

Check `cand.uscourts.gov` or the judge's published standing order before finalizing Topic 15 dates.

---

## Calendar-Assisted Workflow for Topic 15 (Scheduling Table)

### Prerequisites

1. **Calendar tool is connected** (integration with external calendar system, Google Calendar, Outlook, etc.)
2. **Real CMC hearing date exists** (from Rule 16 Order or confirmed by user; not a bracketed placeholder)
3. **Matter has a recognized calendar entry** (calendar lookup in Step 1 succeeded)

### Workflow Steps

#### Step 1: Compute Proposed Dates

Use `scripts/frcp6_date.py` to compute:
- Plaintiff's Motion for Class Certification (9 months after CMC hearing, FRCP-6-adjusted)
- Opposition deadline (45 days after motion, adjusted for judge-specific notice period)
- Reply deadline (30 days after opposition, adjusted)
- Hearing date (35 calendar days after reply filing, or judge-specific notice period)

Example:
```bash
python3 scripts/frcp6_date.py 2026-11-15 "9 months" --weekday Thursday
# Result: Propose motion for Thursday, 2027-08-19
```

#### Step 2: Conflict Check

For each proposed date:
1. Query user's calendar for conflicts
2. Flag any conflicts with existing events (depositions, hearings, vacations, etc.)
3. If conflict exists, suggest alternative date (next available business day per judge's weekday preference)

#### Step 3: User Confirmation

Present proposed dates to user for approval:
- "Proposed Plaintiff's Motion for Class Certification: Thursday, August 19, 2027. Proceed?"
- If user rejects or flags conflict, offer alternative
- Repeat until all four dates are confirmed

#### Step 4: Calendar Event Creation (Conditional)

Once user confirms motion date, opposition date, and reply date:
1. Create calendar events for each date
2. Event titles: "[Matter Number] — Pl. Motion for Class Cert", "[Matter Number] — Opp. to Class Cert", etc.
3. Event details: Link to CMS, case caption, judge name
4. Set reminders: 7 days and 1 day before filing deadline

After dates are confirmed and events created, present hearing-date confirmation as a separate step (see below).

#### Step 5: Hearing Date Confirmation

Once motion/opposition/reply dates are finalized and calendar events created:
1. Compute hearing date using FRCP 6(a): 35 calendar days after reply filing (or judge-specific notice period)
2. Check user's calendar for conflicts on hearing date
3. Present for approval: "Proposed hearing date: [DATE]. Confirm?"
4. If approved, create hearing calendar event (independent of motion/opposition/reply events)

### Fallback: Bracketed Placeholders

If either prerequisite fails (no calendar tool or no real CMC date):
- Leave all four class-cert rows (motion date, opposition date, reply date, hearing date) as bracketed placeholders
- Example:
  ```
  Plaintiff's Motion for Class Certification | [DATE] | [WEEKDAY]
  Oppositions to Class Cert Motion         | [DATE] | [WEEKDAY]
  Replies to Class Cert Opposition         | [DATE] | [WEEKDAY]
  Hearing on Class Cert Motion             | [DATE] | [WEEKDAY]
  ```
- Note in final response: "Calendar-assisted scheduling did not run; class certification dates in Topic 15 left as placeholders. Reason: [no calendar tool / CMC date not confirmed]."

---

## Decision Table: When to Use Placeholders vs. Calendar-Assisted Dates

| Condition | Topic 7 Initial-Disclosures | Topic 15 Class-Cert Rows | Action |
|-----------|-------------------------------|--------------------------|--------|
| 26(f) date found; calendar available | Real date | Real dates (if class action) | Compute all dates, check calendar, confirm with user |
| 26(f) date found; calendar unavailable | Real date | Brackets | Compute initial-disclosures only |
| 26(f) date NOT found; calendar available | Brackets | Brackets (if class action) | Note in final response; leave both sets as placeholders |
| 26(f) date NOT found; calendar unavailable | Brackets | Brackets (if class action) | Note in final response; leave both sets as placeholders |
| Not a class action; 26(f) date found | Real date | N/A | Compute initial-disclosures only |
| Not a class action; 26(f) date NOT found | Brackets | N/A | Note in final response |

---

## Final Response Notes

In Step 5 of the main SKILL.md workflow, report:

1. **Whether Step 1 matter-number/26(f) lookup succeeded:**
   - If yes: "26(f) conference date found: [DATE] (source: [CALENDAR/USER INPUT]). Initial-disclosures deadline computed and entered in Topic 7."
   - If no: "26(f) conference date not found in calendar. Topic 7 initial-disclosures deadline left as placeholder."

2. **Whether calendar-assisted scheduling for Topic 15 ran:**
   - If yes: "Calendar-assisted class-cert scheduling completed. Proposed dates: Motion [DATE], Opposition [DATE], Reply [DATE], Hearing [DATE]. User confirmed all dates. Calendar events created."
   - If no: "Calendar-assisted scheduling did not run. Reason: [no calendar tool / no confirmed CMC date / not a class action]. Topic 15 class-cert rows left as placeholders."

3. **Which rows got real dates vs. brackets:**
   - "Topic 7 initial-disclosures: [REAL DATE]"
   - "Topic 15 class-cert motion date: [REAL DATE or BRACKETS]"
   - "Topic 15 opposition date: [REAL DATE or BRACKETS]"
   - "Topic 15 reply date: [REAL DATE or BRACKETS]"
   - "Topic 15 hearing date: [REAL DATE or BRACKETS]"

---

## Scripting Integration

The FRCP 6(a) date calculator (`scripts/frcp6_date.py`) is the authoritative tool for all date computations. Always use it for:
- Initial-disclosures deadlines (14 days after 26(f))
- Class-cert motion dates (9 months after CMC hearing, or user-specified offset)
- Opposition and reply deadlines
- Hearing dates and other notice-period calculations

The script handles:
- Month arithmetic with proper month-end clamping (e.g., Jan 31 + 1 month = Feb 28, not Mar 2 or 3)
- Weekend roll-forward per FRCP 6(a)
- Federal holiday detection (hardcoded list; does not include California state holidays)
- Optional weekday targeting (e.g., "next Thursday")

**Output format:** JSON with `adjusted_date` (primary result) and `weekday_adjusted_date` (if --weekday flag used).

---

## Examples and Scenarios

### Scenario 1: Simple Matter, No Class Action

**Input:**
- Case: Doe v. Acme Corp., 4:26-cv-12345-JD
- Judge: J. Davila (standard notice periods)
- Matter calendar lookup: 26(f) conference on 2026-09-15
- Not a class action

**Workflow:**
1. Compute initial-disclosures deadline: `python3 scripts/frcp6_date.py 2026-09-15 "14 days"` → 2026-09-29
2. Topic 7: "Initial disclosures shall be made by September 29, 2026."
3. Topic 15: Initial-disclosures row only; class-cert rows not applicable
4. Final note: "26(f) date sourced from matter calendar (2026-09-15). Initial-disclosures deadline computed and entered in Topic 7."

### Scenario 2: Class Action, Calendar Available

**Input:**
- Case: Smith v. BigTech Inc., 4:26-cv-54321-AMO
- Judge: A. Martínez-Olguín (35-day hearing notice per Civil L.R. 7-2(a))
- CMC hearing date: 2026-11-20 (from Rule 16 Order)
- Class action: Yes
- Calendar connected: Yes
- User's calendar checked: No conflicts on proposed dates

**Workflow:**
1. Compute motion date: `python3 scripts/frcp6_date.py 2026-11-20 "9 months" --weekday Thursday` → 2027-08-19
2. Compute opposition date: `python3 scripts/frcp6_date.py 2027-08-19 "45 days"` → 2027-10-03
3. Compute reply date: `python3 scripts/frcp6_date.py 2027-10-03 "30 days"` → 2027-11-02
4. Compute hearing date: `python3 scripts/frcp6_date.py 2027-11-02 "35 days"` → 2027-12-07
5. Check user's calendar: No conflicts
6. User confirms all dates
7. Create calendar events for each date
8. Topic 15 table:
   ```
   Plaintiff's Motion for Class Certification | 2027-08-19 | Thursday
   Oppositions to Class Cert Motion          | 2027-10-03 | Sunday [user flagged]
   Replies to Class Cert Opposition          | 2027-11-02 | Tuesday
   Hearing on Class Cert Motion              | 2027-12-07 | Tuesday
   ```
   (Note: Opposition date falls on Sunday; suggest Monday 2027-10-04 as alternative)
9. User confirms Monday alternative
10. Final note: "Class-cert motion dates computed and confirmed. Calendar events created for motion (August 19), opposition (October 4), reply (November 2), and hearing (December 7)."

### Scenario 3: No Calendar Tool or 26(f) Not Found

**Input:**
- Case: Brown v. City of Somewhere, 4:26-cv-99999-XYZ
- Judge: X. Judge (unknown standing order)
- Matter calendar lookup: 26(f) date not found
- Calendar tool: Not available
- Class action: Yes

**Workflow:**
1. Topic 7: "[INITIAL DISCLOSURES DEADLINE: 14 days after Rule 26(f) conference]"
2. Topic 15 class-cert rows: "[DATE]" (brackets for all four rows)
3. Final note: "26(f) conference date not found in matter calendar. Initial-disclosures deadline in Topic 7 left as placeholder. Calendar tool not available; class-cert dates in Topic 15 left as placeholders. User to fill in after confirming 26(f) date and CMC hearing date."

---

## Historical Reference

This protocol reflects common practice for N.D. Cal. class actions. It was developed to ensure consistency, reduce calculation errors, and integrate with the firm's calendar system. Deviations (judge-specific notice periods, atypical CMC schedules) should be documented in Step 5 of the main workflow.

---

**Last Updated:** August 5, 2026
