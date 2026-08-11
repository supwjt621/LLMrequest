# Save this file as server.ps1
$HttpListener = New-Object System.Net.HttpListener
$HttpListener.Prefixes.Add("http://localhost:5000/")
$HttpListener.Start()

# Set your API Key
$TyphoonApiKey = "sk-MJsRMwZQ1NCysKccWjbc968HJPxvoA7ijcXTvMG3X27vXy0S"

Write-Host "Windows Backend Running!"
Write-Host "👉 Open your browser and go to: http://localhost:5000"

while ($HttpListener.IsListening) {
    $Context = $HttpListener.GetContext()
    $Request = $Context.Request
    $Response = $Context.Response

    # 1. SERVE THE HTML PAGE (When you visit http://localhost:5000 in the browser)
    if ($Request.HttpMethod -eq "GET" -and ($Request.RawUrl -eq "/" -or $Request.RawUrl -eq "/locallm.html")) {
        $HtmlPath = Join-Path $PSScriptRoot "locallm.html"
        if (Test-Path $HtmlPath) {
            $HtmlContent = [System.IO.File]::ReadAllBytes($HtmlPath)
            $Response.ContentType = "text/html; charset=utf-8"
            $Response.ContentLength64 = $HtmlContent.Length
            $Response.OutputStream.Write($HtmlContent, 0, $HtmlContent.Length)
        } else {
            $Response.StatusCode = 404
        }
    }
    # 2. HANDLE THE AI API CALL (When your HTML page fetches /api/chat)
    elseif ($Request.HttpMethod -eq "POST" -and $Request.RawUrl -eq "/api/chat") {
        $Reader = New-Object System.IO.StreamReader($Request.InputStream, [System.Text.Encoding]::UTF8)
        $RequestBody = $Reader.ReadToEnd()
            
            $Headers = @{
                "Authorization" = "Bearer $TyphoonApiKey"
                "Content-Type"  = "application/json"
            }
            
        # FIX 1: Corrected Endpoint Path
        $TyphoonUrl = "https://api.opentyphoon.ai/v1/chat/completions"
        
        try {
            $TyphoonResponse = Invoke-RestMethod -Uri $TyphoonUrl -Method Post -Headers $Headers -Body $RequestBody
            $ResponseString = $TyphoonResponse | ConvertTo-Json -Depth 10
            $Buffer = [System.Text.Encoding]::UTF8.GetBytes($ResponseString)
            
            $Response.ContentType = "application/json"
            $Response.ContentLength64 = $Buffer.Length
            $Response.OutputStream.Write($Buffer, 0, $Buffer.Length)
        } catch {
            # FIX 2: Send the actual error message details back to the browser instead of {}
            $ErrorMessage = $_.Exception.Message
            if ($_.Exception.Response) {
                $Reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                $ErrorMessage = $Reader.ReadToEnd()
            }
            
            $ErrorJson = @{ error = "Backend Failed"; details = $ErrorMessage } | ConvertTo-Json
            $Buffer = [System.Text.Encoding]::UTF8.GetBytes($ErrorJson)
            
            $Response.StatusCode = 500
            $Response.ContentType = "application/json"
            $Response.ContentLength64 = $Buffer.Length
            $Response.OutputStream.Write($Buffer, 0, $Buffer.Length)
        }
    }
    else {
        $Response.StatusCode = 404
    }
    $Response.Close()
}