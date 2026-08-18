rule Suspicious_Strings
{
    meta:
        description = "Common suspicious API strings (heuristic aid)"
        severity = "low"
    strings:
        $a = "VirtualAlloc" ascii
        $b = "WriteProcessMemory" ascii
        $c = "CreateRemoteThread" ascii
    condition:
        2 of them
}
