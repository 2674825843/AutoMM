param([string]$Docx, [string]$Pdf)
$ErrorActionPreference = "Stop"
$word = $null
$document = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $document = $word.Documents.Open([System.IO.Path]::GetFullPath($Docx), $false, $true)
  $document.ExportAsFixedFormat([System.IO.Path]::GetFullPath($Pdf), 17)
} finally {
  if ($null -ne $document) { $document.Close($false); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document) }
  if ($null -ne $word) { $word.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) }
  [GC]::Collect()
  [GC]::WaitForPendingFinalizers()
}
