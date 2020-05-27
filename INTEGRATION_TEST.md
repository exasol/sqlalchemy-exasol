# Integration Test Setup

Integration testing is done by GitHub Actions contained in this repository, which provide a CI/CD pipeline to test, build, and deploy sqlalchemy_exasol to Pypi.

Two main workflows are used for this purpose:

## CI

This is meant to be used as the test workflow. It's located under:

	sqlalchemy_exasol/.github/workflows/CI.yml

This workflow will be executed anytime there's a commit pushed to any branch that is **not master**, or whenever there's a pull request created where the base branch is **not master**. It runs a Docker Container with an Exasol databse for every version specified in *matrix.exasol_version*, and uses those DBs to executes all tests in the repository. If everything went fine, it will create a package distribution using both sdist and wheel.

To run it just commit and push to any non-master branch and watch the workflow run in:

https://github.com/blue-yonder/sqlalchemy_exasol/actions

## CI-CD

This is meant to be used as the Production workflow. It's located under:

	sqlalchemy_exasol/.github/workflows/CI-CD.yml

This workflow will be executed anytime there's a commit pushed to **master**, or whenever a **tag** (release) is pushed. It does all the same steps than the CI workflow with one additional step at the end: Upload the package to Pypi. This upload step only happens when a tag is pushed, it will not be executed when commits are done in master.

To run it just commit and push to master (*Optional:* push a tag in case you want Pypi upload) and watch the workflow run in:

https://github.com/blue-yonder/sqlalchemy_exasol/actions

The status of the CI-CD workflow will always be reflected in the badge called "build" in the README.rst and Home Page of this repository
