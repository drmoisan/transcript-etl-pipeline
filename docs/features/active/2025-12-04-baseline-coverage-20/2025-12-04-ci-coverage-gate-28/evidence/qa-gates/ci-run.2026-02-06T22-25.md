Timestamp: 2026-02-06T22-25
Command: gh run watch --exit-status --workflow ci.yml --branch remediation/ci-coverage-fail-2026-02-06
EXIT_CODE: 1

Output:
~~~
unknown flag: --workflow
System.Management.Automation.RemoteException
Usage:  gh run watch <run-id> [flags]
System.Management.Automation.RemoteException
Flags:
      --compact        Show only relevant/failed steps
      --exit-status    Exit with non-zero status if run fails
  -i, --interval int   Refresh interval in seconds (default 3)
  
~~~

