---
name: review-quiz
description: Reviews a Stat 133 quiz (pl-ucb-stat133 assessments/qN) against guidelines/quiz.md, each question against Q1-Q8 and the whole quiz against Z1-Z15, and publishes a report page with a scorecard by property, charts of how well the quiz covers the key ideas of the lectures it spans, and findings with short ids (Z4a, Q1b) that the instructor names to have them fixed ("fix Z4a and Q1b", "fix Z9"). Use when asked to review, check, audit, or vet a quiz or its coverage of the lectures, and when asked to fix findings from such a review.
---

# Reviewing a Stat 133 quiz

**What makes a quiz good lives in the workspace's `guidelines/quiz.md`
(Q1–Q8 for each question, Z1–Z15 for the quiz). Read it in full before
reviewing; this skill covers only the mechanics.** Every judgment in the
report cites a property.

Run everything from the workspace root. `{N}` is the quiz number (the
`assessments/qN/` directory); `{SCRATCH}` is
`<scratchpad>/review-quiz-q{N}/`.

The review only reports. It changes nothing in `pl-ucb-stat133/` until the
instructor asks for fixes by id ("Acting on fixes", below).

## Finding ids

Each finding's id is the property it falls short of plus a letter: `Z4a`,
`Z4b`, `Q1a`. Letters run in order within a property, across the whole
quiz (so `Q3a` and `Q3b` may be about different questions). An id names one
root cause: two questions with the same flaw share a finding that lists both,
and one question with two unrelated flaws under one property gets two.

This is what lets the instructor answer in a few words: "fix Z7a and Q3b",
"fix Z9" (every open Z9 finding), "fix the must-fixes". Keep ids stable once
the report is published: a fix marks a finding fixed, it doesn't renumber the
rest, and a finding added on a later pass takes the next free letter.

Severity:

- **must**: students lose or gain points they shouldn't, or the quiz
  misbehaves: a wrong answer key, a leak between questions (Z2), real-time
  grading on (Z7), a duplicate quiz number (Z8), a question on untaught
  material (Q1), a grader that rejects correct answers (Q4), a blank part
  that voids the rest of its question (Q4).
- **should**: the quiz falls short of a property in a way students will feel
  but that won't by itself mis-score them: a span lecture with no question,
  points far from weight, unclear answer format, a question that brings a
  new context it doesn't need.
- **consider**: an improvement to a property the quiz already roughly meets,
  or a choice the instructor may have made on purpose. Say which.

## Steps

### 1. Gather the facts

```bash
mkdir -p {SCRATCH}
Rscript .claude/skills/review-quiz/scripts/quiz-facts.R {N} {SCRATCH}/facts.json
```

`facts.json` holds the quiz config zone by zone, the quiz window and the
problem set's due date, the span's lectures (each one's "Key Ideas for
Today", section headings, and number of problem-set problems), every
question (points, a read/write guess, its lecture, number of parts, which
other assessments use it), the other questions in the bank for the span's
lectures, and the mechanical parts of Z4 and Z7–Z11, with line
numbers in `infoAssessment.json`.

**The span.** Quiz N covers problem set N: the lectures `psN.qmd` includes,
plus any lecture the schedule places between them that has no fragment.
Check that this makes sense against `dates` (PS N is due before the quiz).
If the instructor names a different span, or the quiz's questions plainly
target another set of lectures, re-run with `--span FIRST:LAST` (lecture
directories) and say which span you used and why in `quiz.spanNote`. A
lecture with nothing to assess (a welcome, an election-day discussion) stays
in the span with `assessable: false`, so the charts don't count it.

### 2. Read what was taught

For each lecture in the span, read its `slides.qmd` and `_ps.qmd` (with
solutions) in full: Q1 needs to know what functions, syntax, and data sets
students saw, not only the topic.

Then list each lecture's **key ideas**, the rows of the coverage chart. Start
from the closing "Key Ideas for Today" slide (`facts.json` has it) and give
each an id `NN.k`, the lecture number and its position (`18.1`, `18.2`, …).
Where a deck has no such list, or one item lumps several separately
assessable ideas (one item naming six `dplyr` verbs), write three to six
ideas from its section headings and mark them `source: "headings"`. Keep the
deck's wording where it has one. Mark each idea `ps: true` if the problem set
practices it, `false` if not.

### 3. Read every question

For each question in the quiz, read `info.json`, `question.html`, and, where
present, `server.py`, the starter files, `tests/test.R`, and
`grader_cases.R`. Record:

- **kind**: `read`, `write`, or `workspace` (the `r-studio` question).
  `kind_guess` is a starting point; the id's verb and the task decide (Z3).
- **lecture** and **ideas**: which key ideas it assesses, each `core`
  (getting it right takes understanding this idea) or `touches` (uses it in
  passing). A question that assesses nothing on the list is a Z1 or Q1
  finding, not a reason to add an idea.
- **context**: the data set or scenario, and `contextSource`: `slides`,
  `ps`, or `new` (Z5). Grep the span's decks and fragments for the data
  set's name before calling it new.
- **Q1–Q8**, each `meets`, `partly`, `short`, `not-checked`, or `n/a`, with
  the evidence: for Q1, where in the slides or PS each function and idea the
  answer needs appears (`file:line`); for Q2, the PS problem it resembles;
  for Q3, the sentence that would trip a student; for Q5, the title and its
  length.
- **Q4 for read questions**: check the answer key. Where the question shows
  code, run it in R and compare with the keyed answers; a wrong key is a
  must-fix. **Q4 for write questions**: run the question's own cases,
  `Rscript .claude/skills/write-pl-r-question/scripts/test-grader.R
  pl-ucb-stat133/questions/<id>`. Mark Q4 `meets` only if they pass and
  cover a correct alternative to the solution; a full check is
  `review-pl-grader`, which this review doesn't run. Say so under
  `notChecked`.
- **Q4, blank parts, for every question**: `facts.checks.Q4` lists each
  answer element, in a question with more than one, that lacks
  `allow-blank="true"`, and each `"each-answer"` checkbox. Each is a
  must-fix: PrairieLearn marks the whole submission invalid when any part
  is blank, so one skipped part costs the parts a student answered. Give
  all the question's listed elements one finding (Q4 lettered as usual),
  whose fix adds `allow-blank="true"` to each and switches the checkboxes to
  `partial-credit="net-correct"`. Mark Q4 `short` on those questions. When
  the quiz is synced, confirm it in PrairieLearn: submit the question with
  one part blank and check the others are graded.

### 4. Check the quiz as a whole

Work through Z1–Z15 with the guideline's **Check** for each. `facts.checks`
settles most of Z4 and all of Z7–Z11's mechanics; the judgment is yours for:

- **Z1**: lectures and key ideas with no `core` question, and questions with
  no source. Questions in `facts.unused` that would fill a gap are the
  first fix to propose; name them.
- **Z2**: read all `question.html` files one after another, side by side.
- **Z3, Z4**: the build script draws them from `kind` and `points`; a
  finding still needs your judgment of which questions to add, cut, or
  re-weight. `kind_guess` calls any question with a file editor `write`;
  when a question mixes read and write parts (Z11), tally its parts by hand.
- **Z5, Z6**: list the contexts and the answer-format instructions in quiz
  order.
- **Z11**: `facts.checks.Z11` lists lectures with more than one question.
  The fix is to merge them into one multi-part question on a shared context;
  say which parts to keep, which to cut, and which data set they share.
- **Z12**: count each question's parts by kind from its `question.html`
  and give each question its `minutes` at the guideline's rates, the
  `r-studio` question carrying the workspace setup. Quiz-wide time that
  belongs to no question (checking answers) goes in `time.extra`. The build
  script totals them and draws the estimate at the top of the page; a
  quiz over the target needs a finding that names the parts to cut.
- **Z13**: find the project studios in `_schedule.yml` (its notes) and
  which projects' studios end before the quiz opens. Treat a project
  question like a lecture in the span: its own `lecture` entry, named
  `Project: <name>`, whose key ideas are the project's findings on its
  shared data.

### 5. Write the findings

One finding per root cause (see "Finding ids"). Each has:

- **title**: the problem, in one line.
- **detail**: what's wrong and why it matters to students, with evidence.
- **fix**: the exact change, concrete enough to apply when the instructor
  says "fix it" without asking anything: the file, the key or text to
  change, the question to add with its points. Where the fix is a real
  choice (which of two questions to cut), give your recommendation and the
  alternative in the fix, and expect to confirm it when asked to fix.
- **where**: `{file, line, label}` entries, paths from the workspace root.
- **questions**: the ids of the questions involved.

Don't pad: a property the quiz meets gets a one-line summary in the
scorecard and no finding. Strengths go in the summaries.

### 6. Build and publish the report

Write `{SCRATCH}/review.json` (below), then:

```bash
Rscript .claude/skills/review-quiz/scripts/build-report.R {SCRATCH}/review.json {SCRATCH}/quiz-{N}-review.html
```

The script checks the JSON against `guidelines/quiz.md` (every property has
a status; every finding id fits its property; every idea and question a
finding or question names exists) and stops with a list of problems
otherwise. Fix them and rebuild.

Publish `{SCRATCH}/quiz-{N}-review.html` with the Artifact tool:
`icon: "checklist"` and a one-sentence `description` on the first publish.
Republish to the same file path for the rest of the review so the link
stays the same. Don't restyle the page for one quiz: change
`templates/report.html` if the layout needs to change, so every later
report gets it.

The page, top to bottom: the verdict beside the time estimate (Z12: the
total against the target and the limit, broken down by question); the
scorecard (one row per property, status and finding ids); coverage figures
(key ideas by question, points against each lecture's weight, read against
write points, and the contexts); the findings, most severe first; the
questions with their Q1–Q8 statuses; and the bank questions and anything
not checked.

### 7. Report in chat

Give the link, the time estimate against the target ("about 55 minutes;
the target is 40"), the verdict in a sentence or two, and the findings as a
compact list grouped by severity, each as `**Z7a** title`, so the
instructor can answer without opening the page. End by saying how to ask
for fixes ("fix Z7a and Q3b", or a property id for all of its findings).

## review.json

`templates/review.example.json` is a complete review (Quiz 4, Fall 2026).
Copy its shape. Text fields mark code with backticks, emphasis with
`*stars*`, and bold with `**double stars**`.

- `quiz`: `n`, `title`, `course` ("Stat 133 · Fa26"), `window` ("Oct 19–20"),
  `span` ("Lectures 17–22 · PS 4"), `spanNote` (one or two sentences: the
  span and how it was found, and any lecture marked not assessable),
  `reviewed` (date).
- `verdict`: two or three sentences, the headline for the instructor.
- `time`: `limit` (the quiz's time limit in minutes, 50 for a CBTF quiz)
  and `extra` (`{label, minutes}` for time that belongs to no question,
  such as "Checking answers"). The script adds `total` and `target`
  (four-fifths of the limit, per Z12).
- `lectures`: in span order, each `dir`, `title`, `psProblems`,
  `assessable` (omit unless `false`), and `ideas`: `{id, text, ps, source}`
  (`source` only when `"headings"`).
- `questions`: in quiz order, each `id`, `title`, `points` (auto plus
  manual), `kind`, `parts`, `minutes` (Z12), `lecture` (a span `dir`; set `outOfSpan: true`
  if it isn't one), `ideas` (`{"18.1": "core", "18.4": "touches"}`),
  `context`, `contextSource`, `q` (`{"Q1": "meets", …}`), and `findings`
  (ids).
- `properties`: one entry per property in `guidelines/quiz.md`, each `id`,
  `status`, and `summary` (one sentence; for Q properties, across all the
  questions). Names come from the guideline.
- `findings`: `id`, `property`, `severity`, `title`, `detail`, `fix`,
  `where`, `questions`, and once acted on, `status` (`fixed` or `declined`)
  and `statusNote`.
- `unused`: bank questions from `facts.unused` worth knowing about: `id`,
  `kind`, `usedBy`, `note` (e.g. "would fill the Z3a write gap").
- `notChecked`: what the review didn't cover and how to check it.

## Acting on fixes

When the instructor names findings ("fix Z7a and Q3b", "fix Z9", "do the
must-fixes"):

1. **Resolve the ids**, ignoring case. A property id means each of its open
   findings. Repeat back the list you'll fix if it's more than the ids they
   typed, and ask about any finding whose fix is a choice the instructor
   hasn't made.
2. **Apply each finding's fix** in `pl-ucb-stat133/`. A new auto-graded R
   question goes through `write-pl-r-question`; a changed grader gets its
   `grader_cases.R` re-run. Follow `CLAUDE.md` for naming and registering
   questions.
3. **Re-check**: re-run `quiz-facts.R`, re-read what changed, and confirm
   each fix meets its property without breaking another (a new shared data
   set against Z2, a new question against Z4's points).
4. **Republish**: set each finding's `status` and a one-line `statusNote`
   (what changed), update the property and question statuses the fixes
   changed, rebuild to the same path and publish. Fixed findings stay on
   the page, struck through, so the ids the instructor saw still resolve.
5. Summarize in chat what changed and what's still open. Commit in
   `pl-ucb-stat133` only when the instructor asks.
