
# WARNING: all functions act locally, i.e. the working directory and its child .git repository will be edited!

# Initializes all .git repositories from a list of names, given by an input file.
# Also creates the needed folders "concatenated" and "feedback" for correction.
# -> ARGS: $studentsListPath = path of students list file
function Init-All([string]$studentsListPath) {
    $GIT_HOST="https://blabla.com/group"

    if ("$studentsListPath" -ne "") {
        foreach ($name in $(Get-Content $studentsListPath)) {
            git clone "$GIT_HOST/$name.git"
            Set-Location $name
            mkdir "feedback"
            Set-Location ..
        }
        Write-Output "-- DONE INITIALIZING ALL GIT DIRECTORIES --"
    }
}

# Pulls all child .git directories at once. Not recovering from restart. Not recovering from restart.
# -> ARGS: NONE
function Pull-All() {
    foreach ($dir in $(Get-ChildItem -Directory)) {
        Set-Location $dir
        if (Test-Path -Path ".\.git") {
            Write-Output "Pulling changes from $dir..."
            git pull 2>$null
        }
        Set-Location ..
    }
    Write-Output "-- DONE PULLING ALL GIT DIRECTORIES --"
}

# Adds and commits changes at a given path within the child .git directories.
# -> ARGS: $targetPath = folder to be added, $message = the commit message
function Commit-All([string]$targetPath, [string]$message) {
    foreach ($dir in $(Get-ChildItem -Directory)) {
        Set-Location $dir
        if (Test-Path -Path ".\.git") {
            git add $targetPath && git commit -m "$message"
        }
        Set-Location ..
    }
    Write-Output "-- DONE COMMITTING CHANGES IN ALL GIT DIRECTORIES --"
}

# Pushes all child .git directories at once. Not recovering from restart.
# -> ARGS: NONE
function Push-All() {
    foreach ($dir in $(Get-ChildItem -Directory)) {
        Set-Location $dir
        if (Test-Path -Path ".\.git") {
            git push -u origin
        }
        Set-Location ..
    }
    Write-Output "-- DONE PUSHING ALL GIT DIRECTORIES --"
}
