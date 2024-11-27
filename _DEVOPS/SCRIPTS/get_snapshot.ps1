# PowerShell script to get a snapshot (get_snapshot.ps1)

# to run the script, use the following command:
# .\_DEVOPS\SCRIPTS\get_snapshot.ps1 "[LOCAL_PATH_TO_REPO]" "[DIR]" "[NAME]_snapshot"
# Example: # .\_DEVOPS\SCRIPTS\get_snapshot.ps1 "C:\files\repo" "frontend" "frontend_snapshot"
param (
    [Parameter(Mandatory=$true)]
    [string]$RepoPath,
    [Parameter(Mandatory=$true)]
    [string]$FolderName,
    [Parameter(Mandatory=$true)]
    [string]$SnapshotName
)

# Function to find the root directory
function Find-RootDirectory {
    param ([string]$StartPath)
    $currentPath = (Resolve-Path $StartPath).Path
    while ($currentPath -ne $currentPath.Root) {
        if (Test-Path "$currentPath\.git") {
            return $currentPath
        }
        $currentPath = Split-Path $currentPath -Parent
    }
    throw "Root directory not found. Make sure you're providing a path within a Git repository."
}

# Find the root directory
$rootDir = Find-RootDirectory $RepoPath

# Define paths
$folderPath = (Resolve-Path "$rootDir\$FolderName").Path
$outputDir = "$rootDir\_DEVOPS\SCRIPTS\snapshot"

# Ensure the output directory exists
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Generate the snapshot filename
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$snapshotFile = "$outputDir\${SnapshotName}_${timestamp}.snapshot.txt"

# File extensions to include in the search
$FileExtensions = @(
    "js", "py", "sh", "vue", "ts", "tsx", "scss", 
    "html", "css", "json", "md", "yml", "yaml", "txt",
    "gitignore", "env", "config", "sql",
    "jsx", "ini", "toml", "xml"
)

# Files and folders to ignore
$IgnoreFiles = @("package-lock.json")
$IgnoreFolders = @(
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".git",
    "__pycache__",
    ".pytest_cache",
    "coverage"
)

# Function to generate ignore patterns
function Get-IgnorePatterns {
    param ([string]$BasePath)
    $GitignorePath = "$BasePath\.gitignore"
    $Patterns = @()
    if (Test-Path $GitignorePath) {
        Get-Content $GitignorePath | ForEach-Object {
            $line = $_.Trim()
            if ($line -and -not $line.StartsWith("#")) {
                $Patterns += [regex]::Escape($line.TrimEnd('/'))
            }
        }
    }
    return $Patterns
}

# Function to get relative path
function Get-RelativePath {
    param (
        [string]$BasePath,
        [string]$FullPath
    )
    if ($FullPath.StartsWith($BasePath)) {
        return $FullPath.Substring($BasePath.Length).TrimStart('\', '/')
    }
    return $FullPath
}

# Function to collect text from files
function Get-TextFromFiles {
    param (
        [string]$BasePath,
        [string[]]$Extensions,
        [string[]]$IgnorePatterns,
        [string[]]$IgnoreFiles,
        [string[]]$IgnoreFolders
    )
    $CollectedText = ""
    $FileCount = 0
    Write-Host "Collecting text from files..."
    
    # Get all files recursively
    $Files = Get-ChildItem -Path $BasePath -Recurse -File | ForEach-Object {
        $file = $_
        $shouldInclude = $true

        # Get the relative path
        $relativePath = Get-RelativePath -BasePath $BasePath -FullPath $file.FullName
        
        # Check file extension
        $shouldInclude = $shouldInclude -and ($_.Extension -in ($Extensions | ForEach-Object { ".$_" }))
        
        # Check if file is in ignore list
        $shouldInclude = $shouldInclude -and ($_.Name -notin $IgnoreFiles)
        
        # Check if file is in any ignored folder
        $pathParts = $relativePath.Split([IO.Path]::DirectorySeparatorChar)
        $shouldInclude = $shouldInclude -and -not ($IgnoreFolders | Where-Object { $pathParts -contains $_ })
        
        # Check against gitignore patterns
        $shouldInclude = $shouldInclude -and ($IgnorePatterns.Count -eq 0 -or -not ($IgnorePatterns | Where-Object { $relativePath -match $_ }))
        
        if ($shouldInclude) {
            $_
        }
    }

    foreach ($File in $Files) {
        $RelativePath = Get-RelativePath -BasePath $BasePath -FullPath $File.FullName
        Write-Host "Processing file: $RelativePath"
        $CollectedText += "`n--- Text from file: $RelativePath ---`n"
        try {
            $Content = Get-Content $File.FullName -Raw -ErrorAction Stop
            if ($null -ne $Content) {
                $CollectedText += $Content
            }
        }
        catch {
            Write-Host "Error reading file $($File.FullName): $_" -ForegroundColor Red
        }
        $FileCount++
    }

    Write-Host "Text collection complete."
    Write-Host "Total files processed: $FileCount"
    return $CollectedText
}

Write-Host "Starting text collection..."
$CollectedText = ""
$IgnorePatterns = Get-IgnorePatterns $rootDir
$CollectedText = Get-TextFromFiles -BasePath $folderPath -Extensions $FileExtensions -IgnorePatterns $IgnorePatterns -IgnoreFiles $IgnoreFiles -IgnoreFolders $IgnoreFolders

# Write the collected text to the file
$CollectedText | Out-File $snapshotFile -Encoding utf8

Write-Host "`nSnapshot complete.`n"
Write-Host "Snapshot saved to: $snapshotFile"