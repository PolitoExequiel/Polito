param([Parameter(Mandatory=$true)][string]$TicketFile,[Parameter(Mandatory=$true)][string]$PrinterName)
Add-Type -AssemblyName System.Drawing
$lines = [System.IO.File]::ReadAllLines($TicketFile,[System.Text.Encoding]::UTF8)
$doc = New-Object System.Drawing.Printing.PrintDocument
$doc.PrinterSettings.PrinterName = $PrinterName
if (-not $doc.PrinterSettings.IsValid) { throw "Impresora no encontrada: $PrinterName" }
$doc.PrintController = New-Object System.Drawing.Printing.StandardPrintController
# 58 mm = 228 hundredths of an inch. Height grows with content.
$h = [Math]::Max(400, [Math]::Min(1200, ($lines.Count * 20 + 90)))
$doc.DefaultPageSettings.PaperSize = New-Object System.Drawing.Printing.PaperSize('Ticket58',228,$h)
$doc.DefaultPageSettings.Margins = New-Object System.Drawing.Printing.Margins(8,8,8,8)
$doc.add_PrintPage({
  param($sender,$e)
  $font = New-Object System.Drawing.Font('Consolas',9,[System.Drawing.FontStyle]::Regular)
  $fontBold = New-Object System.Drawing.Font('Consolas',10,[System.Drawing.FontStyle]::Bold)
  $brush = [System.Drawing.Brushes]::Black
  $y = 10.0
  foreach ($line in $lines) {
    $useFont = if ($line.StartsWith('TOTAL:') -or $line -eq 'EGRESO DE CAJA') { $fontBold } else { $font }
    $e.Graphics.DrawString($line,$useFont,$brush,8,$y)
    $y += 19
  }
  $e.HasMorePages = $false
  $font.Dispose(); $fontBold.Dispose()
})
try { $doc.Print() } finally { $doc.Dispose() }
