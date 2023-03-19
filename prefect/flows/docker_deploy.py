from web_to_gcs_parent import web_to_gcs 
from gcs_to_bq_parent import gcs_to_bq
from prefect.deployments import Deployment 
from prefect.infrastructure.docker import DockerContainer


docker_block = DockerContainer.load("tsnpdcl-docker-block")

docker_dep_web_to_gcs = Deployment.build_from_flow(
    flow=web_to_gcs,
    name='docker_web_to_gcs',
    infrastructure=docker_block
)
docker_flow_gcs_to_bq = Deployment.build_from_flow(
    flow=gcs_to_bq,
    name='docker_gcs_to_bq',
    infrastructure=docker_block
)

if __name__=='__main__':
    docker_dep_web_to_gcs.apply()
    docker_flow_gcs_to_bq.apply()