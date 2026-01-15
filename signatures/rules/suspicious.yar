rule Double_Extension {
    meta:
        description = "Detects files with double extensions"
        author = "HEX-AVG Team"
        severity = "medium"
    condition:
        filename matches /\.(exe|dll|bat|cmd|vbs|js|ps1|scr|pif)\.(exe|dll|bat|cmd|vbs|js|ps1|scr|pif)$/i
}

rule Hidden_Executable {
    meta:
        description = "Detects executables with hidden attribute"
        author = "HEX-AVG Team"
        severity = "medium"
    condition:
        filename matches /^\./ and
        filename matches /\.(exe|dll|bat|cmd|vbs|js|ps1|scr|pif)$/i
}

rule Tiny_Executable {
    meta:
        description = "Detects unusually small executables"
        author = "HEX-AVG Team"
        severity = "high"
    condition:
        uint16(0) == 0x5A4D and  // MZ header
        filesize < 1024
}

rule Large_Executable {
    meta:
        description = "Detects unusually large executables"
        author = "HEX-AVG Team"
        severity = "medium"
    condition:
        uint16(0) == 0x5A4D and  // MZ header
        filesize > 100MB
}

rule Suspicious_URL {
    meta:
        description = "Detects suspicious URLs in files"
        author = "HEX-AVG Team"
        severity = "medium"
    strings:
        $url1 = /https?:\/\/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\// nocase
        $url2 = /https?:\/\/.*\.tk\// nocase
        $url3 = /https?:\/\/.*\.xyz\// nocase
    condition:
        any of them
}

rule Registry_Modification {
    meta:
        description = "Detects registry modification attempts"
        author = "HEX-AVG Team"
        severity = "high"
    strings:
        $reg1 = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" nocase
        $reg2 = "RegAdd" nocase
        $reg3 = "SetValue" nocase
    condition:
        $reg1 and ($reg2 or $reg3)
}

rule Process_Injection {
    meta:
        description = "Detects process injection patterns"
        author = "HEX-AVG Team"
        severity = "high"
    strings:
        $inj1 = "VirtualAlloc" nocase
        $inj2 = "WriteProcessMemory" nocase
        $inj3 = "CreateRemoteThread" nocase
    condition:
        all of them
}