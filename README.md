[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=pamelafox%2Fflask-db-quiz-example&machine=standardLinux32gb&devcontainer_path=.devcontainer%2Fdevcontainer.json&location=WestUs2)
[![Open in Remote - Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com%2Fpamelafox%2Fflask-db-quiz-example)

This repository includes a small Python Flask web site, made for demonstration purposes only.

## Opening the project

This project has [Dev Container support](https://code.visualstudio.com/docs/devcontainers/containers), so it will be be setup automatically if you open it in Github Codespaces or in local VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

If you're not using one of those options for opening the project, then you'll need to:

1. Create a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate it.

2. Install the requirements:

    ```shell
    python3 -m pip install -r requirements-dev.txt
    ```

3. Install the pre-commit hooks:

    ```shell
    pre-commit install
    ```

## Local development


1. Create an `.env` file using `.env.sample` as a guide. Set the value of `DBNAME` to the name of an existing database in your local PostgreSQL instance. Set the values of `DBHOST`, `DBUSER`, and `DBPASS` as appropriate for your local PostgreSQL instance. If you're in the Dev Container, copy the values exactly from `.env.sample`.

2. Apply migrations to database:

```console
python3 -m flask db upgrade
```

3. Load in seed data (to create first quiz):

```console
python3 -m flask seed
```

4. Run the server:

```console
python3 -m flask --debug run --port 50505
```

5. Click 'http://127.0.0.1:50505' in the terminal, which should open the website in a new tab.
6. Open the quiz linked from the index page.
7. Answer the quiz and submit, notice the high scores update below.

## Deployment

This repository is set up for deployment on Azure using the configuration files in the `infra` folder.

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/?WT.mc_id=python-79461-pamelafox)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd?WT.mc_id=python-79461-pamelafox). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Initialize a new `azd` environment:

    ```shell
    azd init
    ```

    It will prompt you to provide a name (like "flask-app") that will later be used in the name of the deployed resources.

4. Provision and deploy all the resources:

    ```shell
    azd up
    ```

    It will prompt you to login, pick a subscription, and provide a location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location (like to "centralus") can help, as there may be availability constraints for some of the resources.

5. When azd has finished deploying, you'll see an endpoint URI in the command output. Visit that URI and you should see the quiz! 🎉

6. When you've made any changes to the app code, you can just run:

    ```shell
    azd deploy
    ```
