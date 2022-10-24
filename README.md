[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=pamelafox%2Fsimple-flask-server-example)

This repository includes a very simple Python Flask web site, made for demonstration purposes only.

To try it out:

1. Open this repository in Codespaces
2. Run the server:

```console
python app.py
```

2. Click 'http://127.0.0.1:8080' in the terminal, which should open the website in a new tab
3. Try the quiz on the index page, see the high scores update on the bottom.

## Deployment

This repository is set up for deployment on Azure using the configuration files in the `infra` folder.

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/?WT.mc_id=python-79461-pamelafox)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd?WT.mc_id=python-79461-pamelafox). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Provision and deploy all the resources:
```
azd up
```



