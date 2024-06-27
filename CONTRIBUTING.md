# Welcome to Data Product Portal contributing guide <!-- omit in toc -->

Thank you for investing your time in contributing to our project!

Read our [Code of Conduct](./CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

In this guide you will get an overview of the contribution workflow from opening an issue, creating a PR, reviewing, and merging the PR.

## Getting started

To get an overview of the project, read the [README](README.md) file.
Check below to see what types of contributions we accept before making changes.

### Types of contribution

#### Issues
Issues are used to track tasks that contributors can help with. If an issue has a triage label, we haven't reviewed it yet, and you shouldn't begin work on it.

#### Translations
Our application is internationalized and can be served in multiple languages. The source content in this repository is written in English.
If you want a new language to be added follow the instruction [over here](frontend/README.md#adding-new-languages).

#### Pull requests
Pull Requests are a way to suggest changes in our repository. These pull requests can contain code changes that [resolve issues](CONTRIBUTING.md#issues), [add translations](CONTRIBUTING.md#translations) or improve/change functionality of the application in general.

### Issues

#### Create a new issue

If you've found a bug in the application or want to request a new feature, search open issues to see if someone else has reported the same thing. If it's something new, [report the bug](https://github.com/conveyordata/data-product-portal/issues/new?labels=bug&template=bug-report---.md) or [request the feature](https://github.com/conveyordata/data-product-portal/issues/new?labels=enhancement&template=feature-request---.md).

#### Solve an issue

Scan through our [existing issues](https://github.com/conveyordata/data-product-portal/issues) to find one that interests you. If you find an issue to work on, you are welcome to assign it to open a PR with a fix.

### Make Changes

#### Create a fork
Fork the repository to your own GitHub repository.

#### Setup local development
Make sure to correctly set up your local environment for development. For more information, see [the development guide](README.md#local-development).

#### Use branches
First create a branch from 'main'. You can now start with your changes on this newly created branch.
Please make a separate branch for each set of unrelated changes.

#### Commit your update
Once you are happy with your changes, you can commit them.
Give each commit a descriptive message to help you and future contributors understand what changes the commit contains.
Ideally, each commit contains an isolated, complete change.

### Pull Request

When you're finished with the changes, create a pull request to the original Data Product Portal repository.
- Don't forget to link the PR to an issue if you are solving one.
- Your PR submission will trigger a suite of tests to run, only when all tests succeed the PR is considered for merging into the main project.
- One of the project committers will assess the open PR and will provide feedback. Feedback can consist of suggestions, request for changes, additional documentation, tests that need to be addressed before the change can be incorporated. Project committers can also immediately amend the PR to help out the contributor. Project committers have to make sure that commits obey the project development guidelines.
- The requested changes should be made in the forked repository.
- As you update your PR and apply changes, mark each conversation as 'resolved'.
- If you run into any merge issues, checkout this [git tutorial](https://github.com/skills/resolve-merge-conflicts) to help you resolve merge conflicts and other issues.
- Once all tests succeed and a project committer approves the PR, it will be merged into the main branch of the project.

### Your PR is merged!

Congratulations! The Data Product Portal team thanks you!
The new functionality or bugfix will be taken along in the next release.
