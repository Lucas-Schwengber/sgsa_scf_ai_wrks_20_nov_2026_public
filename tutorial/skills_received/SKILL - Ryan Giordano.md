---
name: math-checking
description: Use when helping Ryan write, review, or revise mathematical proofs, lemmas, or theorem statements, especially LaTeX for a paper. Covers self-contained definitions, citation handling, proof structure, macros, rates, how to propose edits, and how to structure mathematical arguments.
---

# Proof writing

These are Ryan's standing preferences for mathematical writing. Follow them whenever you draft, review, or revise a proof, a lemma, a theorem statement, or the surrounding LaTeX.

## Who edits the text

- Ryan makes every edit to the text and mathematics himself. Your role is to review and suggest, unless Ryan instructs you explicitly otherwise.
- Do not edit, commit, or push LaTeX unless Ryan explicitly approves that specific change. Approval for one change does not cover the next.
- By default, show the proposed LaTeX in the conversation, in a fenced code block, ready to paste. Say exactly where it goes (file, label, and the sentence it replaces or follows).
- Before changing anything Ryan has written, ask. Never silently overwrite his wording, including half-finished sentences he is still working on.
- If you are asked to make changes on a shared branch, pull first, make only the changes he asked for, and say what you changed.

## Track pending edits

- While Ryan reads and edits, keep a running list of every small change he has asked for or agreed to but has not yet made. Add to it as he mentions new ones, including ones mentioned in passing.
- Keep the list in a file he can see, remove items once they are done, and keep items he wants to finish himself in a separate section.
- When Ryan asks you to apply the list, apply exactly those items and nothing else.

## Self-contained definitions

- Define every quantity used in the paper, in the paper. Do not assume the reader knows definitions from a cited work, including Ryan's own earlier papers.
- If referring to a quantity defined elsewhere is unavoidable, point to exactly where it is defined (e.g. "Definition 7 of \citet{...}", "eq. (S12) of \citet{...}"), and still say in words what it is.
- Define notation before its first use, and define objects explicitly rather than by description (e.g. define integration regions, events, and index sets with set-builder notation, not "the region where the expansion is valid").
- Give an informal notion (e.g. a "regular event") a formal definition with a label, and cite the corresponding definition in the source if there is one.
- If a cited work is referred to by a short name (e.g. "BayesIJ"), say at the start of each lemma or section that uses it that the name refers to \citet{...}. Do not use the short name before saying this.

## Proof structure

- Open each proof by stating what it will show and how: the target bound, and the facts or steps it reduces to (e.g. "It suffices to show Facts 1-3 below"). Number the facts or steps and refer back to them by number.
- Make every "it suffices to show" reduction correct and complete. Check that the stated sufficient condition really implies the result, including rates and uniformity.
- Give enough intermediate steps that a careful reader can follow each line without filling gaps on scratch paper. Expansions (Taylor series, exponentials of expansions, changes of variables) deserve an explicit line for each step. When in doubt, add the step.
- Say explicitly which assumption, lemma, or equation justifies each nontrivial step, by \cref.
- Do not repeat what notation already says (e.g. if regions are already split in the notation, do not re-announce the split in words).
- Avoid introducing an intermediate object when the final object can be named directly.

## Rates and constants

- Be exact about orders. Distinguish O(·) from Õ(·) (hidden log factors), and check whether log factors break a downstream argument. Do not claim a rate the cited source does not prove.
- State what each constant may and may not depend on (e.g. "C* and N* not depending on t"), and keep uniformity claims explicit.
- When a bound uses a sup or inf over a region, check whether that sup or inf introduces growing factors (such as log N) and track them.

## Macros

- Use a macro for any object whose notation might change (sets, regions, estimators, operators), so it can be changed in one place.
- Use the paper's existing macros consistently. Check the macro file before introducing a new one.
- Keep macros unique: never redefine an existing macro in another file, and check that a new name does not collide with an existing one (or with a standard LaTeX command).
- Do not reuse a symbol for two different objects.

## Mathematical style

- Err on the side of not introducing too many new symbols unless long expressions hinder scannability.
- State the broad structure of the argument at the beginning of a proof.  At the beginning of a lengthy sub-argument (a page or more), describe the overall path at the beginning.
  Always be clear what goal you are working towards during any part of the proof.
- Structure proofs hierarchically.  A single lemma or theorem should ideally have a proof that can be broken into a small number of pieces and sketched 
  in a few lines.  Successively add detail in hierarchical structures.
- When appropriate, make lists of distinct results that need to be shown, and refer back to them.

## Tracking errors

- Maintain files that track errors in (at least) four categories: serious errors that require judgement to fix, serious errors with easy fixes, minor errors that are easily fixed (such as erroneous signs or constants), and mere typos.
- In the error tracking files, give each error a unique identifier (e.g. A1).  Maintain these identifiers over time.  
- Once an error has been fixed and merged into main, you can remove it from the list.  There is no need to keep track of errors that have been fixed unless they are relevant for some future task.
- When reviewing a proof, report errors with file and line, a short description, and a suggested fix in LaTeX. Separate genuine mathematical errors from typos and style issues.
- Flag gaps where a reader could not follow, not only outright mistakes.
