param([string]$Path)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$paperWord = $null
$paperDoc = $null
try {
    $paperWord = New-Object -ComObject Word.Application
    $paperWord.Visible = $false
    $paperWord.DisplayAlerts = 0
    $paperDoc = $paperWord.Documents.Open([IO.Path]::GetFullPath($Path), $false, $true)
    foreach ($paragraph in $paperDoc.Paragraphs) {
        $styleName = [string]$paragraph.Range.Style
        if ($paragraph.OutlineLevel -lt 10 -or $paragraph.Range.ListFormat.ListString) {
            Write-Output ($styleName + ' | ' + $paragraph.Range.ListFormat.ListString + ' | ' + $paragraph.Range.Text.Trim())
        }
    }
    Write-Output ('Pages: ' + $paperDoc.ComputeStatistics(2))
} finally {
    if ($paperDoc) { $paperDoc.Close($false); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($paperDoc) }
    if ($paperWord) { $paperWord.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($paperWord) }
}
