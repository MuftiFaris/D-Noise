param([string]$InputPath,[string]$OutputPath)
$w=$null
try {$w=New-Object -ComObject Word.Application; $w.Visible=$false; Write-Output 'WORD_OK'} finally {if($w){$w.Quit()}}
