
# WARNING: all functions act locally, i.e. the working directory and its child .git repository will be edited!
# WARNING: also, these functions were quickly botched together, so no warrantees.

# Returns all folder names where there some assignments were handed in with the given number.
# -> ARGS: $number = assignment number
function Get-Submissions([uint]$number) {
    # Helper function to extract the immediate child name within the WD.
    function Get-WdChild([string]$absolutePath) {
        return $absolutePath.Split($PWD, 2)[1].Split("\", 3)[1]
    }

    Get-ChildItem . -Recurse -Depth 2 -Include "*$number*" |
    Where-Object {
        (Get-Item $_) -IsNot [System.IO.DirectoryInfo] -Or $null -NE (Get-ChildItem $_) 
    } |
    ForEach-Object { Write-Output $(Get-WdChild($_)) } |
    Get-Unique
}

# Retrieves all point headers per assignment OR total points of students in /feedback/*.
# -> ARGS: $number = either assignment number or the keyword "total"
function Get-Points([string]$keyword) {
    if ("$keyword" -EQ "total") {
        foreach ($dir in $(Get-ChildItem -Directory)) {
            Set-Location $dir
            $sum=0.0
            Select-String -Path "feedback/assignment*.txt" -Pattern "\[\d{1,2}(\.[05])?/10\]" -Raw |
            ForEach-Object {
                $sum+=[double]"$_".Substring(1).Split("/")[0]
            }
            Write-Output "$($dir.BaseName): $sum"
            Set-Location ..
        }
    }
    elseif ("$keyword" -Match "^\d{1,2}$") {
        $num=$("{0:00}" -f [int]$keyword)
        Select-String -Path "*/feedback/assignment$num.txt" -Pattern "\[\d{1,2}(\.[05])?/10\]" |
        ForEach-Object {
            $arr="$_".Split($PWD, 2)[1].Split(":")
            Write-Output "$($arr[0].Split("\", 3)[1]): $($arr[2])" 
        }
    }
}
