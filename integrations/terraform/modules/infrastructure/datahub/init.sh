#!/bin/sh
# you might need to run this without sudo in front.

VERSION=v0.11.0
AWS_REGION=eu-west-1
AWS_ACCOUNT_ID=130966031144

sudo docker pull linkedin/datahub-gms:$VERSION
sudo docker tag linkedin/datahub-gms:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-gms:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-gms:$VERSION

sudo docker pull linkedin/datahub-frontend-react:$VERSION
sudo docker tag linkedin/datahub-frontend-react:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-frontend-react:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-frontend-react:$VERSION

sudo docker pull linkedin/datahub-mae-consumer:$VERSION
sudo docker tag linkedin/datahub-mae-consumer:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-mae-consumer:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-mae-consumer:$VERSION

sudo docker pull linkedin/datahub-mce-consumer:$VERSION
sudo docker tag linkedin/datahub-mce-consumer:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-mce-consumer:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-mce-consumer:$VERSION

sudo docker pull linkedin/datahub-elasticsearch-setup:$VERSION
sudo docker tag linkedin/datahub-elasticsearch-setup:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-elasticsearch-setup:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-elasticsearch-setup:$VERSION

sudo docker pull linkedin/datahub-kafka-setup:$VERSION
sudo docker tag linkedin/datahub-kafka-setup:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-kafka-setup:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/linkedin/datahub-kafka-setup:$VERSION

sudo docker pull acryldata/datahub-postgres-setup:$VERSION
sudo docker tag acryldata/datahub-postgres-setup:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/acryldata/datahub-postgres-setup:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/acryldata/datahub-postgres-setup:$VERSION

sudo docker pull acryldata/datahub-upgrade:$VERSION
sudo docker tag acryldata/datahub-upgrade:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/acryldata/datahub-upgrade:$VERSION
sudo docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/acryldata/datahub-upgrade:$VERSION
