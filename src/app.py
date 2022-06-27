import logging
from kubernetes import client, config
from fixture import *
from settings import *
import time

logging.basicConfig(level = logging.INFO)
config.load_kube_config()

def calculateReplicas(replicas, percent, critical=0):
    if critical:
        minpercent = percent['items'][0]['spec']['criticalminpercent']
        maxpercent = percent['items'][0]['spec']['criticalmaxpercent']
    else:
        minpercent = percent['items'][0]['spec']['minpercent']
        maxpercent = percent['items'][0]['spec']['maxpercent']
    minreplicas = round(replicas + (minpercent * replicas / 100))
    maxreplicas = round(replicas + (maxreplicas * replicas / 100))
    
    return minreplicas, maxreplicas

def preScaler():
    critical_teams = client.CustomObjectsApi().list_cluster_custom_object(
        group="prescaler.kloia.com",
        version="v1",
        plural="criticalteams"
    )

    big_teams = []
    for team in critical_teams['items']:
        big_teams.append(team['spec']['criticalteamid'])

    incoming_matches = check_incoming_matches(big_teams)

    if incoming_matches == MATCH_NOT_EXIST:
        logging.info("No match found!")
        return

    logging.info("Match exists code: " + incoming_matches)

    scalesets = client.CustomObjectsApi().list_cluster_custom_object(
        group="prescaler.kloia.com",
        version="v1",
        plural="scalesets"
    )

    for scaleset in scalesets['items']:
        ns = scaleset['spec']['namespacename']
        deploy = scaleset['spec']['deploymentname']
        hpa = scaleset['spec']['hpaname']
        replicas = scaleset['spec']['defaultreplicas']
        percent = client.CustomObjectsApi().list_namespaced_custom_object(
            group="prescaler.kloia.com",
            version="v1",
            namespace=ns,
            plural="percents",
            limit=1
        )
        if incoming_matches == MATCH_EXIST:
            minReplicas, maxReplicas = calculateReplicas(replicas, percent)
        elif incoming_matches == CRUCIAL_MATCH_EXIST:
            minReplicas, maxReplicas = calculateReplicas(replicas, percent, 1)
        
        logging.info(f"{deploy} deploy {hpa} hpa minreplicas {minreplicas}")
        logging.info(f"{deploy} deploy {hpa} hpa maxreplicas {maxreplicas}")
        
        hpaResource = client.AutoscalingV2Api().list_namespaced_horizontal_pod_autoscaler(
            namespace = ns,
            limit = 1
        )
        hpaMin = hpaResource['items'][0]['spec']['minReplicas']
        
        if hpaMin != minReplicas:
            logging.info(f"{deploy} deploy {hpa} hpa scaling")
            hpaResource['items'][0]['spec']['minReplicas'] = minReplicas
            hpaResource['items'][0]['spec']['maxReplicas'] = maxReplicas
            client.AutoscalingV2Api().patch_namespaced_horizontal_pod_autoscaler(
                name = hpa
                namespace = ns
                body = hpaResource
            )

def main():
    while true:
        preScaler()
        time.wait(WAIT_FOR)


if __name__=="__main__":
    main()