This repo contains Simple Kubernetes PreScaler code, and kubernetes manifests.

Scaler works with Custom Resource Definitions and scales kubernetes workloads using HPA.
Default configuration gets scaling data from Turkey’s Champions League’s fixture services and scale pods during match times.

## How to use PreScaler

 1. Clone repo on kubernetes connected host.

 2. Deploy CRDs (deploy/crds.yaml)

 3. Create namespace (default prescaler)

 4. Create custom resources

 5. Deploy PreScaler (deploy/prescaler.yaml)
 
**by default service account uses cluster-admin role. You can change role scope**

## Custom Resource Definitions

**scalesets.prescaler.kloia.com:** This custom resource is defined cluster-wide for scaleset resource records.
- namespacename: deployment and hpa’s namespace
- deploymentname: deployment name in a specific namespace
- hpaname: hpa name for scaling
- defaultreplicas: default replica count for scaler calculation

**criticalteams.prescaler.kloia.com:** This custom resource is defined cluster-wide for critical teams. Scaler uses these records while scaling count calculation.
- criticalteamid: id for web service calls (for fixture services)

**percents.prescaler.kloia.com:**  This custom resource is defined namespace-wide for scaler calculation percents.
- minpercent: minimum percent for scaler calculations
- maxpercent: maximum percent for scaler calculations
- criticalminpercent: minimum percent for critical teams scaler calculations
- criticalmaxpercent: maximum percent for critical teams scaler calculations

## Environments

You can use those environments for prescaler container.
- wait: interval for service checking.
- FIXTURE_URL: fixture service URL.
- HOURS_INTERVAL_FEATURE: scaling interval hour before the match.
- HOURS_INTERVAL_PAST: scaling interval hour after the match.