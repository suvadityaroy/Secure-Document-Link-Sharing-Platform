$sha = (git rev-parse --short HEAD)
$backup = "backup-old-history-$sha"
Write-Output "Backing up current main to $backup"
git fetch origin
# create backup branch on remote pointing at origin/main
git branch $backup origin/main
git push origin $backup
# create orphan branch, commit current working tree as single commit
git checkout --orphan temp-main
git add -A
git commit -m 'Initial commit: fresh history'
# force-push temp-main to origin/main
git push -f origin temp-main:main
# return to main and delete temp branch locally
git checkout main
git branch -D temp-main
git fetch origin
Write-Output "Done. Remote main ref:"
git ls-remote --heads origin main
