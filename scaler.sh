#!/bin/bash

# error handling
set -e

# debug
if [ "${DEBUG}" = 1 ]; then
    set -x
fi

while true
do

# get critical teams
criticalteams=(`kubectl get criticalteams -A -o=custom-columns=id:.spec.criticalteamid --no-headers`)
data_string="${criticalteams[*]}"
BIG_TEAMS="${data_string//${IFS:0:1}/,}"

# get match state
echo " `date` [INFO] checking current matches"
matchstate=`python3 fixture/app.py`

# if match exist
if [ $matchstate -ne 0 ]; then

echo " `date` [INFO] match exist code $matchstate"

# get critical teams
criticalteams=(`kubectl get criticalteams -A -o=custom-columns=id:.spec.criticalteamid --no-headers`)

# get scalesets
scalesets=(`kubectl get scaleset.prescaler.kloia.com -o name --no-headers`)
echo " `date` [INFO] preparing for $scalesets scalesets"

# do scale tasks for scalesets
for i in "${scalesets[@]}"
do
   ns=`kubectl get $i -o jsonpath='{.spec.namespacename}'`
   deploy=`kubectl get $i -o jsonpath='{.spec.deploymentname}'`
   hpa=`kubectl get $i -o jsonpath='{.spec.hpaname}'`
   replicas=`kubectl get $i -o jsonpath='{.spec.defaultreplicas}'`
#   echo "replicas $replicas"
   if [ $matchstate -eq 1 ]; then
     minpercent=`kubectl get percent.prescaler.kloia.com $ns -o=custom-columns=minpercent:.spec.minpercent --no-headers -n $ns | head -n 1`
     maxpercent=`kubectl get percent.prescaler.kloia.com $ns -o=custom-columns=maxpercent:.spec.maxpercent --no-headers -n $ns | head -n 1`
     tmp0=`echo "scale=1; ($replicas+($minpercent*$replicas/100))" | bc`
     minreplicas=`echo "($tmp0+0.5)/1" | bc`
     tmp1=`echo "scale=1; ($replicas+($maxpercent*$replicas/100))" | bc`
     maxreplicas=`echo "($tmp1+0.5)/1" | bc`
     echo " `date` [INFO] $deploy deploy $hpa hpa minpercents $minpercent"
     echo " `date` [INFO] $deploy deploy $hpa hpa minreplicas $minreplicas"
     echo " `date` [INFO] $deploy deploy $hpa hpa maxpercents $maxpercent"
     echo " `date` [INFO] $deploy deploy $hpa hpa maxreplicas $maxreplicas"
   elif [ $matchstate -eq 2 ]; then
     minpercent=`kubectl get percent.prescaler.kloia.com $ns -o=custom-columns=minpercent:.spec.criticalminpercent --no-headers -n $ns | head -n 1`
     maxpercent=`kubectl get percent.prescaler.kloia.com $ns -o=custom-columns=maxpercent:.spec.criticalmaxpercent --no-headers -n $ns | head -n 1`
     tmp0=`echo "scale=1; ($replicas+($minpercent*$replicas/100))" | bc`
     minreplicas=`echo "($tmp0+0.5)/1" | bc`
     tmp1=`echo "scale=1; ($replicas+($maxpercent*$replicas/100))" | bc`
     maxreplicas=`echo "($tmp1+0.5)/1" | bc`
     echo " `date` [INFO] $deploy deploy $hpa hpa minpercents $minpercent"
     echo " `date` [INFO] $deploy deploy $hpa hpa minreplicas $minreplicas"
     echo " `date` [INFO] $deploy deploy $hpa hpa maxpercents $maxpercent"
     echo " `date` [INFO] $deploy deploy $hpa hpa maxreplicas $maxreplicas"
   fi
   hpamin=`kubectl get hpa $hpa -n $ns -o=custom-columns=minreplicas:.spec.minReplicas --no-headers | head -n 1`
   hpamax=`kubectl get hpa $hpa -n $ns -o=custom-columns=maxreplicas:.spec.maxReplicas --no-headers | head -n 1`
   if [ $hpamin -ne $minreplicas ]; then
   echo " `date` [INFO] $deploy deploy $hpa hpa scaling"
   echo " `date` [INFO] kubectl -n $ns patch hpa $hpa --patch '{"spec":{"minReplicas":$minreplicas,"maxReplicas":$maxreplicas}}'"
   kubectl -n $ns patch hpa $hpa --patch '{"spec":{"minReplicas":'$minreplicas',"maxReplicas":'$maxreplicas'}}'

   fi
done

fi

echo " `date` [INFO] waiting $wait"
sleep $wait

done