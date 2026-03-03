$b = [IO.File]::ReadAllBytes('d:\label\label_maker_2_5.exe')
'path d:\label\label_maker_2_5.exe'
"size $($b.Length)"
"first20 $([BitConverter]::ToString($b[0..19]))"
$tailStart = $b.Length - 20
"tail20 $([BitConverter]::ToString($b[$tailStart..($b.Length-1)]))"
$enc = [Text.Encoding]::ASCII
foreach($sig in 'MEI','pyi','PYZ') {
    $bytes = $enc.GetBytes($sig)
    $idx = [Array]::LastIndexOf($b, $bytes[-1])
    "$sig last-byte index $idx"
}
