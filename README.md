# Réseau SDN à trois commutateurs : Mininet + ONOS

Déploiement d'un réseau **SDN (Software-Defined Networking)** de laboratoire : trois commutateurs Open vSwitch et six hôtes émulés avec **Mininet**, pilotés de façon centralisée par le contrôleur **ONOS** (OpenFlow 1.3) exécuté dans un conteneur Docker, avec supervision via le dashboard web d'ONOS.

📄 **[Rapport technique complet (PDF)](rapport-sdn-onos-3-switches.pdf)**

## Objectifs

- Déployer une VM Linux et y installer Mininet, Docker et ONOS
- Construire une topologie linéaire à trois commutateurs et la connecter à ONOS
- Automatiser le démarrage de l'ensemble en une seule commande
- Exploiter le dashboard ONOS pour visualiser et vérifier le réseau
- Définir un protocole de tests de connectivité, de performance et de résilience

## Architecture

```
            ┌─────────────────────────────┐
            │  Contrôleur ONOS 3.0.0      │
            │  Docker · 172.17.0.2:6653   │
            └──────────────┬──────────────┘
                     OpenFlow 1.3
          ┌────────────────┼────────────────┐
          │                │                │
         s1 ── 100 Mbit/s ─ s2 ── 100 Mbit/s ─ s3
        /  \              /  \             /  \
      h1    h2          h3    h4         h5    h6
   (10.0.0.1 à 10.0.0.6, liens hôte-switch limités à 10 Mbit/s)
```

La topologie est volontairement **linéaire** : un triangle créerait une boucle, et sans protocole anti-boucle (STP) le forwarding réactif d'ONOS risquerait de provoquer une tempête de broadcast.

| Élément | Détail |
| --- | --- |
| Contrôleur | ONOS 3.0.0 (image `onosproject/onos`), OpenFlow sur le port 6653 |
| Commutateurs | s1, s2, s3 : Open vSwitch, OpenFlow 1.3, `fail_mode: secure` |
| Hôtes | h1 à h6, 10.0.0.1 à 10.0.0.6 (/24), deux hôtes par commutateur |
| Liens | hôte-switch 10 Mbit/s, inter-switch 100 Mbit/s (TCLink) |

## Environnement

- VMware Workstation, Ubuntu Desktop 22.04 LTS
- VM : 6 Go de RAM (4 Go minimum), 4 vCPU, 30 Go de disque, réseau NAT
- Mininet + Open vSwitch, Docker CE, ONOS 3.0.0
- Outils : curl, netcat, git, open-vm-tools

## Contenu du dépôt

| Fichier | Rôle |
| --- | --- |
| [`topology_onos.py`](topology_onos.py) | Topologie Mininet (3 switchs, 6 hôtes), contrôleur distant ONOS |
| [`start-sdn.sh`](start-sdn.sh) | Démarre ONOS, active les applications nécessaires et lance la topologie |
| [`rapport-sdn-onos-3-switches.pdf`](rapport-sdn-onos-3-switches.pdf) | Rapport complet : installation, tests, difficultés, perspectives |

## Démarrage rapide

Prérequis : Mininet, Docker et le conteneur ONOS déjà installés (installation pas à pas dans le rapport, section 4).

```bash
# Lancer le conteneur ONOS (redémarrage automatique avec la VM)
docker run -t -d --name onos --restart unless-stopped \
  -p 8181:8181 -p 8101:8101 -p 6653:6653 -p 6640:6640 \
  onosproject/onos:latest

# Placer les scripts dans ~/sdn-lab (chemin attendu par start-sdn.sh)
mkdir -p ~/sdn-lab
cp topology_onos.py start-sdn.sh ~/sdn-lab/
chmod +x ~/sdn-lab/start-sdn.sh

# Tout démarrer en une commande
~/sdn-lab/start-sdn.sh
```

Le script attend qu'ONOS soit prêt (API REST), active les applications `openflow`, `lldpprovider`, `hostprovider` et `fwd`, attend l'ouverture du port 6653, puis lance Mininet.

**Dashboard ONOS** : `http://localhost:8181/onos/ui` (identifiants par défaut `onos` / `rocks`, acceptables en laboratoire uniquement).

## Tests prévus

| Test | Commande (CLI Mininet) | Résultat attendu |
| --- | --- | --- |
| Connectivité globale | `pingall` | 0 % de perte (30/30) |
| Traversée de 3 commutateurs | `h1 ping -c 4 h6` | 0 % de perte |
| Débit | `iperf h1 h2` | environ 9 à 10 Mbit/s |
| Découverte ONOS | Dashboard, panneau Summary | 3 équipements, 4 liens, 6 hôtes |
| Coupure d'un lien | `link s2 s3 down` puis `h1 ping -c 3 h5` | 100 % de perte, lien absent du dashboard |
| Rétablissement | `link s2 s3 up` | connectivité rétablie |
| Redémarrage du contrôleur | `docker restart onos` | reconnexion après environ 2 minutes |

Le rapport détaille la liste complète (isolation partielle, panne d'un hôte, etc.). Une première version à deux commutateurs et quatre hôtes a été validée : 2 équipements, 4 hôtes et 8 flux dans le dashboard, `pingall` à 0 % de perte (12/12).

## Difficultés rencontrées

Quelques points résolus pendant le projet (détails dans le rapport, section 7) :

- **Port 6653 fermé** : l'application `org.onosproject.openflow` doit être activée explicitement.
- **`pingall` à 100 % de perte** : en mode `secure`, sans l'application `fwd` active, les commutateurs ne transmettent rien.
- **Attente d'ONOS faussée** : lire `docker logs` donne un faux signal (lignes des exécutions précédentes) ; le script teste l'API REST et le port TCP.
- **Topologie disparue après redémarrage** : normal, Mininet vit en mémoire, il suffit de relancer `start-sdn.sh`.

## Limites et perspectives

- Contrôleur unique (en production, ONOS est déployé en grappe)
- Topologie sans redondance : un lien s1-s3 supplémentaire demanderait un mécanisme anti-boucle
- Identifiants par défaut, uniquement pour le laboratoire
- Pistes : temps de convergence après rétablissement d'un lien, QoS, statistiques via l'API REST, application ONOS personnalisée

## Auteur

Admin ASUR, administrateur sécurité et réseau
[GitHub : luffymarsseaux](https://github.com/luffymarsseaux)
