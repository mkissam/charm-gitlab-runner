# gitlab-runner-operator

## Description

The machine charm deploys a gitlab runner (14.3 stable branch). 

## Usage

Install the charm:

```
$ juju deploy ./gitlab-runner-operator.charm --series focal --to lxd:0 gitlab-runner
```

Relate with a gitlab sevrer:

```
$ juju add-relation gitlab-server:gitlab-server gitlab-runner:gitlab-server
```


## Developing

Create and activate a virtualenv with the development requirements:

```
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements-dev.txt
```

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

```
$ ./run_tests
```
