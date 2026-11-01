    [CmdletBinding()]
    param(
        [string]$SshTarget = $env:LUDUS_SSH_TARGET,
        [string]$RemoteRepoPath = $env:LUDUS_REMOTE_REPO,
        [string]$RemoteOutputPath = '~/ludus-artifacts/training-batches',
        [ValidateSet('run', 'preflight', 'plan')]
        [string]$Mode = 'run',
        [ValidateSet('training', 'validation')]
        [string]$PipelineMode = 'training',
        [ValidateRange(1, 2147483647)]
        [int]$ValidationFitRows = 50000,
        [ValidateRange(1, 2147483647)]
        [int]$ValidationEvalRows = 1000,
        [int]$PollSeconds = 30
    )

    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if ([string]::IsNullOrWhiteSpace($SshTarget)) {
        throw 'Set LUDUS_SSH_TARGET to an SSH alias or user@host; credentials stay in your SSH agent/config.'
    }
    if ([string]::IsNullOrWhiteSpace($RemoteRepoPath)) {
        throw 'Set LUDUS_REMOTE_REPO to the checkout path containing this repository on the remote machine.'
    }
    if ($SshTarget -notmatch '^[A-Za-z0-9_.@:-]+$') {
        throw 'SSH target contains unsupported characters; use an SSH config alias or user@host.'
    }
    foreach ($path in @($RemoteRepoPath, $RemoteOutputPath)) {
        if ($path -notmatch '^[A-Za-z0-9_./~\-]+$') {
            throw 'Remote paths may contain only letters, digits, underscore, dot, slash, tilde, and hyphen.'
        }
    }

    $remoteArgs = @('--repo-root', $RemoteRepoPath, '--output-dir', $RemoteOutputPath, '--poll-seconds', "$PollSeconds")
    $remoteArgs += @('--pipeline-mode', $PipelineMode, '--validation-fit-rows', "$ValidationFitRows", '--validation-eval-rows', "$ValidationEvalRows")
    if ($Mode -eq 'preflight') { $remoteArgs += '--preflight-only' }
    if ($Mode -eq 'plan') { $remoteArgs += '--plan-only' }
    $quotedArgs = ($remoteArgs | ForEach-Object { "'$_'" }) -join ' '
    $remoteCommand = "cd '$RemoteRepoPath' && python3 -m Backend.training_pipeline.run_batch $quotedArgs"

    $ssh = Get-Command ssh -ErrorAction Stop
    & $ssh.Source -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes $SshTarget $remoteCommand
    if ($LASTEXITCODE -ne 0) {
        if ($LASTEXITCODE -eq 255) {
            throw "SSH connection failed for '$SshTarget'. Check the configured username, key, agent, and known host."
        }
        exit $LASTEXITCODE
    }
