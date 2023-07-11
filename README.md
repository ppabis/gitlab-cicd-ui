Sample GitLab CI/CD triggering UI
------------
Companion repository to a blog post available at:
...

```bash
$ docker build -t gitlab-ci-cd-ui:latest .
$ export GITLAB_TOKEN=<your-gitlab-token>
$ export TRIGGER_TOKEN=<your-trigger-token>
$ docker run --rm -it\
   -p 8000:8000\
   -e GITLAB_TOKEN=$GITLAB_TOKEN\
   -e TRIGGER_TOKEN=$TRIGGER_TOKEN\
   gitlab-ci-cd-ui:latest
```

The server will be available at http://localhost:8000