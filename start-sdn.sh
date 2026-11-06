#!/bin/bash
AUTH="onos:rocks"

echo "*** Demarrage du conteneur ONOS (si arrete)..."
docker start onos > /dev/null 2>&1

ONOS_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' onos 2>/dev/null)
if [ -z "$ONOS_IP" ]; then
  echo "ERREUR : conteneur 'onos' introuvable ou arrete. Verifiez avec : docker ps -a"
  exit 1
fi
echo "*** IP d'ONOS : $ONOS_IP"

echo "*** Attente de l'API d'ONOS (1 a 3 minutes)..."
until curl -sf -u "$AUTH" "http://$ONOS_IP:8181/onos/v1/applications" > /dev/null; do
  echo "    ONOS demarre encore..."
  sleep 5
done

echo "*** Activation des applications ONOS (openflow, decouverte, fwd)..."
for app in openflow lldpprovider hostprovider fwd; do
  curl -s -u "$AUTH" -X POST \
    "http://$ONOS_IP:8181/onos/v1/applications/org.onosproject.$app/active" > /dev/null
done

echo "*** Attente du port OpenFlow 6653..."
for i in $(seq 1 60); do
  nc -z "$ONOS_IP" 6653 && break
  sleep 3
done
if ! nc -z "$ONOS_IP" 6653; then
  echo "ERREUR : le port 6653 reste ferme apres 3 minutes."
  echo "Regardez les logs : docker logs --tail 50 onos"
  exit 1
fi

echo "*** Nettoyage Mininet..."
sudo mn -c > /dev/null 2>&1

echo "*** Lancement de la topologie..."
sudo ONOS_IP="$ONOS_IP" python3 ~/sdn-lab/topology_onos.py
