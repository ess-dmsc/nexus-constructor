## Issues 

When creating an issue, please add it to the kanban board project. It will be placed in the selected column.

## Branches 
### Branching
* Branch your feature off 'master'
* Create pull requests against 'master'

### Branch naming

The names should start with the ticket number and contain a brief description seperated by underscores. For example:
`84_adding_pr_template`

## Pull Requests 
There is a template for pull requests. This should contain enough information for the reviewer to be able to review the code efficiently.

In the case of an in-progress pull request, don't assign any reviewers as it can clog up their github notifications and if someone starts reviewing that's outdated it can potentially cause issues. 

## Code style
All code should be pep8 compliant, we have a linter built into the CI system. 
[Black](https://black.readthedocs.io/en/stable/the_black_code_style.html) code style should be followed where possible unless readability is compromised. 

variable naming conventions should follow the standard set in PEP8.

## Documentation 
Docstrings should be in the reStructuredText format (set by default in pycharm) 

Inline comments should be used when complex logic is used

## Unit tests
Tests should be written/modified for any code added or changed (within reason, of course).
Unit tests should be named using the [GIVEN_WHEN_THEN](https://www.agilealliance.org/glossary/gwt/) pattern.

