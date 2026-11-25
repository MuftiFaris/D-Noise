param([string]$InputPath,[string]$OutputPath)
$ErrorActionPreference='Stop'; $word=$null; $doc=$null
try { $word=New-Object -ComObject Word.Application; $word.Visible=$false; $word.DisplayAlerts=0; $doc=$word.Documents.Open($InputPath,$false,$true); $doc.ExportAsFixedFormat($OutputPath,17); $doc.Close(0); $doc=$null; $word.Quit(); $word=$null; Write-Output 'PDF export completed.' } finally { if($doc){$doc.Close(0)}; if($word){$word.Quit()} }
