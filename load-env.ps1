# Script pour charger les variables d'environnement, installer les dépendances et démarrer azurite
# Utilisation: .\load-env.ps1

$envFile = Join-Path $PSScriptRoot ".env"

# 1. Charger les variables d'environnement depuis .env
Write-Host "=== Chargement des variables d'environnement ===" -ForegroundColor Cyan
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            Write-Host "✓ Chargé: $key = $value" -ForegroundColor Green
        }
    }
} else {
    Write-Host "✗ Fichier .env non trouvé à $envFile" -ForegroundColor Red
    exit 1
}

# 2. Vérifier la variable d'environnement
Write-Host "`n=== Vérification des variables d'environnement ===" -ForegroundColor Cyan
$connectionString = $env:AZURE_STORAGE_CONNECTION_STRING
if ($connectionString) {
    Write-Host "✓ AZURE_STORAGE_CONNECTION_STRING configurée" -ForegroundColor Green
    Write-Host "  Valeur: $connectionString"
} else {
    Write-Host "✗ AZURE_STORAGE_CONNECTION_STRING non définie" -ForegroundColor Red
    exit 1
}

# 3. Installer azure-storage-blob si nécessaire
Write-Host "`n=== Installation des dépendances ===" -ForegroundColor Cyan
try {
    python -m pip show azure-storage-blob | Out-Null
    Write-Host "✓ azure-storage-blob est déjà installé" -ForegroundColor Green
} catch {
    Write-Host "Installation de azure-storage-blob..." -ForegroundColor Yellow
    python -m pip install azure-storage-blob
    if ($?) {
        Write-Host "✓ azure-storage-blob installé avec succès" -ForegroundColor Green
    } else {
        Write-Host "✗ Erreur lors de l'installation de azure-storage-blob" -ForegroundColor Red
        exit 1
    }
}

# 4. Démarrer azurite
Write-Host "`n=== Démarrage d'Azurite ===" -ForegroundColor Cyan
Write-Host "Azurite démarre avec UseDevelopmentStorage=true" -ForegroundColor Yellow
azurite --skipApiVersionCheck
