
SERVICE_NAME = giare
ENV ?= test
AWS_ROLE ?= arn:aws:iam::838080186947:role/deploy-role
APP_REGION = ap-southeast-2

COMPOSE_RUN_AWS = docker-compose -f docker-compose.build.yaml run --rm aws
COMPOSE_RUN_LINT = docker-compose -f docker-compose.build.yaml run --rm lint

AUTH_TOKEN_FILE = auth_token
ECR_REGISTRY ?= 838080186947.dkr.ecr.$(APP_REGION).amazonaws.com
ECR_REPOSITORY = giare

lint: dotenv
	$(COMPOSE_RUN_LINT) yamllint .
.PHONY: lint

validate: dotenv
	$(COMPOSE_RUN_AWS) make _validate
.PHONY: validate

build: dotenv
	$(COMPOSE_RUN_AWS) make _auth
	cat $(AUTH_TOKEN_FILE) | docker login --username AWS --password-stdin $(ECR_REGISTRY)
	docker build -t $(ECR_REGISTRY)/$(ECR_REPOSITORY):$(TAG) .
	docker push $(ECR_REGISTRY)/$(ECR_REPOSITORY):$(TAG)
.PHONY: build

deployApp: dotenv
	$(COMPOSE_RUN_AWS) make _deployApp
.PHONY: deployApp

# replaces .env with DOTENV if the variable is specified
dotenv:
ifdef DOTENV
	cp -f $(DOTENV) .env
else
	$(MAKE) .env
endif

# creates .env with .env.template if it doesn't exist already
.env:
	cp -f .env.template .env

_validate: _assumeRole
	aws --region $(APP_REGION) cloudformation validate-template --template-body file://cloudformation/template.yaml; \

_auth: _assumeRole
	aws ecr get-login-password --region $(APP_REGION) > $(AUTH_TOKEN_FILE)

_deployApp: _assumeRole
	aws --region $(APP_REGION) cloudformation deploy \
		--template-file ./cloudformation/template.yaml \
		--stack-name "$(SERVICE_NAME)-$(ENV)" \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
		--no-fail-on-empty-changeset \
		--parameter-overrides ServiceName=giare Environment=$(ENV) ImageTag=$(TAG)

_assumeRole:
ifndef AWS_SESSION_TOKEN
	$(eval ROLE = "$(shell aws sts assume-role --role-arn "$(AWS_ROLE)" --role-session-name "deploy-assume-role" --query "Credentials.[AccessKeyId, SecretAccessKey, SessionToken]" --output text)")
	$(eval export AWS_ACCESS_KEY_ID = $(shell echo $(ROLE) | cut -f1))
	$(eval export AWS_SECRET_ACCESS_KEY = $(shell echo $(ROLE) | cut -f2))
	$(eval export AWS_SESSION_TOKEN = $(shell echo $(ROLE) | cut -f3))
endif
