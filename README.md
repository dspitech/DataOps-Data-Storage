# TP 1 - Azure Blob Storage - Azurite version Cloud

### Nom : Lo
### Prénom : Pape
### Cours : DataOps
### Année : 2025 - 2026
### Prof : Arij AZZABI 



---
## Objectifs
À la fin de ce TP, vous serez capables de :
- créer un Storage Account et un container `raw` sur Azure
- envoyer un fichier JSON depuis le Cloud Shell avec Python
- organiser les fichiers selon une structure Data Lake (partitions par date)
- historiser les fichiers sans écraser les anciens

---

### Étape 1 – Ouvrir le Cloud Shell en PowerShell
- Aller sur portal.azure.com
- Cliquer sur l'icône Cloud Shell >_ en haut à droite
- Choisir PowerShell
- Si c'est la première utilisation, un storage account sera créé automatiquement pour persister vos fichiers

---
### Étape 2 - Créer un Resource Group et un Storage Account
```powershell
# Variables – adaptez à votre contexte
$RESOURCE_GROUP = "rg-datalake-tp1"
$STORAGE_ACCOUNT = "stdatalaketp1" + (Get-Random -Maximum 9999)   # nom unique obligatoire
$LOCATION = "norwayeast"

# Créer le Resource Group
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION

# Créer le Storage Account
az storage account create `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2

# Récupérer la connection string
$env:AZURE_STORAGE_CONNECTION_STRING = az storage account show-connection-string `
  --name $STORAGE_ACCOUNT `
  --resource-group $RESOURCE_GROUP `
  --query connectionString `
  --output tsv

# Vérifier
echo $env:AZURE_STORAGE_CONNECTION_STRING
```

![image](https://hackmd.io/_uploads/S1fi0lokGx.png)
![image](https://hackmd.io/_uploads/Byo6Rxikzx.png)
![image](https://hackmd.io/_uploads/SJ21JWi1zg.png)
![image](https://hackmd.io/_uploads/S1Y-y-skMg.png)

---
### Étape 3 - Créer la structure du projet
```powershell
mkdir TP-AZURE-BLOB
cd TP-AZURE-BLOB
mkdir data
mkdir scripts
```

![image](https://hackmd.io/_uploads/rk-_kZsJMx.png)

---


### Étape 4 – Installer la librairie Python Azure Blob
```powershell
python -m pip install azure-storage-blob --user
```
> Sur le Cloud Shell, la librairie est souvent déjà disponible. Cette commande s'assure qu'elle est à jour.

![image](https://hackmd.io/_uploads/H1FXgZikGx.png)

---

### Étape 5 - Créer le fichier JSON
```powershell
'{"message": "hello azure", "source": "tp1"}' | Out-File -Encoding utf8 data/test.json

# Vérifier
Get-Content data/test.json
```
Résultat attendu :
```json
{"message": "hello azure", "source": "tp1"}
```

![image](https://hackmd.io/_uploads/Bk3BgboJMg.png)

---

### Étape 6 - Créer le script Python
```powershell
@'
import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = "raw"
LOCAL_FILE_PATH = Path("data/test.json")
BLOB_NAME = "test/test.json"


def get_connection_string():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise EnvironmentError(
            "Variable AZURE_STORAGE_CONNECTION_STRING manquante."
        )
    return connection_string


def upload_file():
    connection_string = get_connection_string()

    if not LOCAL_FILE_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {LOCAL_FILE_PATH}")

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
        print(f"Container créé : {CONTAINER_NAME}")
    except Exception:
        print(f"Container déjà existant : {CONTAINER_NAME}")

    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=BLOB_NAME
    )

    with open(LOCAL_FILE_PATH, "rb") as file:
        blob_client.upload_blob(file, overwrite=True)

    print(f"Upload réussi : {BLOB_NAME}")


if __name__ == "__main__":
    upload_file()
'@ | Out-File -Encoding utf8 scripts/upload_blob.py
```

![image](https://hackmd.io/_uploads/H1hOgZo1Gx.png)
![image](https://hackmd.io/_uploads/Skatl-iyMe.png)
![image](https://hackmd.io/_uploads/ryXjlboJzx.png)

---

## Étape 7 - Exécuter le script
```powershell
python scripts/upload_blob.py
```
Résultat attendu :
```
Container créé : raw
Upload réussi : test/test.json
```
ou, si le container existe déjà :
```
Container déjà existant : raw
Upload réussi : test/test.json
```

![image](https://hackmd.io/_uploads/B1lkZZoJzg.png)
![image](https://hackmd.io/_uploads/S15e-ZjkMl.png)

---

## Étape 8 - Vérifier le blob dans Azure
```powershell
az storage blob list `
  --container-name raw `
  --connection-string $env:AZURE_STORAGE_CONNECTION_STRING `
  --output table
```
![image](https://hackmd.io/_uploads/H1eSfWWiyGl.png)
![image](https://hackmd.io/_uploads/rJhB-ZoJMg.png)

---

## Étape 9 - Structurer le Data Lake (partitions par date)
Modifier la variable `BLOB_NAME` dans le script :
```powershell
(Get-Content scripts/upload_blob.py) `
  -replace 'BLOB_NAME = "test/test.json"', 'BLOB_NAME = "bitcoin/year=2026/month=05/day=10/test.json"' `
  | Set-Content scripts/upload_blob.py

python scripts/upload_blob.py
```

![image](https://hackmd.io/_uploads/BJqAZbs1Gx.png)
![image](https://hackmd.io/_uploads/HJWNGbjyGx.png)

> **À retenir :** Dans un Data Lake, les données sont organisées avec des partitions logiques par date (`year=`, `month=`, `day=`). Cela permet des lectures efficaces en ne scannant que les partitions nécessaires.

![image](https://hackmd.io/_uploads/BJOUzbj1Gl.png)
![image](https://hackmd.io/_uploads/HJEFGboJfe.png)

---

## Étape 10 - Historiser les fichiers
Dans un Data Lake, on ajoute de nouveaux fichiers plutôt que d'écraser les anciens.
```powershell
# Nouveau contenu JSON
'{"message": "second upload", "source": "tp1"}' | Out-File -Encoding utf8 data/test.json

# Nouveau nom de blob (test_2 au lieu de test)
(Get-Content scripts/upload_blob.py) `
  -replace 'bitcoin/year=2026/month=05/day=10/test.json', 'bitcoin/year=2026/month=05/day=10/test_2.json' `
  | Set-Content scripts/upload_blob.py

python scripts/upload_blob.py
```
![image](https://hackmd.io/_uploads/H1q9z-jyze.png)

Vérifier les deux fichiers :
```powershell
az storage blob list `
  --container-name raw `
  --connection-string $env:AZURE_STORAGE_CONNECTION_STRING `
  --prefix "bitcoin/" `
  --output table
```
![image](https://hackmd.io/_uploads/B1qpz-o1fe.png)
![image](https://hackmd.io/_uploads/ryUJm-jkMx.png)


---

## Nettoyage 
Pour éviter des coûts inutiles, supprimez les ressources après le TP :
```powershell
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

![image](https://hackmd.io/_uploads/BkUX7ZsJMl.png)

Supprimer tous les fichiers et répertoires du projet.

```PowerShell
cd ..
Remove-Item -Recurse -Force TP-AZURE-BLOB
```
![image](https://hackmd.io/_uploads/SJ6ur-ikfg.png)

---
## Questions de compréhension

- 1. **Différence entre Azurite et Azure Blob Storage réel ?**
Azurite est un émulateur local qui tourne sur votre machine, gratuit et sans connexion internet. 
Azure Blob Storage réel est un service cloud Microsoft payant, accessible partout, avec haute disponibilité, redondance et sécurité d'entreprise. 
Azurite sert uniquement au développement et aux tests.

- 2. **Pourquoi un container nommé raw ?**
Dans l'architecture Data Lake, raw désigne la zone de données brutes, non transformées, telles qu'elles arrivent de la source. C'est une convention qui permet de distinguer les différentes couches : raw (brut) → processed (nettoyé) → curated (prêt à l'analyse).

- 3. **Pourquoi organiser les blobs par partitions de date ?**
Les partitions year=/month=/day= permettent de lire uniquement les données d'une période précise sans scanner tout le stockage. C'est crucial pour les performances quand le volume de données devient important (des milliers de fichiers). Les outils comme Spark ou Azure Data Factory exploitent nativement ces partitions.

4. **Pourquoi historiser plutôt qu'écraser ?**
Écraser un fichier détruit l'historique des données. En ajoutant de nouveaux fichiers, on peut rejouer des traitements sur des données passées, auditer les changements, détecter des anomalies dans le temps et respecter des obligations de conformité (RGPD, audit).


5. **Qu'est-ce qu'une connection string et pourquoi ne pas la versionner ?**
Une connection string est une chaîne qui contient l'adresse, le nom du compte et la clé d'accès secrète au Storage Account. La versionner dans Git exposerait publiquement cette clé - n'importe qui pourrait alors lire, modifier ou supprimer toutes vos données. On la stocke dans une variable d'environnement ($env:AZURE_STORAGE_CONNECTION_STRING) ou dans un coffre-fort secrets (Azure Key Vault).

**6. Quel est l’intérêt pédagogique d’Azurite?**

Azurite permet d'apprendre et de pratiquer les concepts Azure Blob Storage sans aucun prérequis financier ni compte cloud. Concrètement :
- Gratuit et sans risque : pas de facturation, pas de ressources cloud consommées, on peut faire autant d'erreurs qu'on veut sans conséquence.
- Travail hors ligne : pas besoin d'internet, l'émulateur tourne entièrement en local dans VS Code.
- Mêmes concepts, même code : le SDK Python et les commandes utilisées avec Azurite sont identiques à ceux utilisés sur Azure réel — le passage en production ne nécessite que de changer la connection string.
- Feedback immédiat : on voit directement dans l'explorateur VS Code les containers et blobs créés, ce qui rend les concepts de stockage très concrets et visuels.
- Idéal en salle de classe : un simple PC suffit, sans dépendre d'un abonnement Azure ou d'une connexion réseau stable.

---
## Livrables attendus
- Capture d'écran du container `raw` dans le portail Azure
- Capture d'écran des blobs dans le container (vue arborescente)
- Script `scripts/upload_blob.py`
- Capture des fichiers historisés (`test.json` et `test_2.json`)
- Réponses aux questions de compréhension

---

## Conclusion
Dans ce TP, vous avez construit un mini Data Lake directement sur Azure. Vous avez appris à :
créer un Storage Account et un container via Azure CLI depuis PowerShell
envoyer des fichiers avec Python et le SDK `azure-storage-blob`
structurer un Data Lake avec des partitions logiques par date
historiser des fichiers sans écraser les données existantes
Vous avez reproduit les concepts fondamentaux d'un stockage cloud DataOps sur une infrastructure Azure réelle.

---

# TP 2 – Blob vers SQL (Azure Blob Storage - SQLite)



---

## Objectif

Lire les fichiers JSON stockés dans Azure Blob Storage (container `raw`), puis charger leur contenu dans une base de données SQL locale **SQLite**.

---

## Architecture

```
Azure Blob Storage        Script Python        SQLite
  └── Container: raw  ──►  load_blob_to_sql  ──►  staging
        └── *.json              .py               stg_blob_files
```

---

## Pré-requis

- Avoir terminé le **TP 1** (container `raw` existant avec des fichiers JSON)
- Être dans le projet `TP-AZURE-BLOB`
- Variable `$env:AZURE_STORAGE_CONNECTION_STRING` définie
- Python fonctionnel

> On garde le même projet que le TP 1 : `TP-AZURE-BLOB`

---

## Étape 1 - Se repositionner dans le projet

```powershell
cd TP-AZURE-BLOB
```
![image](https://hackmd.io/_uploads/r1nwmVsyzg.png)

---

## Étape 2 - Vérifier la variable d'environnement

```powershell
echo $env:AZURE_STORAGE_CONNECTION_STRING
```
![image](https://hackmd.io/_uploads/BJA3X4o1fx.png)


---

## Étape 3 - Créer le dossier database

```powershell
mkdir database
```

Structure du projet après cette étape :

```
TP-AZURE-BLOB/
├── data/
├── scripts/
└── database/
```
![image](https://hackmd.io/_uploads/S1dJNNsJfe.png)

---

## Étape 4 - Créer le script de chargement

```powershell
@'
import os
import json
import sqlite3
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = "raw"
DATABASE_PATH = "database/dataops.db"


def get_connection_string():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise EnvironmentError(
            "Variable AZURE_STORAGE_CONNECTION_STRING manquante."
        )
    return connection_string


def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stg_blob_files (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file  TEXT UNIQUE,
            message      TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Base SQLite prête.")


def load_blobs():
    connection_string = get_connection_string()

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    blobs = container_client.list_blobs()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for blob in blobs:
        blob_name = blob.name
        print(f"Lecture blob : {blob_name}")

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=blob_name
        )

        blob_content = blob_client.download_blob().readall()
        data = json.loads(blob_content)
        message = data.get("message")

        cursor.execute("""
            INSERT OR IGNORE INTO stg_blob_files (source_file, message)
            VALUES (?, ?)
        """, (blob_name, message))

        print(f"Chargé dans SQLite : {blob_name}")

    conn.commit()
    conn.close()
    print("Chargement terminé.")


if __name__ == "__main__":
    create_database()
    load_blobs()
'@ | Out-File -Encoding utf8 scripts/load_blob_to_sql.py
```
![image](https://hackmd.io/_uploads/HJhB4EjJGl.png)
![image](https://hackmd.io/_uploads/S1suENjJGg.png)

---

## Étape 5 - Exécuter le script

```powershell
py scripts/load_blob_to_sql.py
```
![image](https://hackmd.io/_uploads/HJZzH4jJMx.png)
![image](https://hackmd.io/_uploads/HJa_BEj1ze.png)


> Le résultat exact dépend des fichiers présents dans votre container `raw`.

---

## Étape 6 – Vérifier les données dans SQLite

```powershell
python -c "import sqlite3; conn=sqlite3.connect('database/dataops.db'); print(conn.execute('SELECT * FROM stg_blob_files').fetchall()); conn.close()"
```

![image](https://hackmd.io/_uploads/r1ApBViJzx.png)

### À retenir
La base SQLite joue ici le rôle d’une couche staging. Elle contient les données structurées
issues de la zone raw.

---

## Étape 7 – Ouvrir la base dans VS Code

- Installer une extension SQLite (SQLite Viewer) :

![image](https://hackmd.io/_uploads/H1M_8Eikzg.png)
![image](https://hackmd.io/_uploads/BJ_c8EskMe.png)

- Ouvrir le fichier `dataops.db` avec cette extension
Vous devez voir la table : `stg_blob_files`
![image](https://hackmd.io/_uploads/HJ4gDVjkfl.png)

---

## Étape 8 – Tester l'idempotence

Relancer le script une deuxième fois :

```powershell
py scripts/load_blob_to_sql.py
```
![image](https://hackmd.io/_uploads/HytPD4j1Ge.png)

Vérifier que le nombre de lignes n'a pas doublé :

```powershell
py -c "import sqlite3; conn=sqlite3.connect('database/dataops.db'); print(conn.execute('SELECT COUNT(*) FROM stg_blob_files').fetchall()); conn.close()"
```

> **Pourquoi ?** La colonne `source_file` est déclarée `UNIQUE` et l'insertion utilise `INSERT OR IGNORE` : un fichier déjà chargé est silencieusement ignoré. C'est ce qu'on appelle l'**idempotence**.

![image](https://hackmd.io/_uploads/By7yONs1Ge.png)


---

## Étape 9 - Ajouter un nouveau blob et recharger

```powershell
# Nouveau fichier JSON
'{"message": "third upload", "source": "tp2"}' | Out-File -Encoding utf8 data/test.json

# Modifier le nom du blob dans upload_blob.py
(Get-Content scripts/upload_blob.py) `
  -replace 'BLOB_NAME = ".*"', 'BLOB_NAME = "bitcoin/year=2026/month=05/day=10/test_3.json"' `
  | Set-Content scripts/upload_blob.py

# Uploader
py scripts/upload_blob.py

# Recharger vers SQLite
py scripts/load_blob_to_sql.py
```
![image](https://hackmd.io/_uploads/S1Q4dViJGe.png)

Vérifier le résultat final :

```powershell
py -c "import sqlite3; conn=sqlite3.connect('database/dataops.db'); print(conn.execute('SELECT source_file, message FROM stg_blob_files').fetchall()); conn.close()"
```

Vous devez voir plusieurs fichiers chargés depuis Azurite.
![image](https://hackmd.io/_uploads/B16dONoyMl.png)

---

## Erreurs fréquentes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `EnvironmentError: Variable AZURE_STORAGE_CONNECTION_STRING manquante` | Variable non définie | Relancer l'export de la connection string (TP 1 Étape 2) |
| `ResourceNotFoundError` | Container `raw` inexistant | Vérifier que le TP 1 est bien complété |
| `JSONDecodeError` | Fichier blob mal formé | Vérifier le contenu JSON avec `az storage blob download` |
| `sqlite3.OperationalError` | Dossier `database/` inexistant | Relancer `mkdir database` |

---

## Concepts clés

**Raw**
La zone `raw` contient les fichiers originaux dans Azure Blob Storage, tels qu'ils arrivent de la source, sans aucune transformation.

**Staging**
La table `stg_blob_files` contient les données structurées et nettoyées, prêtes à être transformées pour l'analyse.

**Idempotence**
Un pipeline est idempotent si on peut le relancer plusieurs fois sans créer de doublons ni d'effets de bord. C'est une propriété fondamentale des pipelines DataOps fiables.

---

## Questions de compréhension

**1. Pourquoi utilise-t-on une table staging ?**
La table staging est une zone tampon entre les données brutes et les données finales. Elle permet de recevoir les données telles quelles, sans transformation complexe, pour ensuite les valider, nettoyer et enrichir avant de les envoyer vers des tables de production. C'est une étape intermédiaire qui isole les erreurs et facilite le débogage du pipeline.

**2. Pourquoi les blobs restent-ils la source de vérité ?**
Les fichiers JSON dans le Blob Storage sont les données originales, jamais modifiées. Si la base SQLite est corrompue, effacée ou mal chargée, on peut toujours tout reconstruire depuis les blobs. C'est le principe du stockage immuable : la source brute ne doit jamais être altérée par les traitements en aval.

**3. Qu'est-ce que l'idempotence ?**
Un pipeline est idempotent si on peut le relancer autant de fois qu'on veut et obtenir toujours le même résultat, sans créer de doublons ni d'effets de bord. C'est une propriété fondamentale en DataOps : elle garantit qu'un re-chargement accidentel ou planifié ne corrompt pas les données.

**4. Pourquoi utilise-t-on `INSERT OR IGNORE` ?**
`INSERT OR IGNORE` combiné à la contrainte `UNIQUE` sur `source_file` permet d'ignorer silencieusement une insertion si le fichier a déjà été chargé. C'est le mécanisme concret qui implémente l'idempotence : le même blob peut être traité plusieurs fois, seule la première insertion est retenue.

**5. Pourquoi séparer le stockage brut (Blob) et la base SQL ?**
Les deux systèmes n'ont pas le même rôle. Le Blob stocke des fichiers non structurés à bas coût, en grande quantité, avec un historique complet. La base SQL structure les données pour les requêtes et l'analyse. Mélanger les deux créerait un système rigide et difficile à faire évoluer. La séparation permet aussi de changer l'un sans impacter l'autre : par exemple remplacer SQLite par PostgreSQL sans toucher aux blobs.

---

## Conclusion

Dans ce TP, vous avez construit la **deuxième brique du pipeline DataOps** :

```
Azure Blob Storage (raw)  ──►  SQLite (staging)
```

Vous avez appris à :

- lire des fichiers depuis un stockage Blob avec Python
- parser des fichiers JSON
- créer une base SQLite et une table staging
- charger les données **sans doublons** grâce à l'idempotence

Le pipeline ne se contente plus de stocker les fichiers : il commence à **structurer les données pour l'analyse**.

---

# TP 3 : dbt Analytics Engineering





## Pipeline complet du TP 3

```
JSON Files  →  
Azurite Blob (raw container)  →  
SQLite (stg_blob_files)  →  
dbt Models (analytics_messages)
```

Dans ce TP, nous allons construire la couche analytique du pipeline DataOps à l'aide de dbt.

---



## 1. Objectif du TP

Dans ce TP, vous allez :

- installer dbt ;
- connecter dbt à SQLite ;
- créer un modèle analytique ;
- transformer les données SQL ;
- ajouter des tests qualité ;
- générer automatiquement la documentation.

---

## 2. Pré-requis

- avoir terminé le TP 1 ;
- avoir terminé le TP 2 ;
- avoir SQLite fonctionnel ;
- avoir la table `stg_blob_files` ;
- avoir Python 3.11 installé.

> Vérifiez que Python 3.11 est bien disponible avant de commencer :
> ```bash
> py -3.11 --version
> ```

![image](https://hackmd.io/_uploads/ryhqhQVgMl.png)
![image](https://hackmd.io/_uploads/Sy-337NxMe.png)

---

## 3. Étape 1 : Créer un environnement virtuel Python

Depuis le dossier projet :

```bash
cd TP-AZURE-BLOB
```
![image](https://hackmd.io/_uploads/r19W6mVxMe.png)

Créer le venv :

```bash
py -3.11 -m venv .venv
```
![image](https://hackmd.io/_uploads/Byu_6mNxGe.png)

Activer le venv :

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

**Résultat attendu :**

```
(.venv)
```
![image](https://hackmd.io/_uploads/S11WR7Vxfx.png)

> Si PowerShell refuse l'exécution du script, autorisez-le temporairement :
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## 4. Étape 2 – Installer dbt

```bash
python -m pip install --upgrade pip
python -m pip install dbt-core dbt-sqlite
```
![image](https://hackmd.io/_uploads/Syo8AQVxMe.png)

![image](https://hackmd.io/_uploads/BybGkNVeMg.png)

Vérifier :

```bash
dbt --version
```
![image](https://hackmd.io/_uploads/ByPN1EExfx.png)

> Pour figer les versions dans un fichier `requirements.txt` (bonne pratique) :
> ```bash
> pip freeze > requirements.txt
> ```
> Cela permet de réinstaller l'environnement à l'identique plus tard :
> ```bash
> pip install -r requirements.txt
> ```

![image](https://hackmd.io/_uploads/HJ6d14NgGx.png)

---

## 5. Étape 3 : Initialiser le projet dbt

Depuis `TP-AZURE-BLOB` :

```bash
dbt init dataops_dbt
```
![image](https://hackmd.io/_uploads/SyFpJ44ezg.png)

Lorsque dbt demande le type de base :

```
sqlite
```
![image](https://hackmd.io/_uploads/H1fJeVVlfe.png)
![image](https://hackmd.io/_uploads/Hy8gxNVlfe.png)

---

## 6. Étape 4 : Structure du projet

```
TP-AZURE-BLOB/
├── database/
│   └── dataops.db
├── dataops_dbt/
│   ├── models/
│   │   ├── analytics_messages.sql   ← modèle analytique (à créer)
│   │   └── schema.yml               ← tests qualité (à créer)
│   ├── dbt_project.yml
│   ├── packages.yml                 ← (optionnel) packages tiers
│   └── ...
└── requirements.txt                 ← (recommandé)
```
![image](https://hackmd.io/_uploads/ry_qeVVxMx.png)

---

## 7. Étape 5 : Configurer profiles.yml

| OS | Chemin |
|---|---|
| Windows | `C:\Users\<votre_utilisateur>\.dbt\profiles.yml` |
| Mac/Linux | `~/.dbt/profiles.yml` |

> Le fichier `profiles.yml` ne se trouve **pas** dans le projet dbt mais il est global à la machine.

![image](https://hackmd.io/_uploads/Hyw-WE4gfl.png)

Le contenu actuel du fichier :
![image](https://hackmd.io/_uploads/SJmIWEEeMl.png)

Remplacer le contenu par :

```yaml
dataops_dbt:
  target: dev
  outputs:
    dev:
      type: sqlite
      threads: 1
      database: dataops
      schema: main
      schemas_and_paths:
        main: "../database/dataops.db"
      schema_directory: "../database"
```
![image](https://hackmd.io/_uploads/BkYuZN4lMg.png)

### Configuration multi-environnements (optionnel)

En situation réelle, on distingue plusieurs cibles. Exemple :

```yaml
dataops_dbt:
  target: dev           # cible active par défaut
  outputs:

    dev:
      type: sqlite
      threads: 1
      database: dataops
      schema: main
      schemas_and_paths:
        main: "../database/dataops.db"
      schema_directory: "../database"

    prod:
      type: sqlite
      threads: 4
      database: dataops_prod
      schema: main
      schemas_and_paths:
        main: "../database/dataops_prod.db"
      schema_directory: "../database"
```

Pour lancer dbt sur une cible spécifique :

```bash
dbt run --target prod
```

---

## 8. Étape 6 : Tester la connexion dbt

Se placer dans le projet dbt :

```bash
cd dataops_dbt
```
![image](https://hackmd.io/_uploads/r1igzENlze.png)

Puis :

```bash
dbt debug
```

**Résultat attendu :**

```
All checks passed
```
![image](https://hackmd.io/_uploads/BJBmMEVgfx.png)

---

## 9. Étape 7 : Créer le modèle analytique

Créer le fichier : `dataops_dbt/models/analytics_messages.sql`

```powershell
New-Item -Path "models\analytics_messages.sql" -ItemType File
```

![image](https://hackmd.io/_uploads/ry1kQ44eGg.png)
![image](https://hackmd.io/_uploads/HJqNQ4VlMe.png)

```powershell
@"
SELECT
    source_file,
    message
FROM stg_blob_files
WHERE message IS NOT NULL
"@ | Set-Content models\analytics_messages.sql
```
![image](https://hackmd.io/_uploads/SkkuXV4eMl.png)

---

## 10. Étape 8 :  Exécuter les transformations

```powershell
dbt run
```

**Résultat attendu :**

```
Completed successfully
```
![image](https://hackmd.io/_uploads/rJhl4V4eMe.png)

> **Important :** dbt transforme automatiquement les modèles SQL en tables ou vues analytiques.

Commandes utiles :

```bash
# Exécuter un seul modèle
dbt run --select analytics_messages

# Exécuter avec logs détaillés
dbt run --debug

# Exécuter sans recréer les tables existantes (mode full-refresh désactivé)
dbt run --no-full-refresh
```

---

## 11. Étape 9 : Vérifier la table analytique

Revenir à la racine :

```bash
cd ..
```

Puis :

```bash
python -c "import sqlite3; conn=sqlite3.connect('database/dataops.db'); print(conn.execute('SELECT * FROM analytics_messages').fetchall()); conn.close()"
```

**Résultat attendu :**

```python
[
  ('test/test.json', 'hello azurite depuis tp2'),
  ('bitcoin/year=2026/month=05/day=10/test_2.json', 'second upload')
]
```
![image](https://hackmd.io/_uploads/ryC0NNEezl.png)

Afficher les données sous forme de tableau 

```python
python -c "
import sqlite3

conn = sqlite3.connect('database/dataops.db')
rows = conn.execute('SELECT * FROM analytics_messages').fetchall()
conn.close()

# Affichage tableau
headers = ['source_file', 'message']
col_widths = [max(len(h), max((len(str(r[i])) for r in rows), default=0)) for i, h in enumerate(headers)]

sep = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
header_row = '|' + '|'.join(f' {h:<{col_widths[i]}} ' for i, h in enumerate(headers)) + '|'

print(sep)
print(header_row)
print(sep)
for row in rows:
    print('|' + '|'.join(f' {str(row[i]):<{col_widths[i]}} ' for i in range(len(headers))) + '|')
print(sep)
"

```
![image](https://hackmd.io/_uploads/rk3xU4Vxfe.png)

Si tu veux quelque chose d'encore plus propre, installe tabulate dans ton venv 

```powershell
pip install tabulate
```
![image](https://hackmd.io/_uploads/HJ8uIV4lGx.png)

Affichage :

```python
python -c "
import sqlite3
from tabulate import tabulate
conn = sqlite3.connect('database/dataops.db')
rows = conn.execute('SELECT * FROM analytics_messages').fetchall()
conn.close()
print(tabulate(rows, headers=['source_file', 'message'], tablefmt='rounded_outline'))
"
```
![image](https://hackmd.io/_uploads/ry05IV4lzg.png)

---

## 12. Étape 10 – Ajouter les tests dbt

Créer ou modifier : `dataops_dbt/models/schema.yml`

```powershell
@"
version: 2

models:
  - name: analytics_messages
    description: "Couche analytique — messages extraits des fichiers blob."
    columns:
      - name: source_file
        description: "Chemin du fichier source dans le blob storage."
        tests:
          - unique
          - not_null
      - name: message
        description: "Contenu du message extrait du JSON."
        tests:
          - not_null
"@ | Set-Content dataops_dbt\models\schema.yml
```
![image](https://hackmd.io/_uploads/HJOaDVNlMe.png)

> Si dbt a créé un dossier `models/example`, supprimez-le pour éviter que ses tests n'interfèrent :
> ```powershell
> Remove-Item -Recurse -Force dataops_dbt\models\example
> ```

![image](https://hackmd.io/_uploads/HkMZd44lMx.png)


---

## 13. Étape 11 : Exécuter les tests

Depuis `TP-AZURE-BLOB/dataops_dbt` :

![image](https://hackmd.io/_uploads/B15Bu4Ngzg.png)

```bash
dbt test
```

**Résultat attendu :**

```
PASS
```
![image](https://hackmd.io/_uploads/HJtFOE4lfx.png)

Pour tester un seul modèle :

```bash
dbt test --select analytics_messages
```

---

## 14. Étape 12 : Générer la documentation & lanacement du serveur

```bash
dbt docs generate
dbt docs serve
```
![image](https://hackmd.io/_uploads/HJ6YKVEeGl.png)

![image](https://hackmd.io/_uploads/B1T0YEEgMx.png)

Ouvrir dans le navigateur : [http://localhost:8080](http://localhost:8080)

![image](https://hackmd.io/_uploads/HJcfq4EgMx.png)

La documentation affiche :

- les modèles et leurs descriptions ;
- les colonnes et leurs types ;
- les tests associés ;
- les dépendances entre modèles ;
- le **lineage graph** (graphe de dépendance visuel).


---

## 16. Concepts importants

### Staging Layer
`stg_blob_files` contient les données brutes structurées, telles qu'elles arrivent du blob storage. Pas de transformation métier à ce niveau.

### Analytics Layer
`analytics_messages` contient les données nettoyées, filtrées et prêtes pour l'analyse ou la visualisation.

### Matérialisation
Comment dbt stocke le résultat d'un modèle : vue, table, incrémental ou éphémère.

### Data Quality
dbt permet de :
- détecter les valeurs nulles ;
- détecter les doublons ;
- valider les transformations métier ;
- bloquer le pipeline si un test échoue.

### Lineage
dbt construit automatiquement le **graphe de dépendance** entre les modèles. Il est visible dans `dbt docs` sous forme de DAG (Directed Acyclic Graph).

### Jinja & Macros
dbt utilise Jinja (moteur de templates Python) dans les fichiers SQL, ce qui permet d'écrire des requêtes dynamiques et réutilisables via `{{ ref() }}`, `{{ source() }}` et des macros custom.

---

## 17. Dépannage (Troubleshooting)

| Problème | Cause probable | Solution |
|---|---|---|
| `dbt: command not found` | dbt non dans le PATH | Vérifier que le venv est activé |
| `All checks passed` absent | Mauvais chemin dans `profiles.yml` | Vérifier le chemin relatif vers `dataops.db` |
| `Table not found: stg_blob_files` | TP 2 non terminé | Compléter le TP 2 d'abord |
| Tests qui échouent sur `models/example` | Dossier example non supprimé | `Remove-Item -Recurse -Force models\example` |
| `Permission denied` sur `.ps1` | Politique d'exécution PowerShell | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `dbt docs serve` port déjà utilisé | Port 8080 occupé | `dbt docs serve --port 8081` |

---

## 18. Questions de compréhension

### 1. Pourquoi séparer staging et analytics ?

La **staging layer** (`stg_blob_files`) contient les données brutes telles qu'elles arrivent, sans transformation métier. On ne touche pas à leur structure.

La **analytics layer** (`analytics_messages`) applique les règles métier : filtres, nettoyage, colonnes dérivées. 

Cette séparation permet de :
- rejouer uniquement la couche analytics sans retoucher l'ingestion ;
- déboguer facilement (on sait exactement où une erreur est apparue) ;
- avoir une source de vérité stable en staging, réutilisable par plusieurs modèles analytics.

---

### 2. À quoi sert dbt ?

dbt (**data build tool**) est un outil de transformation de données. Il permet d'écrire des transformations SQL sous forme de fichiers versionnés, testés et documentés, comme du vrai code applicatif.

Il prend en charge :
- l'exécution ordonnée des modèles SQL ;
- les tests de qualité des données ;
- la génération automatique de documentation ;
- le calcul du lineage entre les modèles.

> dbt ne déplace pas de données - il **transforme** ce qui est déjà dans la base.

---

### 3. Pourquoi ajouter des tests ?

Sans tests, une transformation cassée passe inaperçue et pollue silencieusement les analyses en aval. Les tests dbt permettent de :
- garantir qu'aucune valeur nulle n'existe là où ce n'est pas attendu ;
- détecter les doublons sur des colonnes censées être uniques ;
- bloquer le pipeline automatiquement si une règle est violée.

C'est l'équivalent des **tests unitaires** en développement logiciel, appliqués aux données.

---

### 4. Qu'est-ce qu'un modèle dbt ?

Un modèle dbt est simplement un **fichier `.sql`** contenant un `SELECT`. dbt se charge de le transformer en vue ou en table dans la base de données selon la matérialisation choisie.

```sql
-- models/analytics_messages.sql
SELECT source_file, message
FROM stg_blob_files
WHERE message IS NOT NULL
```

Chaque fichier = un modèle = une table ou vue en base. C'est l'unité de base du pipeline dbt.

---

### 5. Qu'est-ce que le lineage ?

Le lineage est le **graphe de dépendance** entre toutes les tables et modèles du pipeline. Il répond à la question : *d'où viennent ces données, et qui en dépend ?*

Dans notre TP :

```
stg_blob_files  →  analytics_messages
```

dbt construit ce graphe automatiquement et le visualise dans `dbt docs` sous forme de DAG (Directed Acyclic Graph). C'est essentiel pour comprendre l'impact d'une modification en amont.

---

### 6. Différence entre `view` et `table`

| | `view` | `table` |
|---|---|---|
| **Stockage** | Aucun - recalculée à chaque requête | Données physiquement stockées en base |
| **Performance** | Lente si la source est volumineuse | Rapide à la lecture |
| **Fraîcheur** | Toujours à jour | Mise à jour uniquement au prochain `dbt run` |
| **Usage conseillé** | Données légères, exploration | Données volumineuses, consultées souvent |

Dans ce TP on utilise la vue (défaut), ce qui est suffisant pour SQLite avec peu de données.

---

### 7. Rôle de `{{ source() }}` et `{{ ref() }}`

Ces deux fonctions Jinja sont le cœur du système de dépendances de dbt.

**`{{ source('schema', 'table') }}`** - pointe vers une table **brute** existante, non gérée par dbt (ici `stg_blob_files` chargée par le TP 2) :

```sql
SELECT * FROM {{ source('main', 'stg_blob_files') }}
```

**`{{ ref('nom_modele') }}`** - pointe vers un **autre modèle dbt** du projet :

```sql
SELECT * FROM {{ ref('analytics_messages') }}
```

L'avantage : dbt résout automatiquement l'ordre d'exécution et construit le lineage. Si on écrit le nom de table en dur, dbt ne sait pas qu'il existe une dépendance.

---

## 19. Livrables attendus

- projet dbt fonctionnel (`dbt debug` → All checks passed) ;
- modèle SQL `analytics_messages.sql` ;
- fichier `schema.yml` avec tests configurés ;
- capture d'écran `dbt docs` (lineage visible) ;
- preuve des tests PASS (`dbt test`) ;
- réponses aux questions de compréhension.

---

## Conclusion

Dans ce TP, vous avez construit une vraie couche Analytics Engineering avec dbt.

Vous avez appris à :

- créer des modèles analytiques ;
- transformer les données SQL ;
- tester automatiquement les données ;
- documenter les pipelines ;
- construire un lineage analytique.

> **Le pipeline DataOps ne se contente plus de stocker les données : il produit maintenant une couche analytique industrialisée.**

