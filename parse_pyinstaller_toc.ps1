function Read-BEInt32($bytes, $offset){
    $slice = $bytes[$offset..($offset+3)]
    if([BitConverter]::IsLittleEndian){ [Array]::Reverse($slice) }
    return [BitConverter]::ToInt32($slice,0)
}
function Read-BEUInt32($bytes, $offset){
    $slice = $bytes[$offset..($offset+3)]
    if([BitConverter]::IsLittleEndian){ [Array]::Reverse($slice) }
    return [BitConverter]::ToUInt32($slice,0)
}
$path = 'd:\label\label_maker_2_5.exe'
$MAGIC = [byte[]](0x4d,0x45,0x49,0x0c,0x0b,0x0a,0x0b,0x0e)
$cookieSize = 24 + 64 # PyInstaller 2.1+
$fs = [IO.File]::OpenRead($path)
$bytes = New-Object byte[] $fs.Length
$fs.Read($bytes,0,$bytes.Length) | Out-Null
$fs.Close()
# find magic from end
$cookiePos = -1
for($i=$bytes.Length-$MAGIC.Length; $i -ge 0; $i--){
    $match = $true
    for($j=0; $j -lt $MAGIC.Length; $j++){
        if($bytes[$i+$j] -ne $MAGIC[$j]){ $match=$false; break }
    }
    if($match){ $cookiePos=$i; break }
}
if($cookiePos -lt 0){ Write-Error 'magic not found'; exit 1 }
# parse cookie for 2.1+
$cursor = $cookiePos
$magic = $bytes[$cursor..($cursor+7)]; $cursor+=8
$lenPkg = Read-BEUInt32 $bytes $cursor; $cursor+=4
$tocOff = Read-BEUInt32 $bytes $cursor; $cursor+=4
$tocLen = Read-BEUInt32 $bytes $cursor; $cursor+=4
$pyver = Read-BEInt32 $bytes $cursor; $cursor+=4
$pylibnameBytes = $bytes[$cursor..($cursor+63)]; $cursor+=64
$pymaj = [int]($pyver/100)
$pymin = [int]($pyver%100)
$tailBytes = $bytes.Length - $cookiePos - $cookieSize
$overlaySize = $lenPkg + $tailBytes
$overlayPos = $bytes.Length - $overlaySize
$tocPos = $overlayPos + $tocOff
Write-Output "PyVer $pymaj.$pymin"
Write-Output "pkgLen $lenPkg tocOff $tocOff tocLen $tocLen"
Write-Output "overlayPos $overlayPos tocPos $tocPos cookiePos $cookiePos"
# parse TOC
$entries = @()
$parsed = 0
$cursor = $tocPos
while($parsed -lt $tocLen){
    $entrySize = Read-BEInt32 $bytes $cursor; $cursor+=4
    $entryData = $bytes[$cursor..($cursor+$entrySize-5)]
    $cursor += ($entrySize - 4)
    $parsed += $entrySize
    $off=0
    $entryPos = Read-BEUInt32 $entryData $off; $off+=4
    $cmprsd = Read-BEUInt32 $entryData $off; $off+=4
    $uncmprsd = Read-BEUInt32 $entryData $off; $off+=4
    $cmprsFlag = $entryData[$off]; $off+=1
    $type = [char]$entryData[$off]; $off+=1
    $nameBytes = $entryData[$off..($entryData.Length-1)]
    $name = ([Text.Encoding]::UTF8.GetString($nameBytes)).Trim([char]0)
    $entries += [pscustomobject]@{
        Name=$name; Type=$type; Compressed=$cmprsd; Uncompressed=$uncmprsd; Flag=$cmprsFlag; Pos=$entryPos
    }
}
Write-Output "entries $($entries.Count)"
# show potential entry points (Type 's' indicates PYSOURCE)
$entries | Where-Object { $_.Type -eq 's' } | Select-Object -First 20 | ForEach-Object { "PYSOURCE: $($_.Name)" }
# show modules/packages (m/M) top sample
$entries | Where-Object { $_.Type -in @('m','M') } | Select-Object -First 20 | ForEach-Object { "MOD: $($_.Name)" }
# write summary list to file
$entries | Select-Object Name,Type | Out-File 'd:\label\toc_list.txt' -Encoding utf8
