# GiHub Workflow CI/CD demonstration: movie recommender on Render

[![Render deployment](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app-CICD/actions/workflows/render_deployment.yml/badge.svg)](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app-CICD/actions/workflows/render_deployment.yml)[![Codespaces Prebuilds](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app-CICD/actions/workflows/codespaces/create_codespaces_prebuilds/badge.svg)](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app-CICD/actions/workflows/codespaces/create_codespaces_prebuilds)

Service is live on [Render](https://movie-recommender-streamlit-cicd.onrender.com).

**Note**: Render 'scales to zero', so it may take a few minutes for the service to start back up if no one has used it in a while.

## Introduction

This repository demonstrates a simple CI/CD workflow for Render deployment of a ML app using pytest and GitHub workflows. It should be easily adaptable to other simple Render deployments. The rest of this README documents the set-up steps.

## Outline

1. Workflow 
2. Parts list
2. The movie recommender app
3. pytest automation with GitHub workflows
4. Automatic deployment with GitHub workflows
6. Render deployment target set up
7. Authentication
8. How to get those cool 'passing' badges
9. How to start the app automatically in codespaces

## 1. Workflow

1. A developer on the project submits a pull request containing updates to the main fork.
2. A human being sanity checks the changes and merges or closes the pull request at their discretion (this is the last human in the loop step!).
3. Merging the pull request triggers a GitHub workflow.
4. The GitHub workflow triggers an action to test the code.
5. If the tests pass, the GitHub workflow triggers and action to deploy the code to Render.
6. Render spins up the new version of the app.

## 2. Parts list

1. **GitHub**: hosts the code and orchestrates the pipeline.
2. **GitHub Codespaces**: used to develop and train the model and build the app.
3. **Pytest**: tests code for basic functionality before deploying.
4. **GitHub workflows**: orchestrates the testing and deployment of the app.
5. **GitHub actions**: does the deployment.
6. **Render**: hosts the app.

## 3. The movie recommender app

The movie recommender app uses k-nearest neighbors and bag-of-words to recommend movies similar to user input. See the original project repository [here](https://github.com/4GeeksAcademy/gperdrizet-k-nearest-neighbors). The app was manually deployed to Render for the Streamlit web app project [here](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app).

The only major difference in the app itself is the addition of testing with [pytest](https://docs.pytest.org/en/stable/index.html). Testing is needed since deployment will be automated - we don't want to deploy broken code and bring down the app!

The example repository contains [one simple test](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app-CICD/blob/main/tests/test_model.py) to check the model's output against a known case:

```python
import pytest
import movie_recommender.movie_recommender as recommender

def test_model_output():
    '''Tests to see if the model is giving sane output.'''

    # Call then recommendation function with an input for which we know the expected output
    similar_movies=recommender.get_movie_recommendations(
        'Star Wars',
        recommender.MODEL,
        recommender.TFIDF_MATRIX,
        recommender.ENCODED_DATA_DF
    )

    # Check that we received the expected answer
    assert similar_movies[0] == 'The Empire Strikes Back'
```

The test can be run inside of a codespace from the testing tab of the activities bar or via the command line with:

```bash
python -m pytest ./tests/test_model.py
```

## 4. Pytest automation with GitHub workflows

Next, we will set-up the main fork to run the test automatically when a pull request is merged via [GitHub Workflows](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python).

Follow the instructions above to generate a workflow template for building and testing Python. You only need to follow the section *Using a Python workflow template*, the rest is more than we need. Here is what the build/test portion of [the workflow file](https://github.com/4GeeksAcademy/gperdrizet-streamlit-app-CICD/blob/main/.github/workflows/render_deployment.yml) looks like:

```yaml
name: Render deployment

on:
  push:
    branches: [ "main" ]

  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
        cache: "pip"
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt

    - name: Test with pytest
      run: python -m pytest tests/test_model.py
```

This workflow will set-up a Python 3.10 build environment, install the project dependencies and then run the test(s). Next, we will add a step to deploy to Render.

## 5. Automatic deployment with GitHub workflows

For Render deployment, we will use the GitHub action [Deploy to Render](https://github.com/marketplace/actions/deploy-to-render). **Note**: this action is a community contribution - for long term deployment or major projects you would probably want to fork and maintain your own clone. Here is the full workflow file:

```yaml
name: Render deployment

on:
  push:
    branches: [ "main" ]

  workflow_dispatch:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
        cache: "pip"
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt

    - name: Test with pytest
      run: python -m pytest tests/test_model.py

  deploy:
    runs-on: ubuntu-latest
    needs:
      - test

    permissions:
        deployments: write

    steps:
      - uses: JorgeLNJunior/render-deploy@v1.4.5
        with:
          service_id: ${{ secrets.RENDER_SERVICE_ID }}
          api_key: ${{ secrets.RENDER_API_KEY }}
          wait_deploy: true
          github_deployment: true
          deployment_environment: 'production'
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

Don't change the `RENDER_SERVICE_ID`, `RENDER_SERVICE_ID` or `GITHUB_TOKEN`. These are environment variables which will be populated from GitHub secrets at runtime.

## 6. Set-up Render target

Now, we need to set-up a Render service to deploy to. This will only need to be done once, after that, the GitHub workflow will check and deploy new pull requests for us.

Go to [render.com](https://render.com/) and click 'Get started for free'. The site will ask for an email address and password and then send you a conformation link. After clicking the link, you are asked to fill out some basic profile details and are finally taken to the Render Dashboard. From there, we can create a new service for our application:

1. Click '+ New' button at the top right and select 'Web Service' from the dropdown menu
2. Select 'Public Git Repository' and paste the link to your project repository
3. Click 'Connect'

This will take you to the new web service dashboard. Then, from the settings tab set the following values:

- **Name**: whatever you want
- **Project**: don't need to add to a project - this is generally for more complex deployment that comprise multiple services
- **Language**: Python 3
- **Branch**: main
- **Region**: Ohio (US east) - or whatever is closest to you
- **Root directory**: don't set - will default to the project root
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run movie_recommender/movie_recommender.py`
- **Instance type**: Free

Lastly, under the 'Advanced' drop-down menu at the bottom of the page, make sure to turn automatic deployment off. We will manage deployment from GitHub and don't want Render to try and re-deploy every new commit. Then click 'Deploy'. Your web app should spin up after a few minutes. Congrats, the app works!

## 7. Authentication

Last bit of set-up is to store your Render credentials on GitHub so that the GitHub workflow can deploy to Render on your behalf. To do this, we will use GitHub's [secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions). Follow the instructions to add:

1. RENDER_SERVICE_ID (found in the URL of the service page on Render)
2. RENDER_API_KEY (Go to your Render profile > account settings > API keys)

## 8. How to get those cool 'passing' badges

From the GitHub 'Actions' tab:

1. Click on a run of the workflow you want a badge for.
2. Click on the three dot menu next to 'Re-run all jobs' at the upper right.
3. Choose 'Create status badge'.
4. Copy the markdown to your README file.

## 9. How to start the app automatically in codespaces

Codespaces run an instance of the development container specified by `.devcontainer/container.json`. You can set-up lots of fun stuff from there. To start the app on Streamlit's development server using the following:

```json
"postAttachCommand": "streamlit run movie_recommender/movie_recommender.py"
```
